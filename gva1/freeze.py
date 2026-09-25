"""Prospective source/runtime seal, created after development-only validation."""
from pathlib import Path
import os
import platform
import sys
import numpy
import scipy
import z3
from . import ROOT
from .common import atomic_json, digest, read, require, sha, utc
from .design import PROTOCOL, verify_inputs, confirmation

def source_files():
    paths = list((ROOT / 'gva1').glob('*.py')) + list((ROOT / 'tests/gva1').glob('*.py'))
    paths += list((ROOT / 'tests/gva1').glob('*.json'))
    paths += [ROOT / name for name in read(ROOT / 'provenance/published-core-map.json')]
    paths += [PROTOCOL / name for name in read(PROTOCOL / 'COMMITMENT.json')['files']]
    paths += [PROTOCOL / 'COMMITMENT.json', ROOT / 'requirements-replay.txt']
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(paths))}

def runtime():
    return dict(python=sys.version, python_executable_sha256=sha(sys.executable), numpy=numpy.__version__,
        scipy=scipy.__version__, z3=z3.get_version_string(), platform=platform.platform(),
        machine=platform.machine(), processor=platform.processor(), logical_cpus=os.cpu_count())

def validate_freeze(path):
    record = read(path)
    verify_inputs()
    require(record['status'] == 'EXECUTION_READY_NOT_STARTED', 'Execution freeze not ready')
    require(record['confirmation_outcomes_generated'] == 0, 'Freeze not prospective')
    require(record['files'] == source_files(), 'Execution source changed since freeze')
    require(record['source_hash'] == digest(record['files']), 'Invalid aggregate source hash')
    require(record['runtime'] == runtime(), 'Runtime differs from execution freeze')
    require(record['design'] == confirmation().record(), 'Frozen design mismatch')
    require(record['preflight']['source_hash'] == record['source_hash'], 'Preflight used different code')
    require(record['preflight']['status'] == 'PASSED' and record['preflight']['episodes_matched'] == 640, 'Full development preflight required')
    require(record['preflight']['adversarial_tests']['passed'], 'Adversarial checks missing')
    return record

def create_freeze(path, preflight_path):
    path = Path(path)
    require(not path.exists(), 'Do not overwrite an execution freeze')
    verify_inputs()
    report = read(preflight_path)
    files = source_files()
    require(report['source_hash'] == digest(files), 'Preflight source changed; rerun validation')
    require(report['status'] == 'PASSED' and report['episodes_matched'] == 640, 'Preflight incomplete')
    require(report['adversarial_tests']['passed'], 'Test suite failed')
    require(report['runtime'] == runtime(), 'Preflight runtime changed')
    record = dict(status='EXECUTION_READY_NOT_STARTED', utc=utc(), design=confirmation().record(),
        files=files, source_hash=digest(files), runtime=runtime(), preflight=report,
        preflight_sha256=sha(preflight_path), confirmation_outcomes_generated=0,
        scope='Local cryptographic commitment; public version control supplies publication timestamp. External review remains separate.')
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(path, record)
    validate_freeze(path)
    return record
