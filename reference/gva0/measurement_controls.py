"""v0.5 measurement controls with exact rational full-roster scoring.

Mean fusion is scored with integer numerators/denominator three, never int(mean).
The only omitted-report substitution occurs in objective evaluation.
"""
from dataclasses import dataclass
from fractions import Fraction
from time import perf_counter, process_time
import secrets
import numpy as np
from .actions import CATALOGUE
from .seeds import tape, rng
from .types import PublicBatch, Estimate, nullable
from .world import transition_arrays


@dataclass(frozen=True)
class MeasurementControl:
    name: str
    source: str
    aggregation: str = "median"
    rho: float = 0.0

    @property
    def acquired_channels(self):
        return 1 if self.source in ("channel0", "channel2", "copies0") else 3

    @property
    def channel_ids(self):
        return (0,) if self.source == "channel0" else ((2,) if self.source == "channel2" else (0, 1, 2))


CONTROLS = {
    "channel0": MeasurementControl("channel0", "channel0"),
    "median": MeasurementControl("median", "distinct"),
    "channel2": MeasurementControl("channel2", "channel2"),
    "copies0": MeasurementControl("copies0", "copies0"),
    "repeat0": MeasurementControl("repeat0", "repeat0"),
    "rho90": MeasurementControl("rho90", "distinct", rho=.9),
    "mean": MeasurementControl("mean", "distinct", "mean"),
}


def physical_model(live_regime, preview_mode):
    if preview_mode not in ("faithful", "nominal"):
        raise ValueError("Explicit preview mode must be faithful or nominal")
    return "NOMINAL" if preview_mode == "nominal" else live_regime


def measurements(coords, actions, sensor, regime, time, control, remove_q_bias=False):
    """Generate only acquired sensors; copying is separately counted as exposure."""
    fields = np.array([a.key for a in actions]).reshape(-1, 4, 8)
    q, m, e = fields[:, 0], fields[:, 2], fields[:, 3]
    report_q = np.zeros_like(q) if remove_q_bias else q
    if control.source in ("channel0", "copies0", "repeat0"):
        count = 3 if control.source == "repeat0" else 1
        bias = np.repeat((250 * m[:, None, :, None]), 2, axis=-1)
        bias = np.repeat(bias, count, axis=1)
        bias[..., 1] += 100 * report_q[:, None]
        errors = sensor[:, :count]
    elif control.source == "channel2":
        bias = np.zeros((len(actions), 1, 8, 2), dtype=int)
        if regime == "COMMON_BIAS" and time >= 6:
            bias[:, 0, :, 1] = 100 * report_q
        errors = sensor[:, 2:3]
    elif control.source == "distinct":
        bias = np.zeros((len(actions), 3, 8, 2), dtype=int)
        bias[:, :2] += 250 * m[:, None, :, None]
        bias[:, 0, :, 1] += 100 * report_q
        if regime == "COMMON_BIAS" and time >= 6:
            bias[:, 1:, :, 1] += 100 * report_q[:, None]
        errors = sensor
    else:
        raise ValueError("Unknown source")
    raw = np.clip(coords[:, :, None] + bias[:, None] + errors[None], 0, 1000).astype(float)
    residual = raw - np.clip(coords[:, :, None] + bias[:, None], 0, 1000)
    if control.source == "copies0":
        raw, residual = np.repeat(raw, 3, axis=2), np.repeat(residual, 3, axis=2)
    mask = e[:, None, None, :, None].astype(bool)
    return np.where(mask, np.nan, raw), np.where(mask, np.nan, residual)


def rational_points(raw, control):
    missing = np.isnan(raw).all(axis=-3)
    safe = np.nan_to_num(raw, nan=0).astype(np.int64)
    if control.aggregation == "mean":
        return safe.sum(axis=-3), raw.shape[-3], missing
    if control.aggregation != "median":
        raise ValueError("Unknown aggregation")
    return np.median(safe, axis=-3).astype(np.int64), 1, missing


def full_roster_scores(raw, control):
    numerators, d, missing = rational_points(raw, control)
    safe = np.where(missing, 0, numerators)
    deficit = np.maximum(0, 450 * d - safe[..., 1]).sum(axis=-1)
    production = safe[..., 0].sum(axis=-1)
    return tuple(tuple((Fraction(-int(deficit[a, r]), 8000 * d), Fraction(int(production[a, r]), 8000 * d))
                       for r in range(raw.shape[1])) for a in range(raw.shape[0]))


def point_values(raw, control):
    numerator, denominator, missing = rational_points(raw, control)
    return np.where(missing, np.nan, numerator / denominator)


def visible_estimate(raw, control, widths):
    points = point_values(raw, control)
    intervals = np.clip(np.stack((points - widths, points + widths), axis=-1), 0, 1000)
    return Estimate(nullable(points), nullable(intervals), tuple(np.isnan(points[:, 0])), nullable(raw),
                    "v0.5:" + control.name, nullable(np.max(raw, axis=0) - np.min(raw, axis=0)))


def calibrate_controls():
    g = rng("calibration", "v0.5-controls")
    coords = g.integers(300, 801, (2000, 8, 2))
    common = g.choice((-20, 0, 20), (2000, 1, 8, 2))
    independent = g.choice((-20, 0, 20), (2000, 3, 8, 2))
    uniforms = g.random((2000, 1, 8, 2))
    result = {}
    for name, c in CONTROLS.items():
        noise = np.where(uniforms < c.rho, common, independent)
        raw, _ = measurements(coords[None], (CATALOGUE[0],), noise, "NOMINAL", 0, c)
        numerators, d, _ = rational_points(raw[0], c)
        errors = np.max(np.abs(numerators - d * coords), axis=1)
        # Finite calibration rank ceil((2000+1)*.9)=1801; round widths upward to integer.
        widths = (np.sort(errors, axis=0)[1800] + d - 1) // d
        result[name] = {"states": 2000, "rank": 1801, "half_widths": widths.tolist(),
                        "coverage": np.mean(errors <= widths * d, axis=0).tolist(), "rounding": "conservative integer ceiling"}
    return result


class ControlledPreview:
    def __init__(self, state, root, live_regime, control, V, gate, widths, preview_mode="faithful", remove_q_bias=False, namespace="pilot"):
        self._state, self._root, self._live_regime = state, root, live_regime
        self._namespace = namespace
        self.control, self.V, self.gate = CONTROLS[control], V, gate
        self._physics = physical_model(live_regime, preview_mode)
        self._remove_q_bias = remove_q_bias
        self.widths = np.asarray(widths)
        self.token = secrets.token_hex(16)
        self.query_count = self.measurement_count = self.exposed_count = 0
        self.seconds = self.cpu_seconds = 0.0

    def batch(self, ids, token):
        if token != self.token or len(set(ids)) != len(ids):
            raise ValueError("Invalid capability or repeated candidate")
        started, cpu = perf_counter(), process_time()
        gates = tuple(self.gate(a, enabled=self.V) for a in ids)
        actions = tuple(CATALOGUE[g.executed_action_id] for g in gates)
        process, sensor = tape(self._root, self._state.t, "preview", self.control.rho, self._namespace)
        coords = transition_arrays(self._state, actions, process, self._physics)
        raw, _ = measurements(coords, actions, sensor, self._live_regime, self._state.t, self.control, self._remove_q_bias)
        points = point_values(raw, self.control)
        intervals = np.clip(np.stack((points - self.widths, points + self.widths), axis=-1), 0, 1000)
        result = PublicBatch(tuple(ids), raw, self.control.channel_ids, points, intervals,
            np.max(raw, axis=2) - np.min(raw, axis=2), np.array([a.e for a in actions], dtype=bool),
            gates, full_roster_scores(raw, self.control), provenance="v0.5:" + self.control.name)
        self.query_count += 8 * len(ids)
        self.measurement_count += 8 * len(ids) * self.control.acquired_channels * 16
        self.exposed_count += 8 * len(ids) * len(self.control.channel_ids) * 16
        self.seconds += perf_counter() - started
        self.cpu_seconds += process_time() - cpu
        return result
