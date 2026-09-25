"""Explicitly post hoc GVA-0 review analyses; never a confirmation rerun."""
from pathlib import Path
from collections import Counter,defaultdict
from dataclasses import replace
from datetime import datetime,timezone
from io import StringIO
from fractions import Fraction
import argparse,csv,hashlib,json,sys
import numpy as np
from scipy.stats import t

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'reference'))
import reproduce as rep
from gva0.types import WorldState
from gva0.seeds import candidates as original_candidates

NAMESPACE='gva0-confirm-v0.5-displacement'
ROOTS=list(range(1000001,1000021))
KS=(1,2,4,8,16,32,48)

def nested(root,time,K,namespace):
    assert K in KS
    return original_candidates(root,time,48,namespace)[:K]

def save(path,value):path.write_text(json.dumps(rep.plain(value),indent=2)+'\n',encoding='utf-8')

def table(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def interval(values):
    a=np.array(values,dtype=float);mean=float(a.mean());sd=float(a.std(ddof=1))
    half=float(t.ppf(.975,len(a)-1)*sd/np.sqrt(len(a)))
    return dict(mean=mean,sd=sd,lower=mean-half,upper=mean+half,roots=len(a))

def scalar_scores(state,process,sensor,remove):
    scores={}
    for aid,action in enumerate(rep.CATALOGUE):
        if not rep.scalar.permitted(action):action=rep.CATALOGUE[0]
        reporting=replace(action,q=(0,)*8) if remove else action
        sums=[Fraction(0),Fraction(0)]
        for r in range(8):
            after=rep.scalar.step(rep.plain(state),action,process[r].tolist(),'NOMINAL')
            s=rep.scalar.score(rep.scalar.measurements(after,reporting,sensor[r].tolist(),'NOMINAL'),0,'full_roster_zero')
            for j in (0,1):sums[j]+=s[j]
        scores[aid]=tuple(s/8 for s in sums)
    return scores

def witnesses(events,gate):
    rows=[]
    for event in events:
        before=event['before'];state=WorldState(before['t'],tuple(before['X']),tuple(before['Y']),tuple(before['q_prev']))
        root,regime=event['root_seed'],event['regime']
        process,sensor=rep.tape(root,state.t,'preview',namespace=NAMESPACE)
        scores=[]
        for remove in (False,True):
            service=rep.ControlledPreview(state,root,regime,'channel0',1,gate,[20,20],'nominal',remove_q_bias=remove,namespace=NAMESPACE)
            batch=service.batch(tuple(range(48)),service.token)
            bank={a:rep.average_scores(s) for a,s in zip(batch.action_ids,batch.scores)}
            assert bank==scalar_scores(state,process,sensor,remove)
            scores.append(bank)
        on,off=[max(range(48),key=lambda a:(b[a],a==0,-a)) for b in scores]
        assert on==event['executed']
        live,_=rep.tape(root,state.t,'live',namespace=NAMESPACE)
        counts=[]
        for aid in (on,off):
            executed=gate(aid).executed_action_id
            after=rep.scalar.step(before,rep.CATALOGUE[executed],live[0].tolist(),regime)
            counts.append(sum(y<350 for y in after['Y']))
        reversal=scores[0][on]>scores[0][off] and scores[1][off]>scores[1][on]
        legal_q1=rep.scalar.permitted(rep.CATALOGUE[on]) and 1 in rep.CATALOGUE[on].q
        rows.append(dict(root_seed=root,regime=regime,time=state.t,on=on,off=off,action_changed=on!=off,
                         strict_reversal=reversal,on_breaches=counts[0],off_breaches=counts[1],
                         witness=legal_q1 and reversal and counts[1]<counts[0]))
    return rows

def sensitivity():
    rows=[]
    for root in ROOTS:
        for regime in ('NOMINAL','PHYSICAL_SHIFT'):
            for offset in (-50,0,50):
                state=rep.plain(rep.initial_state(root,NAMESPACE));state['Y']=[y+(offset if i>=4 else 0) for i,y in enumerate(state['Y'])]
                ys=[]
                for time in range(16):
                    noise,_=rep.tape(root,time,'live',namespace=NAMESPACE)
                    state=rep.scalar.step(state,rep.CATALOGUE[20],noise[0].tolist(),regime);ys.append(state['Y'])
                for horizon in (8,12,16):
                    for threshold in (300,350,400):
                        burden=sum(y<threshold for step in ys[:horizon] for y in step)/(8*horizon)
                        rows.append(dict(root_seed=root,regime=regime,group_B_lower=450+offset,group_B_upper=600+offset,
                                         horizon=horizon,threshold=threshold,B=burden))
    return rows

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__),Path(__file__).with_name('PROTOCOL.md')]
    save(out/'exploratory-commitment.json',dict(utc=datetime.now(timezone.utc).isoformat(),status='POST_HOC_REVIEW',
         files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},roots=ROOTS,
         interpretation='Existing outcomes already known; not prospective confirmation'))
    rep.candidates=nested
    old=json.loads((BASE/'results/gva0/metrics.json').read_text());lookup={(r['root_seed'],r['control'],r['V'],r['K'],r['regime'],r['preview_mode']):r for r in old}
    gate=rep.FormalGate();rows=[];primary=[];overlap=0
    with rep.ActorProcess() as actor:
        for index,root in enumerate(ROOTS):
            for control in ('channel0','channel2'):
                for V in (0,1):
                    for regime in ('NOMINAL','PHYSICAL_SHIFT'):
                        for K in KS:
                            trace=StringIO()
                            row=rep.episode(root,control,V,K,regime,'nominal',NAMESPACE,[20,20],actor,gate,audit=root==ROOTS[0],trace=trace)
                            events=[json.loads(line) for line in trace.getvalue().splitlines()]
                            counts=Counter(e['executed'] for e in events)
                            row.update(noop_fraction=counts[0]/12,action_counts=dict(counts));rows.append(row)
                            key=(root,control,V,K,regime,'faithful' if regime=='NOMINAL' else 'nominal')
                            if key in lookup:
                                for metric in ('B','L','P','Y_A','Y_B','harm_count','legal_repeat_rate','executed_violations','queries'):
                                    assert abs(row[metric]-lookup[key][metric])<1e-12,(key,metric)
                                overlap+=1
                            if control=='channel0' and V==1 and K==48:primary.extend(events)
            print(f'Exploratory sweep roots {index+1}/20',flush=True)
    save(out/'root-metrics.json',rows)
    groups=defaultdict(list)
    for row in rows:groups[row['control'],row['V'],row['regime'],row['K']].append(row)
    summary=[];frequencies=[]
    for (control,V,regime,K),items in groups.items():
        record=dict(control=control,V=V,regime=regime,K=K)
        for metric in ('B','L','P','Y_A','Y_B','legal_repeat_rate','noop_fraction'):record[metric]=float(np.mean([i[metric] for i in items]))
        record['violations']=sum(i['executed_violations'] for i in items);summary.append(record)
        counts=Counter()
        for item in items:counts.update(item['action_counts'])
        for aid,count in sorted(counts.items()):frequencies.append(dict(control=control,V=V,regime=regime,K=K,action=aid,count=count,total=240))
    table(out/'sweep.csv',summary);table(out/'action-frequencies.csv',frequencies)
    index={(r['root_seed'],r['control'],r['V'],r['regime'],r['K']):r for r in rows}
    differences=[];contrasts=[]
    for regime in ('NOMINAL','PHYSICAL_SHIFT'):
        for metric in ('B','legal_repeat_rate','L','P'):
            values=[]
            for root in ROOTS:
                value=sum(sign*(index[root,c,1,regime,48][metric]-index[root,c,1,regime,4][metric]) for c,sign in (('channel0',1),('channel2',-1)))
                values.append(value);differences.append(dict(root_seed=root,regime=regime,metric=metric,difference=value))
            contrasts.append(dict(regime=regime,metric=metric,**interval(values)))
    table(out/'channel-did.csv',contrasts);table(out/'channel-did-roots.csv',differences)
    witness=witnesses(primary,gate);table(out/'live-state-witnesses.csv',witness)
    sens=sensitivity();table(out/'fixed-policy-sensitivity-roots.csv',sens)
    groups=defaultdict(list)
    for row in sens:groups[row['regime'],row['horizon'],row['threshold'],row['group_B_lower']].append(row['B'])
    table(out/'fixed-policy-sensitivity.csv',[dict(regime=k[0],horizon=k[1],threshold=k[2],group_B_lower=k[3],group_B_upper=k[3]+150,**interval(v)) for k,v in groups.items()])
    for root in ROOTS:
        for regime in ('NOMINAL','PHYSICAL_SHIFT'):
            cell=next(x for x in sens if (x['root_seed'],x['regime'],x['horizon'],x['threshold'],x['group_B_lower'])==(root,regime,12,350,450))
            assert cell['B']==index[root,'channel0',1,regime,48]['B']
    audit=dict(status='PASSED',episodes=len(rows),overlapping_original_cells_matched=overlap,live_scalar_checks=len(rows)*12,
        independent_candidate_audit_root=ROOTS[0],witness_states=len(witness),witness_scalar_score_banks=2*len(witness),
        policy_queries=sum(r['queries'] for r in rows),audit_queries_excluded_from_policy_cost=True,
        enforced_violations=sum(r['executed_violations'] for r in rows if r['V']),
        witness_by_regime={regime:sum(w['witness'] for w in witness if w['regime']==regime) for regime in ('NOMINAL','PHYSICAL_SHIFT')})
    save(out/'audit.json',audit);print(json.dumps(audit))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(Path(p.parse_args().output))
