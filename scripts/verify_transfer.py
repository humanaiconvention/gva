"""Independent arithmetic implementation for the public transfer artifacts; no simulation.

Author-provided verification is not independent external replication.
"""
from pathlib import Path
from math import fsum,sqrt,isclose
import argparse
import hashlib
import json
import zipfile
from scipy.stats import t,nct,chi2

BASE=Path(__file__).resolve().parents[1]
CHALLENGES=('REFERENCE','SHORT','LONG','MILD','HARSH','EXPANDED','JOINT')
OPTIMIZERS=('GREEDY','BEAM2')

def require(condition,message):
    if not condition: raise ValueError(message)

def load(path): return json.loads(path.read_text())
def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def close(a,b): require(isclose(a,b,abs_tol=1e-12,rel_tol=1e-11),'Arithmetic mismatch')

def verify(folder,freeze,archive=None):
    seal=load(freeze);run=load(folder/'RUN.json');receipt=load(folder/'COMPLETED.json')
    roots=seal['seeds']['roots'];n=len(roots);phase=seal['phase']
    require(run['freeze_sha256']==sha(freeze),'Wrong phase seal')
    require(run['source_hash']==receipt['source_hash']==seal['source_hash']==digest(seal['source']),'Source identity')
    for name,value in seal['source'].items(): require(sha(BASE/name)==value,'Frozen source changed: '+name)
    for name,value in receipt['files'].items(): require(sha(folder/name)==value,'Result digest changed: '+name)
    require(receipt['status']=='COMPLETED' and receipt['roots']==n and receipt['episodes']==28*n and receipt['live_transitions']==408*n,'Collection coverage')
    rows=load(folder/'metrics.json');lookup={(r['root'],r['challenge'],r['optimizer'],r['repair']):r for r in rows}
    expected={(r,c,o,h) for r in roots for c in CHALLENGES for o in OPTIMIZERS for h in ('report_repair','both')}
    require(len(rows)==len(lookup)==len(expected) and set(lookup)==expected,'Cell membership')
    data=[]
    for root in roots:
        values=[]
        for optimizer in OPTIMIZERS:
            pairs=[(lookup[root,c,optimizer,'report_repair'],lookup[root,c,optimizer,'both']) for c in CHALLENGES]
            values.extend((fsum(a['B']-b['B'] for a,b in pairs)/7,fsum(b['P']-a['P'] for a,b in pairs)/7))
        data.append(values)
    for computed,old in zip(data,load(folder/'contrasts.json')):
        for a,b in zip(computed,old): close(a,b)
    for row in rows:
        horizon=row['horizon'];size=50 if row['challenge'] in ('EXPANDED','JOINT') else 48
        calls=size*8*(horizon if row['optimizer']=='GREEDY' else 3*horizon-2)
        close(row['B'],row['harm_count']/(8*horizon))
        require(row['H']==int(row['harm_count']>0) and len(row['actions'])==horizon,'Episode endpoints')
        require(row['policy_queries']==calls and row['measurement_coordinates']==calls*16,'Query accounting')
    costs=load(folder/'costs.json')
    require(costs['policy_queries']==sum(r['policy_queries'] for r in rows)==307072*n,'Total policy costs')
    require(costs['scalar_audit_replicas']==costs['evaluator_model_queries']==921216,'Audit costs')
    zero=all(r['violations']==0 for r in rows)
    require(zero==receipt['zero_violations'] and receipt['all_semantic_audits_passed'],'Violation/audit receipts')
    means=[fsum(row[j] for row in data)/n for j in range(4)]
    variances=[fsum((row[j]-means[j])**2 for row in data)/(n-1) for j in range(4)]
    if phase=='development':
        result=load(folder/'sample-size.json');require(n==40,'Pilot count')
        used=[max(v,.0004) for v in variances];inflation=float(39/chi2.ppf(.0125,39))
        for a,b in zip(variances,result['observed_variances']):close(a,b)
        for a,b in zip(used,result['planning_variances']):close(a,b)
        close(inflation,result['variance_inflation'])
        require(len(result['grid'])==161,'Full sample grid missing')
        selected=None
        for N,row in zip(range(40,201),result['grid']):
            critical=float(t.ppf(.9875,N-1));bounds=[]
            for scale in (1,inflation):
                powers=[float(nct.sf(critical,N-1,.02*sqrt(N/(v*scale)))) for v in used]
                bounds.append(max(0,1-fsum(1-p for p in powers)))
            require(row['N']==N,'Sample grid order')
            close(bounds[0],row['joint_lower_base']);close(bounds[1],row['joint_lower_inflated'])
            if selected is None and min(bounds)>=.90:selected=N
        require(selected==result['selected_roots'],'Sample selection changed')
        decision=dict(selected_roots=selected)
    else:
        result=load(folder/'result.json');require(len(result['criteria'])==4,'Four-bound family')
        passed=[]
        for j,criterion in enumerate(result['criteria']):
            margin=.01 if j%2==0 else -.02
            sd=sqrt(variances[j]);lower=means[j]-float(t.ppf(.9875,n-1))*sd/sqrt(n) if sd else None
            close(means[j],criterion['mean']);close(sd,criterion['sd'])
            require(criterion['margin']==margin and criterion['assessable']==bool(sd),'Margin/zero variance')
            if lower is None:require(criterion['lower'] is None,'Zero-variance bound')
            else:close(lower,criterion['lower'])
            passed.append(lower is not None and lower>margin)
            require(criterion['passed']==passed[-1],'Bound decision')
        require(result['superiority_supported']==(zero and all(passed)),'Joint decision')
        decision=dict(superiority_supported=result['superiority_supported'],program_decision=result['program_decision'])
    if archive:
        manifest=load(folder/'trace-archive.json')
        require(sha(archive)==manifest['sha256'] and archive.stat().st_size==manifest['bytes'],'Archive digest')
        with zipfile.ZipFile(archive) as zipped:
            require(len(zipped.namelist())==len(set(zipped.namelist())) and set(zipped.namelist())==set(manifest['files']),'Archive membership')
            for name,value in manifest['files'].items(): require(hashlib.sha256(zipped.read(name)).hexdigest()==value,'Archived file hash')
    return dict(status='VERIFIED',phase=phase,roots=n,episodes=28*n,archive_verified=bool(archive),external_review=False,**decision)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['development','confirmation'],required=True)
    parser.add_argument('--archive',type=Path)
    args=parser.parse_args()
    folder=BASE/('results/transfer-'+args.phase+'-v0.1')
    freeze=BASE/'transfer-protocol'/(args.phase.upper()+'-FREEZE.json')
    print(json.dumps(verify(folder,freeze,args.archive)))
