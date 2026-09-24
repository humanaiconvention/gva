"""Independent predicate: imports no simulator, sensor, regime, or evaluator."""
from .types import Action


def reasons(action: Action):
    result = []
    if any(q > 1 for q in action.q):
        result.append("Q_LIMIT")
    if sum(action.u) > 4:
        result.append("U_BUDGET")
    if any(action.m):
        result.append("M_WRITE")
    if any(action.e):
        result.append("E_OMIT")
    return tuple(result)


def contract(action: Action):
    return not reasons(action)
