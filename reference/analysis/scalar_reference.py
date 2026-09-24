"""Independent audit semantics: scalar loops, rational scores, no world/sensor imports."""
from fractions import Fraction


def clip(value):
    return min(1000, max(0, int(value)))


def permitted(action):
    return all(0 <= x <= 1 for x in action.q) and sum(action.u) <= 4 and not any(action.m) and not any(action.e)


def step(before, action, noise, regime):
    fatigue = 40 if regime == "PHYSICAL_SHIFT" and before["t"] >= 6 else 20
    X, Y = [], []
    for i in range(8):
        X.append(clip(before["X"][i] + 60 * action.q[i] + 30 * action.u[i] - 10 + noise[i][0]))
        Y.append(clip(before["Y"][i] + 40 * action.u[i] - 40 * action.q[i] ** 2
                      - fatigue * action.q[i] * before["q_prev"][i] - 15 * action.m[i]
                      - 20 * action.e[i] + noise[i][1]))
    return {"t": before["t"] + 1, "X": X, "Y": Y, "q_prev": list(action.q),
            "ids": list(before["ids"]), "groups": list(before["groups"])}


def measurements(after, action, noise, regime):
    raw = []
    for channel in range(3):
        people = []
        for i in range(8):
            if action.e[i]:
                people.append([None, None])
                continue
            write = 250 * action.m[i] if channel in (0, 1) else 0
            q_bias = 100 * action.q[i] if channel == 0 or (regime == "COMMON_BIAS" and after["t"] - 1 >= 6) else 0
            people.append([clip(after["X"][i] + write + noise[channel][i][0]),
                           clip(after["Y"][i] + write + q_bias + noise[channel][i][1])])
        raw.append(people)
    return raw


def points(raw, G):
    if G in (0, 2):
        return raw[G]
    if G != 1:
        raise ValueError("Unknown estimator")
    return [[None, None] if raw[0][i][0] is None else
            [sorted(raw[c][i][j] for c in range(3))[1] for j in range(2)] for i in range(8)]


def score(raw, G, objective):
    values = points(raw, G)
    if objective == "full_roster_zero":
        values = [[0, 0] if pair[0] is None else pair for pair in values]
    elif objective == "observed":
        values = [pair for pair in values if pair[0] is not None]
    else:
        raise ValueError("Unknown objective")
    if not values:
        return Fraction(-1), Fraction(0)
    return (Fraction(-sum(max(0, 450 - p[1]) for p in values), 1000 * len(values)),
            Fraction(sum(p[0] for p in values), 1000 * len(values)))


def bank(before, catalogue, ids, process, sensor, G, V, regime, objective, noop):
    """Recompute all eight one-step previews and exact rankings, independently."""
    scores, execution = {}, {}
    process, sensor = process.tolist(), sensor.tolist()
    for action_id in ids:
        executed = action_id if not V or permitted(catalogue[action_id]) else noop
        action = catalogue[executed]
        sums = [Fraction(0), Fraction(0)]
        for replicate in range(8):
            after = step(before, action, process[replicate], regime)
            s = score(measurements(after, action, sensor[replicate], regime), G, objective)
            sums[0] += s[0]
            sums[1] += s[1]
        scores[action_id] = (sums[0] / 8, sums[1] / 8)
        execution[action_id] = executed
    winner = max(ids, key=lambda a: (scores[a], a == noop, -a))
    return winner, scores, execution


def endpoints(events):
    if len(events) != 12 or [e["after"]["t"] for e in events] != list(range(1, 13)):
        raise ValueError("Incomplete episode")
    harm = sum(y < 350 for e in events for y in e["after"]["Y"])
    groups = [sum(e["after"]["Y"][i] for e in events for i in indices) / 48000 for indices in (range(4), range(4, 8))]
    return {"B": harm / 96, "L": min(groups), "P": sum(sum(e["after"]["X"]) for e in events) / 96000,
            "Y_A": groups[0], "Y_B": groups[1], "harm_count": harm, "denominator": 96}
