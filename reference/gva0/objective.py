from fractions import Fraction


def rank_score(estimate, inclusion_mask, mode="observed"):
    if mode not in ("observed", "full_roster_zero"):
        raise ValueError("Unknown objective mode")
    points = estimate.mean_or_median
    if mode == "full_roster_zero":
        # Decision-rule substitutions only: leave Estimate and its missing values intact.
        complete = [(0, 0) if estimate.missing[i] else points[i] for i in range(8)]
        return (Fraction(-sum(max(0, 450 - int(p[1])) for p in complete), 8000),
                Fraction(sum(int(p[0]) for p in complete), 8000))
    indices = [i for i, include in enumerate(inclusion_mask) if include and not estimate.missing[i]]
    if not indices:
        return Fraction(-1), Fraction(0)
    denominator = len(indices) * 1000
    deficit = sum(max(0, 450 - int(points[i][1])) for i in indices)
    production = sum(int(points[i][0]) for i in indices)
    return Fraction(-deficit, denominator), Fraction(production, denominator)


def average_scores(scores):
    return tuple(sum((s[j] for s in scores), Fraction(0)) / len(scores) for j in (0, 1))
