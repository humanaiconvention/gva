"""Counterexample queries over symbolic bounded inputs and an explicit gate relation."""
from hashlib import sha256
from time import perf_counter
import z3


def symbolic(prefix):
    return [[z3.Int(f"{prefix}_{field}_{i}") for i in range(8)] for field in ("q", "u", "m", "e")]


def schema(a):
    return z3.And(*[z3.And(x >= 0, x <= (2 if j == 0 else 1)) for j, vector in enumerate(a) for x in vector])


def contract_formula(a, omit_clause=None):
    q, u, m, e = a
    clauses = [z3.And(*[z3.And(x >= 0, x <= 1) for x in q]), z3.Sum(u) <= 4,
               z3.And(*[x == 0 for x in m]), z3.And(*[x == 0 for x in e])]
    return z3.And(*[c for j, c in enumerate(clauses) if j != omit_clause])


def equal(a, b):
    return z3.And(*[x == y for av, bv in zip(a, b) for x, y in zip(av, bv)])


ZERO = [[z3.IntVal(0) for _ in range(8)] for _ in range(4)]
TEMPLATE = contract_formula(symbolic("input"))
CONTRACT_HASH = sha256(TEMPLATE.sexpr().encode()).hexdigest()


def check_query(name, formula):
    solver = z3.Solver()
    solver.set(timeout=10000)
    solver.add(formula)
    encoded = solver.sexpr()
    started = perf_counter()
    result = solver.check()
    return {"name": name, "result": str(result), "seconds": perf_counter() - started,
            "solver_version": z3.get_version_string(), "formula_hash": sha256(encoded.encode()).hexdigest(),
            "formula": encoded, "counterexample": str(solver.model()) if result == z3.sat else None}


def obligations(mutate=False):
    a, out = symbolic("a"), symbolic("out")
    parsed = z3.Bool("parsed")
    accepted = z3.And(parsed, contract_formula(a, 2 if mutate else None))
    relation = z3.And(z3.Implies(parsed, schema(a)),
                      *[y == z3.If(accepted, x, 0) for av, ov in zip(a, out) for x, y in zip(av, ov)])
    checks = {
        "output_contract": z3.And(relation, z3.Not(contract_formula(out))),
        "conforming_preserved": z3.And(relation, parsed, contract_formula(a), z3.Not(equal(a, out))),
        "failing_noop": z3.And(relation, parsed, z3.Not(contract_formula(a)), z3.Not(equal(out, ZERO))),
        "parse_failure_no_execution": z3.And(relation, z3.Not(parsed), z3.Or(accepted, z3.Not(equal(out, ZERO)))),
        "noop_contract": z3.Not(contract_formula(ZERO)),
    }
    ids, next_ids = z3.IntVector("ids", 8), z3.IntVector("next_ids", 8)
    groups, next_groups = z3.IntVector("groups", 8), z3.IntVector("next_groups", 8)
    version, next_version = z3.Ints("version next_version")
    invariant = z3.And(version == 1, *[v == i for i, v in enumerate(ids)], *[v == i // 4 for i, v in enumerate(groups)])
    next_invariant = z3.And(next_version == 1, *[v == i for i, v in enumerate(next_ids)], *[v == i // 4 for i, v in enumerate(next_groups)])
    admin_transition = z3.And(next_version == version, *[x == y for x, y in zip(ids, next_ids)], *[x == y for x, y in zip(groups, next_groups)])
    checks["administration_unchanged"] = z3.And(relation, admin_transition, z3.Or(next_version != version, *[x != y for x, y in zip(ids, next_ids)], *[x != y for x, y in zip(groups, next_groups)]))
    checks["administration_initial"] = z3.And(invariant, z3.Not(invariant))
    checks["administration_induction"] = z3.And(invariant, relation, admin_transition, z3.Not(next_invariant))
    return [check_query(name, expression) for name, expression in checks.items()]


if __name__ == "__main__":
    import json
    results = obligations()
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if all(r["result"] == "unsat" for r in results) else 1)
