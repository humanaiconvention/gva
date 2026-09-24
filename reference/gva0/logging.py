"""Append-only, hash-chained event streams with an external manifest anchor."""
from dataclasses import asdict, is_dataclass
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import numpy as np
from .config import digest


def plain(value):
    if is_dataclass(value):
        return plain(asdict(value))
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if isinstance(value, np.ndarray):
        return plain(value.tolist())
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def source_hash(root=None):
    root = Path(root or Path(__file__).resolve().parents[1])
    paths = []
    for folder in ("gva0", "formal", "analysis", "tests", "configs", "preregistration"):
        paths.extend(p for p in (root / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    paths.extend(root / p for p in ("pyproject.toml", "requirements.lock", ".python-version"))
    return digest({p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.exists()})


class EventWriter:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("x", encoding="utf-8")
        self.head = "0" * 64
        self.substantive_head = "0" * 64
        self.count = 0

    def append(self, event):
        value = plain(event)
        value["previous_hash"] = self.head
        substantive = {k: v for k, v in value.items() if k not in ("timing", "previous_hash")}
        self.substantive_head = digest([self.substantive_head, substantive])
        value["substantive_hash"] = self.substantive_head
        value["event_hash"] = digest(value)
        self.file.write(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")
        self.head = value["event_hash"]
        self.count += 1

    def close(self):
        self.file.close()
        return {"events": self.count, "head": self.head, "substantive_head": self.substantive_head}


def verify_stream(path, anchor=None):
    head, substantive_head, count = "0" * 64, "0" * 64, 0
    with Path(path).open(encoding="utf-8") as stream:
        for line in stream:
            value = json.loads(line)
            actual = value.pop("event_hash")
            if value["previous_hash"] != head or digest(value) != actual:
                raise ValueError(f"Modified event {count}")
            substantive = {k: v for k, v in value.items() if k not in ("timing", "previous_hash", "substantive_hash")}
            substantive_head = digest([substantive_head, substantive])
            if value["substantive_hash"] != substantive_head:
                raise ValueError(f"Substantive chain mismatch {count}")
            head, count = actual, count + 1
    result = {"events": count, "head": head, "substantive_head": substantive_head}
    if anchor is not None and result != anchor:
        raise ValueError("External anchor mismatch (including truncation)")
    return result


def write_json(path, value):
    Path(path).write_text(json.dumps(plain(value), indent=2, allow_nan=False) + "\n", encoding="utf-8")
