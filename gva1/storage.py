"""Atomic whole-root checkpoints; invalid audits cannot be retried as infrastructure."""
from pathlib import Path
import json
import os
import uuid
from gva0.logging import EventWriter, verify_stream, plain
from gva0.types import WorldState
from gva0.actions import CATALOGUE
from gva0.seeds import candidates, tape
from gva0.world import initial_state
from analysis import scalar_reference as scalar
from .common import read, atomic_json, sha, digest, require, journal, utc
from .design import CELLS
from .semantics import permitted, report_reference, StatefulGate

def semantic_metrics(rows):
    return [{k: v for k, v in row.items() if not k.endswith('_seconds')} for row in rows]

class RootWriter:
    def __init__(self, output, root, identity):
        self.output, self.root, self.identity = Path(output), root, identity
        self.folder = self.output / f'{root}.partial'
        self.folder.mkdir()
        self.events = EventWriter(self.folder / 'events.jsonl')

    def emit(self, event):
        self.events.append(event)

    def close_incomplete(self):
        if not self.events.file.closed:
            self.events.file.flush()
            os.fsync(self.events.file.fileno())
            self.events.close()

    def commit(self, metrics):
        self.events.file.flush()
        os.fsync(self.events.file.fileno())
        anchor = self.events.close()
        require(anchor['events'] == 192 and len(metrics) == 16, 'Incomplete root cannot commit')
        atomic_json(self.folder / 'metrics.json', metrics)
        manifest = dict(root_seed=self.root, run_identity=self.identity, anchor=anchor,
            metrics_sha256=sha(self.folder / 'metrics.json'), events_sha256=sha(self.folder / 'events.jsonl'),
            scientific_metrics_sha256=digest(semantic_metrics(metrics)))
        atomic_json(self.folder / 'COMPLETE.json', manifest)
        final = self.output / str(self.root)
        require(not final.exists(), 'Never overwrite a completed root')
        os.rename(self.folder, final)
        return manifest

def reconstruct_state(value):
    return WorldState(value['t'], tuple(value['X']), tuple(value['Y']), tuple(value['q_prev']),
                      tuple(value['ids']), tuple(value['groups']))

def verify_root(folder, design, root, identity):
    folder = Path(folder)
    manifest = read(folder / 'COMPLETE.json')
    require(manifest['root_seed'] == root and manifest['run_identity'] == identity, 'Foreign root checkpoint')
    require(sha(folder / 'metrics.json') == manifest['metrics_sha256'], 'Checkpoint metric hash mismatch')
    require(sha(folder / 'events.jsonl') == manifest['events_sha256'], 'Checkpoint trace hash mismatch')
    try:
        verify_stream(folder / 'events.jsonl', manifest['anchor'])
    except ValueError as error:
        require(False, 'Event chain invalid: ' + str(error))
    events = [json.loads(line) for line in (folder / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
    metrics = read(folder / 'metrics.json')
    require(len(events) == 192 and len(metrics) == 16, 'Root completeness mismatch')
    require(digest(semantic_metrics(metrics)) == manifest['scientific_metrics_sha256'], 'Scientific metric digest mismatch')
    for index, (repair, regime, K) in enumerate(CELLS):
        subset = events[index * 12:(index + 1) * 12]
        row = metrics[index]
        require((row['root_seed'], row['repair'], row['regime'], row['K']) == (root, repair, regime, K), 'Cell order/identity mismatch')
        state = initial_state(root, design.namespace)
        actions, repeats = [], 0
        for time, event in enumerate(subset):
            require((event['root_seed'], event['namespace'], event['repair'], event['regime'], event['K'], event['time']) ==
                    (root, design.namespace, repair, regime, K, time), 'Trace identity/order mismatch')
            require(event['before'] == plain(state), 'State continuity mismatch')
            contract, report = repair in ('contract_repair', 'both'), repair in ('report_repair', 'both')
            metadata = StatefulGate(state, contract, None).metadata
            require(event['contract'] == metadata and event['authorized']['contract_hash'] == digest(metadata), 'Accepted/rejected stateful metadata mismatch')
            aid = event['authorized']['executed_action_id']
            action = CATALOGUE[aid]
            require(event['action'] == plain(action) and permitted(action, state, contract), 'Checkpoint executed predicate mismatch')
            process, sensor = tape(root, time, 'live', namespace=design.namespace)
            require(event['process_noise'] == plain(process[0]) and event['sensor_noise'] == plain(sensor[0]), 'Disturbance namespace mismatch')
            expected = scalar.step(plain(state), action, process[0].tolist(), regime)
            require(event['after'] == expected, 'Checkpoint scalar physics mismatch')
            after = reconstruct_state(expected)
            require(event['reports'] == [report_reference(after, action, sensor[0], regime, report)], 'Checkpoint scalar reporting mismatch')
            require(event['missing'] == [bool(v) for v in action.e] and len(event['reports'][0]) == 8, 'Missingness/roster mismatch')
            require(event['candidate_ids'] == list(candidates(root, time, K, design.namespace)), 'Candidate order mismatch')
            require(event['preview_replicas'] == 8 and event['preview_physics'] == 'NOMINAL', 'Preview contract mismatch')
            require(event['costs']['policy_queries'] == K * 8 and event['costs']['measurement_coordinates'] == K * 8 * 16, 'Trace cost mismatch')
            require(event['costs']['scalar_audit_replicas'] == (K * 8 if root in design.audit_roots else 0), 'Audit cost mismatch')
            require(all(event['audits'][key] for key in ('live_scalar', 'stateful_predicate')), 'Missing live audit')
            require(event['audits']['scalar_candidate_bank'] == (root in design.audit_roots), 'Wrong candidate audit roots')
            repeats += any(q == p == 1 for q, p in zip(action.q, state.q_prev))
            actions.append(aid)
            state = after
        expected = scalar.endpoints(subset)
        for key, value in expected.items():
            require(abs(row[key] - value) < 1e-12, 'Reconstructed endpoint mismatch: ' + key)
        require(row['actions'] == actions and row['R'] == repeats / 12 and row['H'] == int(row['harm_count'] > 0), 'Action/H/R mismatch')
        require(row['queries'] == 12 * K * 8 and row['audit_replicas'] == (12 * K * 8 if root in design.audit_roots else 0), 'Root cost mismatch')
        require(row['violations'] == row['base_violations'] == row['stateful_violations'] == 0, 'Recorded violations')
    return manifest, metrics

def recover(output, design, identity):
    output = Path(output).resolve()
    require(not (output / 'INVALIDATED.json').exists(), 'Audit-invalidated run cannot resume')
    require(all(int(p.name) in design.roots for p in output.iterdir() if p.is_dir() and p.name.isdigit()), 'Foreign completed root directory')
    checkpoint = read(output / 'CHECKPOINT.json') if (output / 'CHECKPOINT.json').exists() else {'roots': []}
    require(checkpoint.get('run_identity', identity) == identity, 'Checkpoint belongs to another run')
    commits, rows = [], []
    gap = False
    for root in design.roots:
        folder = output / str(root)
        if folder.exists():
            require(not gap, 'Completed roots must form an ordered prefix')
            manifest, metrics = verify_root(folder, design, root, identity)
            commits.append(dict(root_seed=root, manifest_sha256=sha(folder / 'COMPLETE.json')))
            rows.extend(metrics)
        else:
            gap = True
    require(checkpoint['roots'] == commits[:len(checkpoint['roots'])], 'Checkpoint prefix changed')
    if len(commits) > len(checkpoint['roots']):
        journal(output / 'RECOVERY.jsonl', dict(utc=utc(), event='adopt_verified_atomic_root', roots=[v['root_seed'] for v in commits[len(checkpoint['roots']):]]))
    for partial in output.glob('*.partial'):
        require(partial.is_dir() and partial.stem.isdigit(), 'Unexpected partial path')
        root = int(partial.stem)
        require(len(commits) < len(design.roots) and root == design.roots[len(commits)], 'Unexpected interrupted root')
        retained = output / ('interrupted-' + partial.name + '-' + uuid.uuid4().hex)
        require(partial.resolve().parent == output and retained.resolve().parent == output, 'Recovery move escaped run directory')
        journal(output / 'RECOVERY.jsonl', dict(utc=utc(), event='retain_incomplete_root_before_deterministic_retry', root_seed=root, directory=retained.name))
        os.rename(partial, retained)
    atomic_json(output / 'CHECKPOINT.json', dict(run_identity=identity, roots=commits))
    return commits, rows

def cost_report(output, metrics):
    output = Path(output)
    def records(path):
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    interrupted = []
    for folder in output.glob('interrupted-*'):
        entries, truncated = [], False
        for line in (folder/'events.jsonl').read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                event = json.loads(line)
                if 'costs' in event:
                    entries.append(event)
            except (ValueError, TypeError):
                truncated = True
        interrupted.append(dict(directory=folder.name, logged_decisions=len(entries),
            logged_policy_queries=sum(e['costs']['policy_queries'] for e in entries),
            logged_decision_seconds=sum(e['timing']['decision_seconds'] for e in entries),
            logged_scalar_audit_replicas=sum(e['costs']['scalar_audit_replicas'] for e in entries),
            truncated_log=truncated))
    setup = records(output/'SETUP.jsonl')
    audits = records(output/'CHECKPOINT-AUDITS.jsonl')
    return dict(completed_policy_queries=sum(row['queries'] for row in metrics),
        completed_scalar_audit_replicas=sum(row['audit_replicas'] for row in metrics),
        completed_measurement_coordinates=sum(row['measurement_coordinates'] for row in metrics),
        completed_decision_seconds=sum(row['decision_seconds'] for row in metrics),
        completed_live_audit_seconds=sum(row['evaluator_audit_seconds'] for row in metrics),
        completed_logging_seconds=sum(row['evaluator_logging_seconds'] for row in metrics),
        setup_attempts=len(setup), formal_and_gate_setup_seconds=sum(r['formal_and_gate_seconds'] for r in setup),
        actor_startup_seconds=sum(r['actor_startup_seconds'] for r in setup),
        checkpoint_validation_seconds=sum(r['seconds'] for r in audits),
        interrupted_attempts=interrupted,
        attempted_policy_queries_lower_bound=sum(row['queries'] for row in metrics)+sum(r['logged_policy_queries'] for r in interrupted),
        limitation='Interrupted-attempt costs are lower bounds: a crash can precede event persistence. They are never counted as extra scientific observations. Decision timing excludes live execution, evaluator audits, logging and setup.')
