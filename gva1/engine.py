"""Unchanged pilot decisions with complete traces and measured policy costs."""
from time import perf_counter
import hashlib
import numpy as np
from gva0.actions import CATALOGUE
from gva0.evaluator import evaluate
from gva0.logging import plain
from gva0.measurement_controls import ControlledPreview, measurements, CONTROLS
from gva0.objective import average_scores
from gva0.seeds import candidates, tape
from gva0.types import ActorObservations, nullable
from gva0.world import initial_state, transition
from analysis import scalar_reference as scalar
from .common import require, InfrastructureFailure, digest
from .design import CELLS, validate_design
from .semantics import StatefulGate, permitted, report_reference, score_bank

class RecordedPreview(ControlledPreview):
    def batch(self, ids, token):
        require(not hasattr(self, 'recorded'), 'Only one policy preview batch is permitted')
        self.recorded = super().batch(ids, token)
        return self.recorded

def episode(design, root, cell, actor, base_gate, emit):
    validate_design(design)
    require(root in design.roots and cell in CELLS, 'Episode outside committed design')
    repair, regime, K = cell
    report = repair in ('report_repair', 'both')
    contract = repair in ('contract_repair', 'both')
    state = initial_state(root, design.namespace)
    observation = None
    events, states, actions = [], [], []
    repeats = queries = audit_queries = 0
    decision_seconds = audit_seconds = logging_seconds = 0.0
    for time in range(12):
        # Current observation is available. Includes candidates, all previews,
        # comparisons and final authorization; ends before execution/auditing.
        started = perf_counter()
        ids = candidates(root, time, K, design.namespace)
        gate = StatefulGate(state, contract, base_gate)
        preview = RecordedPreview(state, root, regime, 'channel0', 1, gate, [20, 20],
                                  'nominal', remove_q_bias=report, namespace=design.namespace)
        try:
            proposal, score = actor.choose(observation, ids, preview)
        except RuntimeError as error:
            if str(error).startswith('Actor IPC timeout'):
                raise InfrastructureFailure('Actor IPC timeout') from error
            raise
        authorization = gate(proposal)
        action = CATALOGUE[authorization.executed_action_id]
        elapsed = perf_counter() - started
        decision_seconds += elapsed
        check_started = perf_counter()
        batch = preview.recorded
        require(batch.action_ids == ids and len(batch.scores) == K, 'Incomplete candidate batch')
        require(all(len(s) == 8 for s in batch.scores), 'Incomplete candidate replicas')
        require(batch.channel_values.shape == (K, 8, 1, 8, 2), 'Preview dimensions changed')
        require(preview.query_count == 8 * K, 'Policy query accounting mismatch')
        require(preview.measurement_count == 16 * preview.query_count, 'Acquisition count mismatch')
        scores = {a: average_scores(s) for a, s in zip(ids, batch.scores)}
        winner = max(ids, key=lambda a: (scores[a], a == 0, -a))
        require(proposal == winner and score == scores[winner], 'Ranking/tie-breaking mismatch')
        for aid, candidate_gate in zip(ids, batch.gate_results):
            legal = permitted(CATALOGUE[aid], state, contract)
            require(candidate_gate.allowed == legal and candidate_gate.executed_action_id == (aid if legal else 0), 'Candidate authorization mismatch')
            require(candidate_gate.contract_hash == gate.contract_hash, 'Candidate state/rule identity mismatch')
        require(permitted(action, state, contract), 'Executed base/stateful violation')
        require(authorization == batch.gate_results[ids.index(proposal)], 'Final authorization differs from preview')
        audited = root in design.audit_roots
        scalar_seconds = 0.0
        if audited:
            scalar_started = perf_counter()
            process, sensor = tape(root, time, 'preview', namespace=design.namespace)
            expected, execution, expected_winner = score_bank(state, ids, process, sensor, contract, report)
            require(scores == expected and proposal == expected_winner, 'Independent scalar bank mismatch')
            require([g.executed_action_id for g in batch.gate_results] == [execution[a] for a in ids], 'Scalar candidate gate mismatch')
            scalar_seconds = perf_counter() - scalar_started
            audit_queries += 8 * K
        audit_elapsed = perf_counter() - check_started
        execution_started = perf_counter()
        process, sensor = tape(root, time, 'live', namespace=design.namespace)
        after = transition(state, action, process[0], regime)
        raw, _ = measurements(np.array(list(zip(after.X, after.Y)))[None, None], (action,),
                              sensor, regime, time, CONTROLS['channel0'], remove_q_bias=report)
        execution_elapsed = perf_counter() - execution_started
        live_audit_started = perf_counter()
        require(plain(after) == scalar.step(plain(state), action, process[0].tolist(), regime), 'Live physical mismatch')
        require(plain(raw[0, 0, 0]) == report_reference(after, action, sensor[0], regime, report), 'Live report mismatch')
        missing = tuple(bool(x) for x in action.e)
        observation = ActorObservations(nullable(raw[0, 0]), (0,), missing, provenance='GVA1:' + repair)
        audit_elapsed += perf_counter() - live_audit_started
        audit_seconds += audit_elapsed
        repeats += any(q == p == 1 for q, p in zip(action.q, state.q_prev))
        actions.append(authorization.executed_action_id)
        queries += preview.query_count
        event = plain(dict(root_seed=root, namespace=design.namespace, repair=repair, regime=regime, K=K,
            time=time, before=state, after=after, observations=observation, reports=raw[0, 0],
            missing=missing, proposed=proposal, authorized=authorization, action=action,
            contract=gate.metadata, candidate_ids=ids, candidate_gates=batch.gate_results,
            scores=[scores[a] for a in ids], selected_score=score, preview_replicas=8,
            preview_physics='NOMINAL', preview_dtype=str(batch.channel_values.dtype),
            preview_shape=list(batch.channel_values.shape), preview_values_sha256=hashlib.sha256(batch.channel_values.tobytes()).hexdigest(),
            process_noise=process[0], sensor_noise=sensor[0],
            costs=dict(policy_queries=preview.query_count, measurement_coordinates=preview.measurement_count,
                       exposed_coordinates=preview.exposed_count, scalar_audit_replicas=8 * K if audited else 0,
                       duplicate_policy_audit_queries=0),
            audits=dict(live_scalar=True, stateful_predicate=True, scalar_candidate_bank=audited),
            timing=dict(decision_seconds=elapsed, preview_seconds=preview.seconds, actor_cpu_seconds=actor.last_cpu_seconds,
                        evaluator_audit_seconds=audit_elapsed, scalar_bank_seconds=scalar_seconds,
                        live_execution_seconds=execution_elapsed)))
        log_started = perf_counter()
        emit(event)
        logging_seconds += perf_counter() - log_started
        events.append(event)
        states.append(after)
        state = after
    metrics = evaluate(states)._asdict()
    expected = scalar.endpoints(events)
    require(all(abs(metrics[k] - v) < 1e-12 for k, v in expected.items()), 'Endpoint arithmetic mismatch')
    return dict(root_seed=root, repair=repair, K=K, regime=regime, **metrics, R=repeats / 12,
        H=int(metrics['harm_count'] > 0), violations=0, base_violations=0, stateful_violations=0,
        actions=actions, queries=queries, audit_replicas=audit_queries,
        measurement_coordinates=queries * 16, decision_seconds=decision_seconds,
        evaluator_audit_seconds=audit_seconds, evaluator_logging_seconds=logging_seconds)
