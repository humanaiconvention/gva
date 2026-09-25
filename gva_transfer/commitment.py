from pathlib import Path
from itertools import product
from gva0.seeds import seed_value
from gva1.common import read,sha,digest,atomic_json,utc
from gva1.freeze import runtime,validate_freeze
from . import ROOT
from .design import record,phase_design
from .model import require

def source():
    original=read(ROOT/'gva1-execution-v0.1/FREEZE.json')
    for name,value in original['files'].items(): require(sha(ROOT/name)==value,'Original frozen file changed')
    paths=[ROOT/name for name in original['files']]
    paths+=list((ROOT/'gva_transfer').glob('*.py'))+list((ROOT/'tests/transfer').glob('*.py'))
    paths+=[ROOT/'transfer-protocol/PREREGISTRATION.md']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))}

def seed_keys(namespace,roots):
    for root in roots:
        yield namespace,root,'initial'
        for time,kind,stream in product(range(24),('live','preview','preview-depth-2'),('process','sensor')):
            yield namespace,root,time,kind,stream

def seeds(phase,n=None):
    namespace,roots=phase_design(phase,n)
    values=[seed_value(*key) for key in seed_keys(namespace,roots)]
    require(len(values)==len(set(values))==145*len(roots),'Within-phase seed collision')
    excluded=[]
    for ns,rs in (('pilot',range(1,41)),('gva0-confirm-v0.5-displacement',range(1000001,1000021)),
                  ('gva1-development-repair-v0.1',range(3000001,3000041)),('gva1-confirm-repair-v0.1',range(4000001,4000146))):
        excluded.extend(seed_value(*key) for key in seed_keys(ns,rs))
        excluded.extend(seed_value(ns,r,t,'candidate-permutation') for r in rs for t in range(24))
    excluded.extend(seed_value('development-fixed-bank-v0.4',r) for r in range(1,41))
    excluded.extend([seed_value('calibration','v0.1'),seed_value('calibration','v0.5-controls')])
    if phase=='confirmation': excluded.extend(seed_value(*key) for key in seed_keys(*phase_design('development')))
    require(set(values).isdisjoint(excluded),'Historical/development seed collision')
    return dict(namespace=namespace,roots=list(roots),stream_count=len(values),stream_seed_digest=digest([str(v) for v in values]),
        collision_checked=True,derivation='gva0.seeds.seed_value; initial and 24 times x 3 kinds x 2 named streams; see seed_keys')

def freeze(phase,output,validation_path,sample_path=None):
    require(not Path(output).exists(),'Never overwrite a freeze')
    validation=read(validation_path)
    files=source();require(validation['status']=='PASSED' and validation['source_hash']==digest(files),'Validated source required')
    require(validation['runtime']==runtime(),'Validation runtime mismatch')
    plan=read(sample_path) if sample_path else None
    if phase=='confirmation': require(plan is not None and plan['selected_roots'] is not None,'Feasible calculated sample required')
    n=plan['selected_roots'] if plan else None
    value=dict(utc=utc(),phase=phase,source=files,source_hash=digest(files),runtime=runtime(),design=record(),
        seeds=seeds(phase,n),validation=validation,sample=plan,sample_sha256=sha(sample_path) if sample_path else None,
        status='FROZEN_BEFORE_PHASE_OUTCOMES',external_review=False)
    atomic_json(Path(output),value);return value

def verify(path,phase):
    value=read(path)
    require(value['phase']==phase and value['status']=='FROZEN_BEFORE_PHASE_OUTCOMES','Wrong phase freeze')
    require(value['source']==source() and value['source_hash']==digest(source()),'Source drift')
    require(value['runtime']==runtime() and digest(value['design'])==digest(record()),'Runtime/design drift')
    n=value['sample']['selected_roots'] if phase=='confirmation' else None
    require(value['seeds']==seeds(phase,n),'Seed schedule drift')
    return value
