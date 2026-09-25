"""Verify descriptive review arithmetic and prospective GVA-1 commitments."""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,math,statistics

BASE=Path(__file__).resolve().parents[1]
def load(name):return json.loads((BASE/name).read_text(encoding='utf-8'))
def seed(key):return int.from_bytes(hashlib.sha256(json.dumps(key,separators=(',',':')).encode()).digest()[:16],'little')
def keys(namespace,roots):
    for root in roots:
        yield (namespace,root,'initial')
        for time in range(12):
            yield (namespace,root,time,'candidate-permutation')
            for kind in ('live','preview'):
                for stream in ('process','sensor'):yield(namespace,root,time,kind,stream)

def main():
    old=load('results/gva0/metrics.json')
    oldindex={(r['root_seed'],r['control'],r['V'],r['K'],r['regime'],r['preview_mode']):r for r in old}
    for root in range(1000001,1000021):
        for K in (4,48):
            faithful=oldindex[root,'channel0',1,K,'PHYSICAL_SHIFT','faithful']
            nominal=oldindex[root,'channel0',1,K,'PHYSICAL_SHIFT','nominal']
            for metric in ('B','L','P','legal_repeat_rate'):assert faithful[metric]==nominal[metric]
        for g,m in (('NOMINAL','faithful'),('PHYSICAL_SHIFT','nominal')):
            diff=oldindex[root,'channel0',1,48,g,m]['legal_repeat_rate']-oldindex[root,'channel0',1,4,g,m]['legal_repeat_rate']
            if g=='NOMINAL':saved=diff
            else:assert diff==saved
    rows=load('results/review-v0.5.1/root-metrics.json')
    assert len(rows)==1120
    lookup={(r['root_seed'],r['control'],r['V'],r['regime'],r['K']):r for r in rows}
    assert len(lookup)==1120
    assert not sum(r['executed_violations'] for r in rows if r['V'])
    assert sum(r['queries'] for r in rows)==1704960
    for r in rows:
        assert sum(r['action_counts'].values())==12
        assert r['queries']==12*r['K']*8
        assert math.isclose(r['B'],r['harm_count']/96)
    did=list(csv.DictReader((BASE/'results/review-v0.5.1/channel-did-roots.csv').open()))
    for row in did:
        root,g,m=int(row['root_seed']),row['regime'],row['metric']
        expected=sum(sign*(lookup[root,c,1,g,48][m]-lookup[root,c,1,g,4][m]) for c,sign in (('channel0',1),('channel2',-1)))
        assert abs(float(row['difference'])-expected)<1e-14
    commitment=load('gva1-preregistration/COMMITMENT.json')
    for name,expected in commitment['files'].items():
        assert hashlib.sha256((BASE/'gva1-preregistration'/name).read_bytes()).hexdigest()==expected,name
    manifest=load('gva1-preregistration/SEED-COMMITMENT.json')
    assert manifest['roots']==list(range(4000001,4000146))
    new=[seed(k) for k in keys(manifest['namespace'],manifest['roots'])]
    assert len(new)==len(set(new))==8845
    digest=hashlib.sha256(json.dumps([str(s) for s in new],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest==manifest['seed_list_sha256']
    excluded=list(keys('pilot',range(1,41)))+list(keys('gva0-confirm-v0.5-displacement',range(1000001,1000021)))+list(keys('gva1-development-repair-v0.1',range(3000001,3000041)))
    excluded+=[('development-fixed-bank-v0.4',r) for r in range(1,41)]+[('calibration','v0.1'),('calibration','v0.5-controls')]
    excluded+=[('gva0-confirm-v0.5-displacement',r,time,'live',stream) for r in range(1000001,1000021) for time in range(12,16) for stream in ('process','sensor')]
    assert set(new).isdisjoint(map(seed,excluded))
    print(json.dumps(dict(status='VERIFIED',review_episodes=1120,duplicated_R_vector_verified=True,primary_preview_invariance_verified=True,
                         new_GVA1_roots=145,disjoint_GVA1_stream_seeds=8845,confirmation_outcomes_generated=0)))

if __name__=='__main__':main()
