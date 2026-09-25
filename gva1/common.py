from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os

class AuditFailure(RuntimeError):
    """A semantic/integrity failure invalidates a run instead of permitting retry."""

class InfrastructureFailure(RuntimeError):
    """An interrupted computation may resume from verified whole-root commits."""

def require(condition, message):
    if not condition:
        raise AuditFailure(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def utc():
    return datetime.now(timezone.utc).isoformat()

def atomic_json(path, value):
    path = Path(path)
    pending = path.with_name(path.name + '.pending')
    with pending.open('wb') as stream:
        stream.write(canonical(value) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(pending, path)

def journal(path, value):
    with Path(path).open('ab') as stream:
        stream.write(canonical(value) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
