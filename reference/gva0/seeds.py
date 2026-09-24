"""Named tapes: no action, architecture, K, or regime enters a random key."""
from functools import lru_cache
from hashlib import sha256
import json
import numpy as np
from .actions import NOOP


def seed_value(*key):
    raw = json.dumps(key, separators=(",", ":")).encode()
    return int.from_bytes(sha256(raw).digest()[:16], "little")


def rng(*key):
    return np.random.Generator(np.random.PCG64(seed_value(*key)))


@lru_cache(maxsize=256)
def tape(root, time, kind, rho=0.0, namespace="pilot"):
    # Fixed shape indexes replicate, individual, coordinate. Live has one replicate.
    r = 8 if kind == "preview" else 1
    process = rng(namespace, root, time, kind, "process").choice((-5, 0, 5), (r, 8, 2), p=(.25, .5, .25))
    generator = rng(namespace, root, time, kind, "sensor")
    common = generator.choice((-20, 0, 20), (r, 1, 8, 2))
    independent = generator.choice((-20, 0, 20), (r, 3, 8, 2))
    b = generator.random((r, 1, 8, 2)) < rho
    sensor = np.where(b, common, independent)
    process.flags.writeable = False
    sensor.flags.writeable = False
    return process, sensor


def candidates(root, time, K, namespace="pilot"):
    if K not in (4, 16, 48):
        raise ValueError("Unsupported search pressure")
    rest = [i for i in range(48) if i != NOOP]
    order = rng(namespace, root, time, "candidate-permutation").permutation(rest)
    return (NOOP,) + tuple(int(x) for x in order[:K - 1])
