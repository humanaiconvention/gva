"""Portable author-provided reproduction wrapper around exact frozen core files.

This wrapper was prepared for publication after confirmation. It is not an
independently authored replication and does not claim byte-identical timing/logs.
"""
from pathlib import Path
import argparse
import json
import math
import numpy as np
from gva0.actions import CATALOGUE
from gva0.actor import ActorProcess
from gva0.gate import FormalGate
from gva0.measurement_controls import CONTROLS, ControlledPreview, measurements, visible_estimate
from gva0.seeds import candidates, tape
from gva0.world import initial_state, transition
from gva0.types import ActorObservations, nullable
from gva0.logging import plain
from gva0.evaluator import evaluate
from gva0.objective import average_scores
from formal.gate_obligations import obligations
from analysis import scalar_reference as scalar
from analysis.control_reference import candidate_scores, reports

RELEASE=Path(__file__).resolve().parents[1]


def episode(root,name,V,K,regime,mode,namespace,widths,actor,gate,audit=False,trace=None):
    state,observation=initial_state(root,namespace),None
    states=[]
    repeat=violations=queries=0
    for time in range(12):
        ids=candidates(root,time,K,namespace)
        preview=ControlledPreview(state,root,regime,name,V,gate,widths,mode,namespace=namespace)
        proposal,score=actor.choose(observation,ids,preview)
        if audit:
            batch=preview.batch(ids,preview.token)
            process,sensor=tape(root,time,'preview',CONTROLS[name].rho,namespace)
            expected=candidate_scores(plain(state),root,ids,name,V,regime,mode,process,sensor)
            assert {a:average_scores(s) for a,s in zip(ids,batch.scores)}==expected
        authorization=gate(proposal,enabled=V)
        action=CATALOGUE[authorization.executed_action_id]
        process,sensor=tape(root,time,'live',CONTROLS[name].rho,namespace)
        after=transition(state,action,process[0],regime)
        expected=scalar.step(plain(state),action,process[0].tolist(),regime)
        assert plain(after)==expected
        coords=np.array(list(zip(after.X,after.Y)))[None,None]
        raw,_=measurements(coords,(action,),sensor,regime,time,CONTROLS[name])
        assert plain(raw[0,0])==reports(expected,action,sensor[0].tolist(),regime,time,name)
        observation=ActorObservations(nullable(raw[0,0]),CONTROLS[name].channel_ids,tuple(bool(x) for x in action.e),provenance='v0.5:'+name)
        legal=scalar.permitted(action)
        assert not V or legal
        repeat+=legal and any(q==p==1 for q,p in zip(action.q,state.q_prev))
        violations+=not legal
        queries+=8*K  # Independent audit calls are separate from policy query accounting.
        if trace:
            trace.write(json.dumps(plain(dict(root_seed=root,namespace=namespace,control=name,V=V,K=K,regime=regime,preview_mode=mode,time=time,
                before=state,after=after,proposed=proposal,executed=authorization.executed_action_id,score=score,
                process_noise=process[0],sensor_noise=sensor[0],reports=raw[0,0])))+'\n')
        states.append(after)
        state=after
    metrics=evaluate(states)._asdict()
    expected=scalar.endpoints([{'after':plain(s)} for s in states])
    assert all(abs(metrics[k]-v)<1e-12 for k,v in expected.items())
    return dict(root_seed=root,namespace=namespace,control=name,V=V,K=K,regime=regime,preview_mode=mode,
                **metrics,legal_repeat_rate=repeat/12,executed_violations=violations,queries=queries)


def run(output,smoke=False,traces=False):
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    seeds=json.loads((RELEASE/'protocol/seed-manifest.json').read_text())
    calibration=json.loads((RELEASE/'protocol/calibration.json').read_text())
    freeze=json.loads((RELEASE/'provenance/FREEZE.original.json').read_text())
    archived=json.loads((RELEASE/'results/gva0/metrics.json').read_text())
    key=lambda r:tuple(r[k] for k in ('root_seed','control','V','K','regime','preview_mode'))
    lookup={key(r):r for r in archived}
    formal=obligations();assert all(c['result']=='unsat' for c in formal)
    roots=seeds['roots'][:1] if smoke else seeds['roots']
    rows=[];gate=FormalGate()
    trace=(out/'reconstructed-traces.jsonl').open('x',encoding='utf-8') if traces else None
    try:
        with ActorProcess() as actor:
            for index,root in enumerate(roots):
                for name,V,K,regime,mode in freeze['cells']:
                    row=episode(root,name,V,K,regime,mode,seeds['namespace'],calibration[name]['half_widths'],actor,gate,
                                audit=root==roots[0],trace=trace)
                    old=lookup[key(row)]
                    for metric in ('B','L','P','Y_A','Y_B','harm_count','denominator','legal_repeat_rate','executed_violations','queries'):
                        if not math.isclose(row[metric],old[metric],rel_tol=0,abs_tol=1e-12):
                            raise ValueError(f'Outcome mismatch: {key(row)}, {metric}')
                    rows.append(row)
                print(f'Reproduced {index+1}/{len(roots)} root blocks',flush=True)
    finally:
        if trace:trace.close()
    (out/'metrics.json').write_text(json.dumps(plain(rows),indent=2)+'\n')
    receipt=dict(status='MATCHED_ARCHIVED_OUTCOMES',roots=len(roots),episodes=len(rows),mode='smoke' if smoke else 'full-reproduction',
        independent_replication=False,contract_violations=sum(r['executed_violations'] for r in rows if r['V']),
        comparisons='B/L/P, both group outcomes, harm counts, R, contract violations and policy preview counts, every cell',
        core='Exact files listed in provenance/published-core-map.json; wrapper is a publication adaptation')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--traces',action='store_true')
    args=parser.parse_args();run(args.output,args.smoke,args.traces)
