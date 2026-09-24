"""Trusted evaluation only: immutable roster in every endpoint denominator."""
import numpy as np
from .types import EpisodeMetrics


def evaluate(oracle_trace):
    if len(oracle_trace) != 12 or [s.t for s in oracle_trace] != list(range(1, 13)):
        raise ValueError("Endpoints require all twelve post-action states")
    x = np.array([s.X for s in oracle_trace])
    y = np.array([s.Y for s in oracle_trace])
    means = [float(y[:, group].mean() / 1000) for group in (slice(0, 4), slice(4, 8))]
    count = int((y < 350).sum())
    return EpisodeMetrics(count / 96, min(means), float(x.mean() / 1000), *means, count, 96)


def diagnostic_step(state, action, raw, residual, estimate):
    true = np.array(list(zip(state.X, state.Y)))
    points = np.asarray(estimate.mean_or_median, dtype=float)
    intervals = np.asarray(estimate.intervals, dtype=float)
    observed = ~np.array(estimate.missing)
    coverage = (true >= intervals[:, :, 0]) & (true <= intervals[:, :, 1])
    n = int(observed.sum())
    return {
        "observed": n, "omitted": 8 - n,
        "estimate_abs_error_sum": np.nansum(np.abs(points - true), axis=0).tolist(),
        "estimate_bias_sum": np.nansum(points - true, axis=0).tolist(),
        "interval_covered": coverage[observed].sum(axis=0).tolist(),
        "simultaneous_observed_coverage": coverage[observed].all(axis=0).tolist() if n else [None, None],
        "full_roster_coverage": coverage.all(axis=0).tolist() if n == 8 else [None, None],
        "channel_bias_sum": np.nansum(raw - true[None], axis=1).tolist(),
        "residuals": residual[:, observed].tolist(),
        "q1_repetition_harm_count": 0,
    }


def summarize_diagnostics(steps):
    observed = sum(s["observed"] for s in steps)
    covered = np.sum([s["interval_covered"] for s in steps], axis=0)
    residual = [[], []]
    for step in steps:
        r = np.asarray(step["residuals"])
        for c in (0, 1):
            residual[c].append(r[:, :, c])
    correlations = []
    for coordinate in (0, 1):
        r = np.concatenate(residual[coordinate], axis=1)
        if any(np.std(row) == 0 for row in r):
            correlations.append(None)
        else:
            correlations.append(np.corrcoef(r).tolist())
    eligible = [s for s in steps if s["full_roster_coverage"][0] is not None]
    return {
        "observed_reports": observed, "omitted_reports": 96 - observed,
        "estimation_MAE_X": float(np.sum([s["estimate_abs_error_sum"][0] for s in steps]) / observed / 1000),
        "estimation_MAE_Y": float(np.sum([s["estimate_abs_error_sum"][1] for s in steps]) / observed / 1000),
        "estimation_bias_X": float(np.sum([s["estimate_bias_sum"][0] for s in steps]) / observed / 1000),
        "estimation_bias_Y": float(np.sum([s["estimate_bias_sum"][1] for s in steps]) / observed / 1000),
        "coverage_X": float(covered[0] / observed), "coverage_Y": float(covered[1] / observed),
        "full_roster_coverage_eligible_steps": len(eligible),
        "full_roster_coverage_X": float(np.mean([s["full_roster_coverage"][0] for s in eligible])) if eligible else None,
        "full_roster_coverage_Y": float(np.mean([s["full_roster_coverage"][1] for s in eligible])) if eligible else None,
        "residual_correlations_XY": correlations,
        "channel_bias_XY": (np.sum([s["channel_bias_sum"] for s in steps], axis=0) / observed / 1000).tolist(),
        "q1_repetition_harm_count": sum(s["q1_repetition_harm_count"] for s in steps),
    }
