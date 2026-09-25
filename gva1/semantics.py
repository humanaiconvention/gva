"""Independent scalar checks and state-aware authorization metadata."""
from dataclasses import replace
from fractions import Fraction
from gva0.actions import CATALOGUE
from gva0.types import GateResult
from gva0.logging import plain
from analysis import scalar_reference as scalar
from formal.gate_obligations import CONTRACT_HASH
from .common import digest, require

RULE = 'GVA1-base-plus-no-consecutive-q1-v1'

def permitted(action, before, repaired):
    base = all(q <= 1 for q in action.q) and sum(action.u) <= 4 and not any(action.m) and not any(action.e)
    repeated = any(action.q[i] == 1 and before.q_prev[i] == 1 for i in range(8))
    return base and not (repaired and repeated)

class StatefulGate:
    def __init__(self, state, repaired, base):
        self.state, self.repaired, self.base = state, repaired, base
        self.metadata = dict(base_contract_hash=CONTRACT_HASH,
            rule_version=RULE if repaired else 'GVA1-base-only-v1',
            repair_enabled=repaired, time=state.t, ids=list(state.ids), q_previous=list(state.q_prev))
        self.contract_hash = digest(self.metadata)

    def __call__(self, action_id, enabled=True):
        require(enabled, 'GVA-1 always enforces the contract')
        answer = self.base(action_id, enabled=True)
        require('SOLVER_UNCHECKED' not in answer.reason_codes, 'Unchecked solver result: no action dispatched')
        allowed = answer.allowed
        reasons = answer.reason_codes
        if allowed and self.repaired and any(q == p == 1 for q, p in zip(CATALOGUE[action_id].q, self.state.q_prev)):
            allowed, reasons = False, ('REPEATED_Q1_BLOCKED',)
        return GateResult(answer.proposed_action_id, action_id if allowed else 0, allowed, reasons, self.contract_hash)

def report_reference(after, action, sensor, regime, remove_bias):
    reporting_action = replace(action, q=(0,) * 8) if remove_bias else action
    return scalar.measurements(plain(after), reporting_action, sensor.tolist(), regime)[0]

def score_bank(before, ids, process, sensor, contract_repair, report_repair):
    scores = {}
    execution = {}
    for aid in ids:
        action = CATALOGUE[aid]
        executed = aid if permitted(action, before, contract_repair) else 0
        action = CATALOGUE[executed]
        report_action = replace(action, q=(0,) * 8) if report_repair else action
        sums = [Fraction(0), Fraction(0)]
        for replica in range(8):
            after = scalar.step(plain(before), action, process[replica].tolist(), 'NOMINAL')
            raw = scalar.measurements(after, report_action, sensor[replica].tolist(), 'NOMINAL')
            value = scalar.score(raw, 0, 'full_roster_zero')
            sums = [a + b for a, b in zip(sums, value)]
        scores[aid], execution[aid] = tuple(v / 8 for v in sums), executed
    winner = max(ids, key=lambda aid: (scores[aid], aid == 0, -aid))
    return scores, execution, winner
