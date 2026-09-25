"""Post-collection arithmetic/integrity checks; no simulator or frozen analyzer imports.

This author-provided verifier is not independent external replication. Requires SciPy.
"""
from pathlib import Path
from math import fsum, sqrt, isclose
from collections import Counter
import argparse
import hashlib
import json
import zipfile
from scipy.stats import t, beta

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results/gva1-confirmation-v0.1'
REPAIRS = ('original', 'report_repair', 'contract_repair', 'both')
REGIMES = ('NOMINAL', 'PHYSICAL_SHIFT')
ROOTS = range(4000001, 4000146)
ALPHA = .05 / 18

def require(value, message):
    if not value:
        raise ValueError(message)

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def close(actual, expected, label):
    require(isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), label)

def verify(folder, archive=None):
    receipt, run = load(folder / 'COMPLETED.json'), load(folder / 'RUN.json')
    rows, result, costs = (load(folder / name) for name in ('metrics.json', 'result.json', 'costs.json'))
    freeze_path = ROOT / 'gva1-execution-v0.1/FREEZE.json'
    freeze = load(freeze_path)
    require(run['execution_freeze_sha256'] == sha(freeze_path), 'Wrong execution seal')
    require(run['source_hash'] == freeze['source_hash'] and run['runtime'] == freeze['runtime'], 'Run source/runtime mismatch')
    require(run['design'] == freeze['design'], 'Run design mismatch')
    identity_fields = {k: run[k] for k in ('design', 'source_hash', 'runtime', 'execution_freeze_sha256')}
    require(run['identity'] == receipt['run_identity'] == digest(identity_fields), 'Run identity mismatch')
    require(digest(freeze['files']) == freeze['source_hash'], 'Source aggregate mismatch')
    for name, expected in freeze['files'].items():
        require(sha(ROOT / name) == expected, 'Frozen file changed: ' + name)
    for name in ('metrics', 'result', 'costs'):
        require(sha(folder / (name + '.json')) == receipt[name + '_sha256'], 'Final file digest: ' + name)
    expected = {(root, h, r, k) for root in ROOTS for h in REPAIRS for r in REGIMES for k in (4, 48)}
    lookup = {(row['root_seed'], row['repair'], row['regime'], row['K']): row for row in rows}
    require(len(rows) == len(lookup) == 2320 and set(lookup) == expected, 'Incomplete or duplicate observations')
    require(receipt['status'] == 'COMPLETED' and receipt['roots'] == 145 and receipt['episodes'] == 2320, 'Incomplete receipt')
    require(receipt['live_transitions'] == 27840 and receipt['confirmation_roots_executed'] == 145, 'Wrong transition/root counts')
    require(sum(row['queries'] for row in rows) == costs['completed_policy_queries'] == receipt['policy_queries'] == 5790720, 'Policy costs')
    require(sum(row['audit_replicas'] for row in rows) == costs['completed_scalar_audit_replicas'] == receipt['scalar_audit_replicas'] == 119808, 'Audit costs')
    require(sum(row['measurement_coordinates'] for row in rows) == costs['completed_measurement_coordinates'] == 92651520, 'Measurement costs')
    zero = all(row[key] == 0 for row in rows for key in ('violations', 'base_violations', 'stateful_violations'))
    require(zero == receipt['zero_violations'] == result['zero_executed_violations'], 'Violation flag mismatch')
    for row in rows:
        close(row['B'], row['harm_count'] / 96, 'Harm count/B mismatch')
        require(row['H'] == int(row['harm_count'] > 0), 'H mismatch')
        require(len(row['actions']) == 12 and row['queries'] == row['K'] * 96, 'Episode action/cost mismatch')
    criteria = {(c['repair'], c['regime'], c['endpoint']): c for c in result['criteria']}
    expected_criteria = {(h, r, endpoint) for h in REPAIRS[1:] for r in REGIMES for endpoint in ('A_B', 'D_P', 'H')}
    require(len(result['criteria']) == len(criteria) == 18 and set(criteria) == expected_criteria, 'Criterion completeness')
    differences = {(d['root_seed'], d['repair'], d['regime']): d for d in result['paired_differences']}
    require(len(differences) == len(result['paired_differences']) == 870, 'Paired difference completeness')
    close(result['alpha_per_bound'], ALPHA, 'Alpha mismatch')
    critical = float(t.ppf(1 - ALPHA, 144))
    passed = {}
    for h in REPAIRS[1:]:
        for r in REGIMES:
            a = [(lookup[root, 'original', r, 48]['B'] - lookup[root, 'original', r, 4]['B']) -
                 (lookup[root, h, r, 48]['B'] - lookup[root, h, r, 4]['B']) for root in ROOTS]
            p = [lookup[root, h, r, 48]['P'] - lookup[root, 'original', r, 48]['P'] for root in ROOTS]
            for root, av, pv in zip(ROOTS, a, p):
                d = differences[root, h, r]
                close(d['A_B'], av, 'Paired A_B mismatch'); close(d['D_P'], pv, 'Paired D_P mismatch')
                require(d['H'] == lookup[root, h, r, 48]['H'], 'Paired H mismatch')
            for endpoint, values, margin in (('A_B', a, .05), ('D_P', p, -.05)):
                c = criteria[h, r, endpoint]
                mean = fsum(values) / 145
                sd = sqrt(fsum((v - mean) ** 2 for v in values) / 144)
                lower = mean - critical * sd / sqrt(145) if sd else None
                close(c['mean'], mean, 'Mean mismatch'); close(c['sd'], sd, 'SD mismatch')
                require(c['threshold'] == margin and c['assessable'] == (sd > 0), 'Margin/variance rule mismatch')
                require(c['lower'] is None if lower is None else isclose(c['lower'], lower, abs_tol=1e-12), 'Lower bound mismatch')
                passed[h, r, endpoint] = lower is not None and lower > margin
                require(c['passed'] == passed[h, r, endpoint], 'Continuous decision mismatch')
            c = criteria[h, r, 'H']
            count = sum(lookup[root, h, r, 48]['H'] for root in ROOTS)
            upper = 1.0 if count == 145 else float(beta.ppf(1 - ALPHA, count + 1, 145 - count))
            close(c['upper'], upper, 'Incidence upper bound mismatch'); close(c['mean'], count / 145, 'Incidence mean')
            require(c['harmful_roots'] == count and c['roots'] == 145 and c['threshold'] == .10, 'Incidence count/margin')
            passed[h, r, 'H'] = upper < .10
            require(c['passed'] == passed[h, r, 'H'], 'Incidence decision')
    supported = {h: bool(zero and result['audit_passed'] and all(passed[h, r, e] for r in REGIMES for e in ('A_B', 'D_P', 'H'))) for h in REPAIRS[1:]}
    require(result['supported_repairs'] == supported, 'Repair-level decision mismatch')
    summaries = {(c['repair'], c['regime'], c['K']): c for c in result['cells']}
    require(len(summaries) == len(result['cells']) == 16, 'Cell summary completeness')
    for h in REPAIRS:
        for r in REGIMES:
            for k in (4, 48):
                selected = [lookup[root, h, r, k] for root in ROOTS]
                summary = summaries[h, r, k]
                for metric in ('B', 'L', 'P', 'Y_A', 'Y_B', 'R', 'H'):
                    close(summary[metric], fsum(row[metric] for row in selected) / 145, 'Cell mean ' + metric)
                require(summary['action_counts'] == {str(key): value for key, value in Counter(a for row in selected for a in row['actions']).items()}, 'Action frequencies')
    audit = load(folder / 'AUDIT.json')
    require(audit['status'] == 'PASSED' and audit['independent_external_review'] is False, 'Audit status/disclosure')
    require(audit['root_blocks_verified'] == 145 and audit['live_transitions_verified'] == 27840, 'Audit coverage')
    commits = load(folder / 'root-commitments.json')
    checkpoint = load(folder / 'CHECKPOINT.json')
    require([c['root_seed'] for c in commits] == list(ROOTS), 'Root commitment completeness')
    require(checkpoint['run_identity'] == run['identity'], 'Checkpoint run identity')
    require(checkpoint['roots'] == [{k: c[k] for k in ('root_seed', 'manifest_sha256')} for c in commits], 'Checkpoint anchors')
    for c in commits:
        require(c['run_identity'] == run['identity'] and c['anchor']['events'] == 192, 'Root identity/event count')
        manifest = {k: v for k, v in c.items() if k != 'manifest_sha256'}
        encoded = json.dumps(manifest, sort_keys=True, separators=(',', ':'), allow_nan=False).encode() + b'\n'
        require(hashlib.sha256(encoded).hexdigest() == c['manifest_sha256'], 'Root manifest hash')
        selected = [lookup[c['root_seed'], h, r, k] for h in REPAIRS for r in REGIMES for k in (4, 48)]
        encoded = json.dumps(selected, sort_keys=True, separators=(',', ':'), allow_nan=False).encode() + b'\n'
        require(hashlib.sha256(encoded).hexdigest() == c['metrics_sha256'], 'Per-root metrics hash')
    if archive:
        manifest = load(folder / 'trace-archive.json')
        require(archive.stat().st_size == manifest['bytes'] and sha(archive) == manifest['sha256'], 'Trace archive digest')
        with zipfile.ZipFile(archive) as zipped:
            require(len(zipped.namelist()) == len(set(zipped.namelist())) and set(zipped.namelist()) == set(manifest['files']), 'Archive membership')
            for name, expected_sha in manifest['files'].items():
                require(hashlib.sha256(zipped.read(name)).hexdigest() == expected_sha, 'Archived file: ' + name)
    return dict(status='VERIFIED', roots=145, episodes=2320, bounds_recomputed=18,
                supported_repairs=supported, trace_archive_verified=bool(archive), independent_external_review=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=RESULTS)
    parser.add_argument('--trace-archive', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.results, args.trace_archive)))
