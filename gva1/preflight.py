"""Run preparation on development roots only and issue a reproducible readiness receipt."""
from pathlib import Path
import argparse
import io
import json
import unittest
from . import ROOT
from .common import atomic_json, digest, read, require, sha, utc
from .design import development, verify_inputs, confirmation
from .freeze import source_files, runtime
from .runner import execute

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    verify_inputs()
    files = source_files()
    before = digest(files)
    capture = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests/gva1'), pattern='test_*.py')
    result = unittest.TextTestRunner(stream=capture, verbosity=2).run(suite)
    (out/'tests.txt').write_text(capture.getvalue(), encoding='utf-8')
    require(result.wasSuccessful(), 'Adversarial/semantic tests failed; see tests.txt')
    require(source_files() == files, 'Source changed during tests')
    print(f'Passed {result.testsRun} execution tests; starting complete development replay', flush=True)
    receipt = execute(development(), out/'development-replay')
    actual = read(out/'development-replay/metrics.json')
    golden_path = ROOT/'tests/gva1/pilot-golden.json'
    golden = read(golden_path)
    key = lambda row: (row['root_seed'], row['repair'], row['regime'], row['K'])
    expected = {key(row): row for row in golden}
    require(len(expected) == len(actual) == len(golden) == 640, 'Pilot fixture incomplete/duplicated')
    for row in actual:
        require(key(row) in expected, 'Unexpected development cell')
        for metric, value in expected[key(row)].items():
            if isinstance(value, float):
                require(abs(row[metric] - value) < 1e-12, 'Pilot numerical mismatch: ' + metric)
            else:
                require(row[metric] == value, 'Pilot exact mismatch: ' + metric)
    require({row['root_seed'] for row in actual} == set(development().roots), 'Replay used wrong roots')
    require(set(development().roots).isdisjoint(confirmation().roots), 'Development/confirmation overlap')
    require(source_files() == files, 'Source changed during full preflight')
    report = dict(status='PASSED', utc=utc(), source_hash=before, runtime=runtime(),
        episodes_matched=640, root_blocks_matched=40, live_transitions=7680,
        policy_preview_queries=receipt['policy_queries'], independent_scalar_candidate_replicas=receipt['scalar_audit_replicas'],
        golden_sha256=sha(golden_path), development_receipt_sha256=sha(out/'development-replay/COMPLETED.json'),
        test_log_sha256=sha(out/'tests.txt'), adversarial_tests=dict(passed=True, count=result.testsRun),
        checks=['all pilot endpoints and every action sequence', 'all 12 steps and 16 cells per root',
                'stateful rule/history metadata on acceptance and rejection', '12,288 gate/history cases',
                'unknown solver fails before dispatch', 'nominal previews / shifted live physics',
                'whole-root recovery and retained interrupted-attempt evidence', 'changed source/runtime/checkpoints rejected',
                'query/measurement/audit/setup/interruption accounting', 'incomplete confirmation analysis blocked',
                'strict bounds and zero-variance handling', 'guards survive python -O'],
        confirmation_roots_executed=0, independent_external_review=False,
        execution='Ready for a prospective execution freeze; outside review remains a separate roadmap step.')
    atomic_json(out/'PREFLIGHT.json', report)
    print(json.dumps(report))

if __name__ == '__main__':
    main()
