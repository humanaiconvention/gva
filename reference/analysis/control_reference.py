"""Independent scalar semantics for the v0.5 measurement interventions."""
from fractions import Fraction
from .scalar_reference import clip, step, permitted
from gva0.actions import CATALOGUE, NOOP


def reports(after, action, noise, regime, time, name):
    originals = [0] if name == "channel0" else ([2] if name == "channel2" else [0, 1, 2])
    result = []
    for position, channel in enumerate(originals):
        source = 0 if name in ("copies0", "repeat0") else channel
        noise_channel = 0 if name == "copies0" else channel
        people = []
        for i in range(8):
            if action.e[i]:
                people.append([None, None])
            else:
                write = 250 * action.m[i] if source in (0, 1) else 0
                qbias = 100 * action.q[i] if source == 0 or (regime == "COMMON_BIAS" and time >= 6) else 0
                people.append([clip(after["X"][i] + write + noise[noise_channel][i][0]),
                               clip(after["Y"][i] + write + qbias + noise[noise_channel][i][1])])
        result.append(people)
    return result


def score(raw, name):
    points = []
    for i in range(8):
        if raw[0][i][0] is None:
            points.append([Fraction(0), Fraction(0)])
        elif name == "mean":
            points.append([Fraction(sum(c[i][j] for c in raw), len(raw)) for j in (0, 1)])
        else:
            points.append([Fraction(sorted(c[i][j] for c in raw)[len(raw) // 2]) for j in (0, 1)])
    return (-sum((max(Fraction(0), 450 - p[1]) for p in points), Fraction(0)) / 8000,
            sum((p[0] for p in points), Fraction(0)) / 8000)


def candidate_scores(before, root, ids, name, V, regime, preview_mode, process, sensor):
    output = {}
    physics = "NOMINAL" if preview_mode == "nominal" else regime
    for a in ids:
        action = CATALOGUE[a if not V or permitted(CATALOGUE[a]) else NOOP]
        sums = [Fraction(0), Fraction(0)]
        for r in range(8):
            after = step(before, action, process[r].tolist(), physics)
            s = score(reports(after, action, sensor[r].tolist(), regime, before["t"], name), name)
            for j in (0, 1):
                sums[j] += s[j]
        output[a] = tuple(x / 8 for x in sums)
    return output
