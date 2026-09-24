from dataclasses import dataclass, asdict
from hashlib import sha256
import json


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Config:
    protocol: str = "GVA-0-v0.1"
    n: int = 8
    horizon: int = 12
    replicates: int = 8
    rho: float = 0.0
    calibration_states: int = 2000
    phase: str = "pilot"

    def __post_init__(self):
        if (self.n, self.horizon, self.replicates, self.calibration_states) != (8, 12, 8, 2000):
            raise ValueError("Core protocol constants are frozen")
        if self.phase != "pilot" or self.rho != 0:
            raise ValueError("Core entry point permits only the specified nominal-sensor pilot")

    @property
    def hash(self):
        return digest(asdict(self))


REGIMES = ("NOMINAL", "PHYSICAL_SHIFT", "COMMON_BIAS")
