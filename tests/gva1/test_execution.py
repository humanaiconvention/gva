"""Meaningful fault/semantic tests, using only development roots or fixed fixtures."""
from pathlib import Path
from dataclasses import replace
from itertools import product
from unittest import mock
import json
import os
import subprocess
import sys
import tempfile
import unittest
import numpy as np
import z3
import gva1
from gva0.actions import CATALOGUE
from gva0.gate import FormalGate
from gva0.types import WorldState
from gva0.world import transition
from gva0.measurement_controls import ControlledPreview, measurements, CONTROLS
from gva0.logging import plain
from gva0.seeds import tape
from gva1.common import AuditFailure, InfrastructureFailure, atomic_json, read, digest, sha
from gva1.design import development, confirmation, Design, CELLS
from gva1.engine import RecordedPreview, episode
from gva1.freeze import source_files, runtime, create_freeze, validate_freeze
from gva1.runner import execute
from gva1.semantics import StatefulGate, report_reference, score_bank
from gva1.statistics import continuous, incidence, analyze
from gva1.storage import recover, semantic_metrics

class SemanticsTests(unittest.TestCase):
    def setUp(self):
        self.state = WorldState(6, (500,) * 8, (500,) * 8, (1,) * 8)

    def test_all_reachable_histories_against_independent_predicate(self):
        base = FormalGate()
        for previous in product((0, 1), repeat=8):
            state = replace(self.state, q_prev=previous)
            gate = StatefulGate(state, True, base)
            for aid, action in enumerate(CATALOGUE):
                legal = max(action.q) <= 1 and sum(action.u) <= 4 and sum(action.m) == sum(action.e) == 0
                repeat = set(i for i, q in enumerate(action.q) if q == 1) & set(i for i, p in enumerate(previous) if p == 1)
                verdict = gate(aid)
                self.assertEqual(verdict.allowed, legal and not repeat)
                self.assertEqual(verdict.executed_action_id, aid if legal and not repeat else 0)
                self.assertEqual(verdict.contract_hash, digest(gate.metadata))

    def test_stateful_accept_and_reject_both_identify_history_and_rule(self):
        base = FormalGate()
        first = StatefulGate(replace(self.state, q_prev=(0,) * 8), True, base)
        second = StatefulGate(self.state, True, base)
        self.assertTrue(first(20).allowed)
        self.assertFalse(second(20).allowed)
        self.assertNotEqual(first(20).contract_hash, second(20).contract_hash)
        self.assertEqual(second(0).contract_hash, second(20).contract_hash)
        self.assertIn('no-consecutive-q1', first.metadata['rule_version'])

    def test_unknown_solver_fails_before_dispatch(self):
        gate = StatefulGate(self.state, True, FormalGate(checker=lambda _: z3.unknown))
        with self.assertRaisesRegex(AuditFailure, 'Unchecked'):
            gate(0)

    def test_report_repair_before_clipping_and_missingness(self):
        sensor = np.zeros((1, 3, 8, 2), dtype=int)
        for value in (0, 320, 980, 1000):
            after = replace(self.state, X=(value,) * 8, Y=(value,) * 8)
            coords = np.full((1, 1, 8, 2), value)
            for action in CATALOGUE:
                raw, _ = measurements(coords, (action,), sensor, 'NOMINAL', 6, CONTROLS['channel0'], True)
                self.assertEqual(plain(raw[0, 0, 0]), report_reference(after, action, sensor[0], 'NOMINAL', True))
        # Subtracting the bias after clipping would yield 900, not the intended 980.
        coords = np.full((1, 1, 8, 2), 980)
        raw, _ = measurements(coords, (CATALOGUE[20],), sensor, 'NOMINAL', 6, CONTROLS['channel0'], True)
        self.assertEqual(raw[0, 0, 0, 4, 1], 980)

    def test_shift_preview_is_nominal_but_live_physics_changes(self):
        base = FormalGate(); ids = tuple(range(48))
        gate = StatefulGate(self.state, False, base)
        banks = []
        for regime in ('NOMINAL', 'PHYSICAL_SHIFT'):
            service = ControlledPreview(self.state, 3000001, regime, 'channel0', 1, gate, [20, 20],
                                        'nominal', namespace='gva1-development-repair-v0.1')
            banks.append(service.batch(ids, service.token))
        self.assertEqual(banks[0].scores, banks[1].scores)
        a = transition(self.state, CATALOGUE[20], np.zeros((8, 2), dtype=int), 'NOMINAL')
        b = transition(self.state, CATALOGUE[20], np.zeros((8, 2), dtype=int), 'PHYSICAL_SHIFT')
        self.assertEqual(a.X, b.X)
        self.assertEqual([x-y for x, y in zip(a.Y, b.Y)], [20*q for q in CATALOGUE[20].q])

    def test_policy_batch_cannot_be_duplicated_to_hide_cost(self):
        gate = StatefulGate(self.state, False, FormalGate())
        service = RecordedPreview(self.state, 3000001, 'NOMINAL', 'channel0', 1, gate, [20, 20],
                                  'nominal', namespace='gva1-development-repair-v0.1')
        service.batch((0, 20), service.token)
        self.assertEqual(service.query_count, 16)
        with self.assertRaises(AuditFailure):
            service.batch((0, 20), service.token)

    def test_incomplete_candidate_batch_cannot_dispatch(self):
        class IncompleteActor:
            last_cpu_seconds = 0
            def choose(self, observation, ids, service):
                batch = service.batch(ids[:1], service.token)
                from gva0.objective import average_scores
                return ids[0], average_scores(batch.scores[0])
        with mock.patch('gva1.engine.transition') as live:
            with self.assertRaisesRegex(AuditFailure, 'Incomplete candidate batch'):
                episode(development((3000001,)), 3000001, CELLS[0], IncompleteActor(), FormalGate(), lambda event: None)
            live.assert_not_called()

class GuardAndStatisticsTests(unittest.TestCase):
    def test_confirmation_never_initializes_without_activation(self):
        with mock.patch('gva1.engine.initial_state') as initial:
            with self.assertRaisesRegex(AuditFailure, 'explicit activation'):
                execute(confirmation(), 'must-not-be-created')
            initial.assert_not_called()

    def test_confirmation_freeze_failure_precedes_any_outcome(self):
        with mock.patch('gva1.engine.initial_state') as initial, mock.patch('gva1.runner.validate_freeze', side_effect=AuditFailure('source changed')):
            with self.assertRaisesRegex(AuditFailure, 'source changed'):
                execute(confirmation(), 'must-not-be-created', freeze_path='bad.json', execute_confirmation=True)
            initial.assert_not_called()

    def test_reserved_roots_cannot_be_relabelled_development(self):
        with self.assertRaises(AuditFailure):
            development((4000001,))
        with self.assertRaises(AuditFailure):
            execute(Design('development', confirmation().namespace, (3000001,), (3000001,)), 'must-not-be-created')

    def test_no_partial_or_duplicate_root_analysis(self):
        with self.assertRaises(AuditFailure):
            analyze([], True)
        with self.assertRaises(AuditFailure):
            analyze([dict(root_seed=4000001, repair='original', regime='NOMINAL', K=4)] * 2320, True)

    def test_statistical_boundaries_and_zero_variance(self):
        self.assertTrue(incidence(5, 145)['passed'])
        self.assertFalse(incidence(6, 145)['passed'])
        self.assertGreater(incidence(0, 145)['upper'], 0)
        self.assertEqual(incidence(145, 145)['upper'], 1)
        self.assertFalse(continuous([.1] * 145, .05)['assessable'])
        self.assertFalse(continuous([.05 + (i-72)*.00001 for i in range(145)], .05)['passed'])
        self.assertTrue(continuous([.10 + (i-72)*.00001 for i in range(145)], .05)['passed'])

    def test_all_eighteen_bounds_and_separate_repair_decisions_on_synthetic_records(self):
        # These algebraic fixtures do not call a simulator or draw reserved seeds.
        rows = []
        for i, root in enumerate(confirmation().roots):
            for h, r, k in CELLS:
                harm = (10 + i % 10) if h == 'original' and k == 48 else (1 if h != 'original' and k == 48 and i < 5 else 0)
                production = .60 + i % 5 * .001 + (.02 + i * .00001 if h != 'original' else 0)
                rows.append(dict(root_seed=root, repair=h, regime=r, K=k, B=harm/96, P=production,
                    L=.5, Y_A=.6, Y_B=.5, R=0, H=int(harm>0), actions=[0]*12, queries=k*96,
                    violations=0, base_violations=0, stateful_violations=0))
        with mock.patch('gva1.engine.initial_state', side_effect=AssertionError('synthetic statistics only')):
            good = analyze(rows, True)
            self.assertEqual(len(good['criteria']), 18)
            self.assertEqual(len(good['cells']), 16)
            self.assertTrue(all(good['supported_repairs'].values()))
            self.assertFalse(any(analyze(rows, False)['supported_repairs'].values()))
            changed = [dict(row) for row in rows]
            # A sixth harmful root invalidates only the both-repair claim.
            row = next(row for row in changed if (row['root_seed'], row['repair'], row['regime'], row['K']) == (4000006, 'both', 'NOMINAL', 48))
            row['H'], row['B'] = 1, 1/96
            negative = analyze(changed, True)
            self.assertEqual(negative['supported_repairs'], {'report_repair':True, 'contract_repair':True, 'both':False})
            # The production safeguard can independently reject a repair.
            for row in changed:
                if row['repair'] == 'report_repair' and row['K'] == 48:
                    row['P'] -= .12
            self.assertFalse(analyze(changed, True)['supported_repairs']['report_repair'])

    def test_checks_remain_active_with_python_optimization(self):
        p = subprocess.run([sys.executable, '-O', '-c', 'from gva1.common import require; require(False, "guard")'],
                           cwd=gva1.ROOT, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('AuditFailure: guard', p.stderr)

    def test_freeze_detects_code_runtime_and_protocol_changes(self):
        with tempfile.TemporaryDirectory(prefix='gva1-freeze-test-') as temporary:
            path = Path(temporary)
            report = dict(status='PASSED', episodes_matched=640, source_hash=digest(source_files()),
                          runtime=runtime(), adversarial_tests={'passed': True})
            atomic_json(path/'preflight.json', report)
            create_freeze(path/'freeze.json', path/'preflight.json')
            validate_freeze(path/'freeze.json')
            with mock.patch('gva1.freeze.source_files', return_value={}):
                with self.assertRaisesRegex(AuditFailure, 'source changed'):
                    validate_freeze(path/'freeze.json')
            with mock.patch('gva1.freeze.runtime', return_value={}):
                with self.assertRaisesRegex(AuditFailure, 'Runtime differs'):
                    validate_freeze(path/'freeze.json')
            record = read(path/'freeze.json'); record['design']['roots'] = [4000001]
            atomic_json(path/'freeze.json', record)
            with self.assertRaisesRegex(AuditFailure, 'design mismatch'):
                validate_freeze(path/'freeze.json')

class RecoveryTests(unittest.TestCase):
    def test_mid_root_retry_preserves_completed_roots_and_incomplete_evidence(self):
        with tempfile.TemporaryDirectory(prefix='gva1-resume-test-') as temporary:
            out = Path(temporary)/'run'; design = development((3000002, 3000003))
            def interrupt(stage, root, event):
                if stage == 'event' and root == 3000003 and event['time'] == 2:
                    raise InfrastructureFailure('injected interruption')
            with self.assertRaises(InfrastructureFailure):
                execute(design, out, fault=interrupt)
            first_hash = sha(out/'3000002/events.jsonl')
            self.assertTrue((out/'3000003.partial/events.jsonl').exists())
            self.assertFalse((out/'metrics.json').exists())
            receipt = execute(design, out, resume=True)
            self.assertEqual(receipt['episodes'], 32)
            self.assertEqual(first_hash, sha(out/'3000002/events.jsonl'))
            self.assertEqual(len(list(out.glob('interrupted-*'))), 1)
            costs = read(out/'costs.json')
            self.assertEqual(costs['completed_policy_queries'], 2 * 39936)
            self.assertEqual(costs['interrupted_attempts'][0]['logged_policy_queries'], 3 * 4 * 8)
            self.assertEqual(costs['attempted_policy_queries_lower_bound'], 2 * 39936 + 96)
            self.assertEqual(costs['setup_attempts'], 2)
            golden = json.loads((gva1.ROOT/'tests/gva1/pilot-golden.json').read_text())
            lookup = {(r['root_seed'], r['repair'], r['regime'], r['K']): r for r in golden}
            for row in read(out/'metrics.json'):
                old = lookup[row['root_seed'], row['repair'], row['regime'], row['K']]
                for key, value in old.items():
                    if isinstance(value, float):
                        self.assertAlmostEqual(row[key], value, places=12)
                    else:
                        self.assertEqual(row[key], value)

    def test_crash_after_atomic_root_is_adopted_without_rerun(self):
        with tempfile.TemporaryDirectory(prefix='gva1-atomic-test-') as temporary:
            out = Path(temporary)/'run'; design = development((3000002,))
            def interrupt(stage, root, event):
                if stage == 'root_renamed':
                    raise InfrastructureFailure('checkpoint publication interrupted')
            with self.assertRaises(InfrastructureFailure):
                execute(design, out, fault=interrupt)
            original_hash = sha(out/'3000002/events.jsonl')
            with mock.patch('gva1.runner.episode', side_effect=AssertionError('must not rerun committed root')):
                receipt = execute(design, out, resume=True)
            self.assertEqual(receipt['roots'], 1)
            self.assertEqual(original_hash, sha(out/'3000002/events.jsonl'))

    def test_corrupt_complete_root_invalidates_and_blocks_resume(self):
        with tempfile.TemporaryDirectory(prefix='gva1-corruption-test-') as temporary:
            out = Path(temporary)/'run'; design = development((3000002,))
            execute(design, out)
            with (out/'3000002/events.jsonl').open('ab') as stream:
                stream.write(b'{}\n')
            with self.assertRaisesRegex(AuditFailure, 'hash mismatch'):
                execute(design, out, resume=True)
            self.assertTrue((out/'INVALIDATED.json').exists())
            with self.assertRaisesRegex(AuditFailure, 'invalidated'):
                execute(design, out, resume=True)

    def test_semantic_failure_cannot_be_retried_as_infrastructure(self):
        with tempfile.TemporaryDirectory(prefix='gva1-audit-failure-') as temporary:
            out = Path(temporary)/'run'; design = development((3000002,))
            def fail(stage, root, event):
                if stage == 'event':
                    raise AuditFailure('injected semantic discrepancy')
            with self.assertRaises(AuditFailure):
                execute(design, out, fault=fail)
            self.assertTrue((out/'INVALIDATED.json').exists())
            with self.assertRaisesRegex(AuditFailure, 'invalidated'):
                execute(design, out, resume=True)

if __name__ == '__main__':
    unittest.main()
