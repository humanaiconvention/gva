from time import perf_counter
from hashlib import sha256
import z3
from formal.gate_obligations import contract_formula, CONTRACT_HASH
from .types import AdminState, GateResult
from .actions import parse_id, NOOP
from .contracts import reasons


class FormalGate:
    def __init__(self, checker=None):
        self.cache = {}
        self.solver_log = []
        self.checker = checker

    def check(self, action):
        if action in self.cache:
            return self.cache[action]
        expression = contract_formula([[z3.IntVal(x) for x in v] for v in (action.q, action.u, action.m, action.e)])
        solver = z3.Solver()
        solver.set(timeout=1000)
        solver.add(expression)
        started = perf_counter()
        try:
            result = self.checker(solver) if self.checker else solver.check()
            status = str(result)
        except Exception as error:
            status = "error:" + type(error).__name__
        self.solver_log.append({"solver_version": z3.get_version_string(), "formula_hash": sha256(solver.sexpr().encode()).hexdigest(),
                                "result": status, "seconds": perf_counter() - started})
        answer = status == "sat", status
        # Only determinate answers are cached, under immutable parsed action and fixed formula.
        if status in ("sat", "unsat"):
            self.cache[action] = answer
        return answer

    def __call__(self, action_id, admin=AdminState(), enabled=True):
        if admin != AdminState():
            return GateResult(None, NOOP, False, ("ADMIN_INVALID",), CONTRACT_HASH)
        try:
            action = parse_id(action_id)
        except (ValueError, TypeError):
            return GateResult(None, NOOP, False, ("SCHEMA_INVALID",), CONTRACT_HASH)
        if not enabled:
            return GateResult(action_id, action_id, True, (), CONTRACT_HASH)
        allowed, status = self.check(action)
        codes = () if allowed else (reasons(action) if status == "unsat" else ("SOLVER_UNCHECKED",))
        return GateResult(action_id, action_id if allowed else NOOP, allowed, codes, CONTRACT_HASH)


_DEFAULT = FormalGate()


def gate(action, admin=AdminState(), enabled=True):
    return _DEFAULT(action, admin, enabled)
