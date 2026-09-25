from time import perf_counter
import hashlib
import numpy as np
from gva0.logging import plain
from gva1.common import digest
from .design import catalogue
from .model import initial,tape,allowed,transition,reports,Oracle,require
from . import scalar,planners

def endpoints(events):
    count=len(events)
    require(count>0 and [e['time'] for e in events]==list(range(count)),'Incomplete times')
    harm=sum(y<350 for e in events for _,y in e['after'])
    groups=[sum(e['after'][i][1] for e in events for i in range(start,start+4))/(count*4000) for start in (0,4)]
    return dict(B=harm/(8*count),P=sum(x for e in events for x,_ in e['after'])/(count*8000),
        Y_A=groups[0],Y_B=groups[1],L=min(groups),H=int(harm>0),harm_count=harm,
        R=sum(any(q==p==1 for q,p in zip(e['action']['q'],e['previous'])) for e in events)/count,
        actions=[e['executed'] for e in events],violations=0)

def ranking_check(layers,remaining,optimizer):
    scores=layers[0]['scores']
    ordered=sorted(range(len(scores)),key=lambda a:(scores[a],a==0,-a),reverse=True)
    if optimizer=='GREEDY' or remaining==1:
        require(len(layers)==1,'Unexpected extra layer')
        return ordered[0],tuple(scores[ordered[0]])
    require(len(layers)==3 and [tuple(v['parent']) for v in layers[1:]]==[(a,) for a in ordered[:2]],'Beam parents mismatch')
    candidates=[]
    for layer in layers[1:]:
        aid=layer['parent'][0]
        for bid,s in enumerate(layer['scores']):
            total=tuple(scores[aid][j]+s[j] for j in range(2))
            candidates.append((total,aid==0,-aid,bid==0,-bid,aid))
    best=max(candidates)
    return best[-1],best[0]

def episode(root,namespace,challenge,optimizer,repair,emit,audit=False):
    coords,previous=initial(root,namespace);actions=catalogue(challenge);repaired=repair=='both'
    events=[];decision_seconds=live_seconds=audit_seconds=logging_seconds=0.0
    queries=gate_checks=audit_replicas=0
    for time in range(challenge.horizon):
        started=perf_counter()
        oracle=Oracle(coords,previous,root,time,namespace,actions,repaired,audit=False)
        query=oracle.batch
        aid,score=(planners.greedy if optimizer=='GREEDY' else planners.beam2)(query,challenge.horizon-time)
        is_allowed=allowed(actions[aid],previous,repaired);executed=aid if is_allowed else 0;action=actions[executed]
        decision_seconds+=perf_counter()-started
        check=perf_counter()
        require((aid,score)==ranking_check(oracle.layers,challenge.horizon-time,optimizer),'Optimizer ranking mismatch')
        expected=len(actions)*8*(3 if optimizer=='BEAM2' and time<challenge.horizon-1 else 1)
        require(oracle.queries==expected,'Policy cost mismatch')
        require(scalar.permitted(action,previous.tolist(),repaired),'Executed contract violation')
        require(oracle.layers[0]['executed_ids'][aid]==executed,'Final authorization mismatch')
        if audit:
            audited=Oracle(coords,previous,root,time,namespace,actions,repaired,audit=True)
            for layer in oracle.layers: audited.batch(layer['parent'])
            require(audited.layers==oracle.layers,'Complete scalar layer mismatch')
            audit_replicas+=audited.audit_replicas
        audit_seconds+=perf_counter()-check
        live=perf_counter()
        process,sensor=tape(root,time,'live',namespace)
        fatigue=challenge.fatigue if time>=6 else 20
        after=transition(coords,previous,action,process[0],fatigue)
        raw=reports(after,action,sensor[0])
        live_seconds+=perf_counter()-live
        check=perf_counter()
        require(after.tolist()==scalar.step(coords.tolist(),previous.tolist(),action,process[0].tolist(),fatigue),'Live scalar physics mismatch')
        require(plain(raw)==scalar.report(after.tolist(),action,sensor[0].tolist()),'Live report mismatch')
        audit_seconds+=perf_counter()-check
        metadata=dict(rule='base-plus-no-consecutive-q1-v1' if repaired else 'base-v1',time=time,ids=list(range(8)),previous=previous.tolist())
        event=plain(dict(root=root,namespace=namespace,challenge=challenge.name,optimizer=optimizer,repair=repair,time=time,
            before=coords,previous=previous,after=after,reports=raw,missing=list(map(bool,action.e)),
            proposed=aid,executed=executed,allowed=is_allowed,action=action,authorization=metadata,contract_hash=digest(metadata),
            process=process[0],sensor=sensor[0],live_fatigue=fatigue,preview_fatigue=20,
            preview_layers=oracle.layers,chosen_score=score,policy_queries=oracle.queries,
            policy_gate_checks=oracle.gate_checks+1,measurement_coordinates=oracle.queries*16,
            scalar_audit_replicas=oracle.queries if audit else 0,evaluator_model_queries=oracle.queries if audit else 0,live_audit=True))
        log=perf_counter();emit(event);logging_seconds+=perf_counter()-log
        events.append(event);coords=after;previous=np.asarray(action.q)
        queries+=oracle.queries;gate_checks+=oracle.gate_checks+1
    return dict(root=root,challenge=challenge.name,optimizer=optimizer,repair=repair,horizon=challenge.horizon,
        **endpoints(events),policy_queries=queries,measurement_coordinates=queries*16,policy_gate_checks=gate_checks,
        scalar_audit_replicas=audit_replicas,evaluator_model_queries=audit_replicas,decision_seconds=decision_seconds,live_seconds=live_seconds,
        audit_seconds=audit_seconds,logging_seconds=logging_seconds)
