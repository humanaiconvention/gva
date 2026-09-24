import numpy as np
from .types import WorldState
from .config import REGIMES
from .seeds import rng


def initial_state(root, namespace="pilot"):
    g = rng(namespace, root, "initial")
    lo = np.array([[500, 550]] * 4 + [[350, 450]] * 4)
    coords = g.integers(lo, lo + 151)
    return WorldState(0, tuple(map(int, coords[:, 0])), tuple(map(int, coords[:, 1])))


def transition_arrays(state, actions, noise, regime):
    """Vectorized exact transition, output shape (actions, replicates, IDs, XY)."""
    if state.t >= 12:
        raise ValueError("Terminal horizon")
    if regime not in REGIMES:
        raise ValueError("Unknown evaluator regime")
    fields = np.array([a.key for a in actions], dtype=np.int64).reshape(-1, 4, 8)
    q, u, m, e = (fields[:, j, None, :] for j in range(4))
    fatigue = 40 if regime == "PHYSICAL_SHIFT" and state.t >= 6 else 20
    x = np.array(state.X) + 60 * q + 30 * u - 10 + noise[None, :, :, 0]
    y = np.array(state.Y) + 40 * u - 40 * q ** 2 - fatigue * q * np.array(state.q_prev) - 15 * m - 20 * e + noise[None, :, :, 1]
    return np.clip(np.stack((x, y), axis=-1), 0, 1000)


def transition(state, action, process_noise, regime="NOMINAL"):
    next_values = transition_arrays(state, (action,), np.asarray(process_noise).reshape(1, 8, 2), regime)[0, 0]
    return WorldState(state.t + 1, tuple(map(int, next_values[:, 0])), tuple(map(int, next_values[:, 1])), action.q)
