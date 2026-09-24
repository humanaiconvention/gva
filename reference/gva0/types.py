from dataclasses import dataclass
from fractions import Fraction
from typing import NamedTuple
import numpy as np

IDS = tuple(range(8))
GROUPS = ("A",) * 4 + ("B",) * 4
ZERO = (0,) * 8


@dataclass(frozen=True)
class Action:
    q: tuple[int, ...] = ZERO
    u: tuple[int, ...] = ZERO
    m: tuple[int, ...] = ZERO
    e: tuple[int, ...] = ZERO

    def __post_init__(self):
        for name, high in (("q", 2), ("u", 1), ("m", 1), ("e", 1)):
            v = getattr(self, name)
            if type(v) is not tuple or len(v) != 8 or any(type(x) is not int or not 0 <= x <= high for x in v):
                raise ValueError(f"Invalid action field {name}")

    @property
    def key(self):
        return self.q + self.u + self.m + self.e


@dataclass(frozen=True)
class WorldState:
    t: int
    X: tuple[int, ...]
    Y: tuple[int, ...]
    q_prev: tuple[int, ...] = ZERO
    ids: tuple[int, ...] = IDS
    groups: tuple[str, ...] = GROUPS

    def __post_init__(self):
        if self.ids != IDS or self.groups != GROUPS or not 0 <= self.t <= 12:
            raise ValueError("Invalid administrative state or time")
        for v in (self.X, self.Y):
            if len(v) != 8 or any(type(x) is not int or not 0 <= x <= 1000 for x in v):
                raise ValueError("Invalid coordinates")
        if len(self.q_prev) != 8 or any(type(x) is not int or not 0 <= x <= 2 for x in self.q_prev):
            raise ValueError("Invalid previous production")


@dataclass(frozen=True)
class AdminState:
    ids: tuple[int, ...] = IDS
    groups: tuple[str, ...] = GROUPS
    contract_version: str = "GVA-0-v0.1-contract"


@dataclass(frozen=True)
class GateResult:
    proposed_action_id: int | None
    executed_action_id: int
    allowed: bool
    reason_codes: tuple[str, ...]
    contract_hash: str


@dataclass(frozen=True)
class ActorObservations:
    # None is the serialized missing marker. Arrays use NaN internally only.
    values: tuple
    channels: tuple[int, ...]
    missing: tuple[bool, ...]
    roster: tuple[int, ...] = IDS
    provenance: str = "synthetic-report-pipeline-v0.1"


@dataclass(frozen=True)
class Estimate:
    mean_or_median: tuple
    intervals: tuple
    missing: tuple[bool, ...]
    channel_values: tuple
    provenance: str
    disagreement: tuple


@dataclass(frozen=True)
class PreviewResult:
    observation: ActorObservations
    estimate: Estimate
    rational_score: tuple[Fraction, Fraction]
    gate_result: GateResult


@dataclass(frozen=True)
class PublicBatch:
    action_ids: tuple
    channel_values: np.ndarray
    channel_ids: tuple
    points: np.ndarray
    intervals: np.ndarray
    disagreement: np.ndarray
    missing: np.ndarray
    gate_results: tuple
    scores: tuple
    roster: tuple = IDS
    provenance: str = "synthetic-report-pipeline-v0.1"


@dataclass(frozen=True)
class EstimatorConfig:
    grounding: int
    half_widths: tuple[int, int] = (20, 20)


class EpisodeMetrics(NamedTuple):
    B: float
    L: float
    P: float
    Y_A: float
    Y_B: float
    harm_count: int
    denominator: int


def nullable(a):
    if isinstance(a, np.ndarray):
        return nullable(a.tolist())
    if isinstance(a, (list, tuple)):
        return tuple(nullable(v) for v in a)
    return None if isinstance(a, float) and np.isnan(a) else a
