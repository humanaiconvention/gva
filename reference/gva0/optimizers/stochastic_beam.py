"""Untuned stochastic beam traversal over the PUBLIC action language.

No world, evaluator, regime, root seed or production selector imports.
Independent running-best ranking uses exact rational replica averages.
"""
from fractions import Fraction
import random
from time import process_time


def preference(action, score, noop):
    return score, action == noop, -action


def search(ids, vectors, budget, seed, evaluate, noop=0, width=4, expansion=4, restart=.25):
    if budget not in (4, 16, 48) or len(ids) != 48 or len(set(ids)) != 48 or noop not in ids:
        raise ValueError("Unsupported finite search challenge")
    generator = random.Random(seed)
    unseen, scores, checkpoints, order = set(ids), {}, {}, []
    best = None
    while len(order) < budget:
        proposed = []
        beam = sorted(scores, key=lambda a: preference(a, scores[a], noop), reverse=True)[:width]
        for _ in range(min(expansion, budget - len(order))):
            remaining = sorted(unseen)
            if not scores and not proposed:
                action = noop
            elif generator.random() < restart:
                action = generator.choice(remaining)
            else:
                # Rank-based parent sampling preserves lexicographic score semantics.
                parent = generator.choices(beam, weights=[.5 ** j for j in range(len(beam))])[0] if beam else noop
                distances = {a: sum(abs(x - y) for x, y in zip(vectors[a], vectors[parent])) for a in remaining}
                minimum = min(distances.values())
                action = generator.choice([a for a in remaining if distances[a] == minimum])
            unseen.remove(action)
            proposed.append(action)
        batch = evaluate(tuple(proposed))
        if batch.action_ids != tuple(proposed) or any(len(s) != 8 for s in batch.scores):
            raise ValueError("Incomplete or mismatched public evaluation")
        for action, replicas in zip(proposed, batch.scores):
            score = tuple(sum((s[j] for s in replicas), Fraction(0)) / 8 for j in (0, 1))
            scores[action] = score
            order.append(action)
            if best is None or preference(action, score, noop) > preference(best, scores[best], noop):
                best = action
        if len(order) in (4, 16, 48):
            checkpoints[len(order)] = {"proposed": best, "score": scores[best], "evaluated": tuple(order)}
    return best, scores[best], checkpoints


def worker(connection):
    connection.send("ready")
    while True:
        command = connection.recv()
        if command is None:
            return
        ids, vectors, budget, private_seed = command
        cpu_started = process_time()
        def evaluate(requests):
            connection.send(("preview", requests))
            return connection.recv()
        result = search(ids, vectors, budget, private_seed, evaluate)
        connection.send(("chosen", *result, process_time() - cpu_started))
