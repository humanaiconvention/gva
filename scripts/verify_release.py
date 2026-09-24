"""Standard-library checks of published hashes, seed disjointness and statistics."""
from pathlib import Path
from math import fsum,sqrt
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def seed(key):return int.from_bytes(hashlib.sha256(json.dumps(key,separators=(',',':')).encode()).digest()[:16],'little')

def verify():
    hashes=load('provenance/original-source-hashes.json')
    assert hashlib.sha256(canonical(hashes['files'])).hexdigest()==hashes['source_hash']
    core=load('provenance/published-core-map.json')
    for public,original in core.items():assert sha(ROOT/public)==hashes['files'][original],public
    original=load('provenance/FREEZE.original.json')
    result=load('results/gva0/result.json')
    manifest=load('results/gva0/manifest.json')
    assert sha(ROOT/'provenance/FREEZE.original.json')==manifest['hashes']['freeze']
    assert sha(ROOT/'protocol/PREREGISTRATION.original.md')==original['preregistration_sha256']
    assert sha(ROOT/'protocol/seed-manifest.json')==original['files']['seed-manifest.json']
    seeds=load('protocol/seed-manifest.json')
    assert set(seeds['roots']).isdisjoint(range(1,41)) and len(seeds['roots'])==20
    values=set()
    for entry in seeds['streams']:
        assert entry['key'][0]==seeds['namespace']
        value=seed(entry['key']);assert value==int(entry['pcg64_seed']) and value not in values
        values.add(value)
    old=[]
    for root in range(1,41):
        old.append(['pilot',root,'initial']);old.append(['development-fixed-bank-v0.4',root])
        for time in range(12):
            old.append(['pilot',root,time,'candidate-permutation'])
            for kind in ('live','preview'):
                for stream in ('process','sensor'):old.append(['pilot',root,time,kind,stream])
    old.extend([['calibration','v0.1'],['calibration','v0.5-controls']])
    assert values.isdisjoint(map(seed,old))
    rows=load('results/gva0/metrics.json')
    lookup={(r['root_seed'],r['control'],r['V'],r['K'],r['regime'],r['preview_mode']):r for r in rows}
    assert len(lookup)==len(rows)==820
    matrix=[[lookup[root,'channel0',1,48,regime,mode][metric]-lookup[root,'channel0',1,4,regime,mode][metric]
        for regime,mode in (('NOMINAL','faithful'),('PHYSICAL_SHIFT','nominal')) for metric in ('B','legal_repeat_rate')]
        for root in seeds['roots']]
    for j,threshold in enumerate((.05,.20,.05,.20)):
        mean=fsum(r[j] for r in matrix)/20
        sd=sqrt(fsum((r[j]-mean)**2 for r in matrix)/19)
        lower=mean-result['critical_t']*sd/sqrt(20)
        assert abs(lower-result['primary'][j]['lower'])<1e-12
        assert abs(mean-result['primary'][j]['mean'])<1e-12
        assert sd>0 and lower>threshold
    assert not sum(r['executed_violations'] for r in rows if r['V'])
    assert load('results/gva0/audit.json')['all_passed']
    release=ROOT/'RELEASE-MANIFEST.json'
    if release.exists():
        for name,expected in load('RELEASE-MANIFEST.json')['files'].items():assert sha(ROOT/name)==expected,name
    print(json.dumps({'status':'VERIFIED','exact_core_files':len(core),'roots':20,'episodes':820,'stream_seeds':len(values),
                      'joint_criteria':'all four passed','external_replication':False}))

if __name__=='__main__':verify()
