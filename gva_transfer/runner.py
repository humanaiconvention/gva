"""Whole-root collection, hash chains, scalar reconstruction, and final-only analysis."""
from pathlib import Path
from time import perf_counter
import json
import os
import uuid
import numpy as np
from gva0.logging import EventWriter,verify_stream,plain
from gva1.common import read,sha,digest,atomic_json,utc,journal
from .design import CELLS,catalogue
from .model import require,initial,tape
from .commitment import source,verify,runtime
from .engine import episode,endpoints,ranking_check
from . import scalar
from .analysis import matrix,plan,analyze

def verify_root(folder,identity,namespace,root,audited):
    manifest=read(folder/'COMPLETE.json');rows=read(folder/'metrics.json')
    require(manifest['identity']==identity and manifest['root']==root,'Root identity')
    require(sha(folder/'events.jsonl')==manifest['events_sha256'] and sha(folder/'metrics.json')==manifest['metrics_sha256'],'Root file hashes')
    verify_stream(folder/'events.jsonl',manifest['anchor'])
    events=[json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines()]
    require(len(rows)==28 and len(events)==408,'Root completeness')
    offset=0
    for row,(challenge,optimizer,repair) in zip(rows,CELLS):
        require((row['root'],row['challenge'],row['optimizer'],row['repair'])==(root,challenge.name,optimizer,repair),'Cell identity')
        subset=events[offset:offset+challenge.horizon];offset+=challenge.horizon
        coords,previous=initial(root,namespace);coords=coords.tolist();previous=previous.tolist()
        actions=catalogue(challenge)
        for time,event in enumerate(subset):
            require((event['root'],event['namespace'],event['challenge'],event['optimizer'],event['repair'],event['time'])==(root,namespace,challenge.name,optimizer,repair,time),'Trace identity')
            require(event['before']==coords and event['previous']==previous,'State continuity')
            action=actions[event['executed']]
            require(plain(action)==event['action'] and scalar.permitted(action,previous,repair=='both'),'Executed scalar predicate')
            allowed=scalar.permitted(actions[event['proposed']],previous,repair=='both')
            require(event['allowed']==allowed and event['executed']==(event['proposed'] if allowed else 0),'Final authorization')
            require(event['authorization']['previous']==previous and event['contract_hash']==digest(event['authorization']),'History identity')
            process,sensor=tape(root,time,'live',namespace)
            require(event['process']==process[0].tolist() and event['sensor']==sensor[0].tolist(),'Named disturbances')
            fatigue=challenge.fatigue if time>=6 else 20
            expected=scalar.step(coords,previous,action,process[0].tolist(),fatigue)
            require(event['after']==expected and event['reports']==scalar.report(expected,action,sensor[0].tolist()),'Reconstructed physics/report')
            require(event['preview_fatigue']==20 and event['live_fatigue']==fatigue,'Physical isolation')
            require((event['proposed'],tuple(event['chosen_score']))==ranking_check(event['preview_layers'],challenge.horizon-time,optimizer),'Reconstructed ranking')
            queries=len(actions)*8*(3 if optimizer=='BEAM2' and time<challenge.horizon-1 else 1)
            require(event['policy_queries']==queries and event['scalar_audit_replicas']==(queries if audited else 0),'Query/audit accounting')
            coords=expected;previous=list(action.q)
        for name,value in endpoints(subset).items():
            if isinstance(value,float): require(abs(row[name]-value)<1e-12,'Endpoint '+name)
            else: require(row[name]==value,'Endpoint '+name)
        for key in ('policy_queries','policy_gate_checks','measurement_coordinates','scalar_audit_replicas','evaluator_model_queries'):
            require(row[key]==sum(e[key] for e in subset),'Summed cost '+key)
    return rows,manifest

def execute(phase,freeze_path,output,resume=False,activate=False):
    setup_started=perf_counter()
    require(activate,'Explicit phase activation required')
    frozen=verify(freeze_path,phase);roots=frozen['seeds']['roots'];namespace=frozen['seeds']['namespace']
    identity=digest(dict(freeze_sha256=sha(freeze_path),phase=phase))
    folder=Path(output);snapshot=source();audits={roots[0],roots[19],roots[-1]}
    if resume:
        require(read(folder/'RUN.json')['identity']==identity and not (folder/'INVALIDATED.json').exists(),'Invalid resume')
        journal(folder/'RECOVERY.jsonl',dict(utc=utc(),event='resume_requested'))
    else:
        folder.mkdir(parents=True,exist_ok=False)
        atomic_json(folder/'RUN.json',dict(identity=identity,phase=phase,created_utc=utc(),freeze_sha256=sha(freeze_path),seeds=frozen['seeds'],source_hash=digest(snapshot)))
    setup_seconds=perf_counter()-setup_started
    rows=[];commits=[];writer=None;started=perf_counter();checkpoint_seconds=0.0
    try:
        gap=False
        for root in roots:
            final=folder/str(root)
            if final.exists():
                require(not gap,'Non-prefix root blocks')
                checkpoint_started=perf_counter()
                data,manifest=verify_root(final,identity,namespace,root,root in audits)
                checkpoint_seconds+=perf_counter()-checkpoint_started
                rows.extend(data);commits.append(dict(root=root,manifest_sha256=sha(final/'COMPLETE.json')))
            else: gap=True
        if (folder/'CHECKPOINT.json').exists():
            old=read(folder/'CHECKPOINT.json')['roots'];require(old==commits[:len(old)],'Checkpoint prefix changed')
        if (folder/'COMPLETED.json').exists():
            receipt=read(folder/'COMPLETED.json');require(len(commits)==len(roots),'Incomplete completion')
            for name,value in receipt['files'].items(): require(sha(folder/name)==value,'Completed file changed')
            return receipt
        for partial in folder.glob('*.partial'):
            require(len(commits)<len(roots) and partial.stem==str(roots[len(commits)]),'Unexpected partial root')
            dest=folder/('interrupted-'+partial.name+'-'+uuid.uuid4().hex)
            require(partial.resolve().parent==folder.resolve() and dest.resolve().parent==folder.resolve(),'Unsafe recovery path')
            journal(folder/'RECOVERY.jsonl',dict(utc=utc(),event='retain_partial_root',directory=dest.name))
            os.rename(partial,dest)
        for root in roots[len(commits):]:
            pending=folder/(str(root)+'.partial');pending.mkdir();writer=EventWriter(pending/'events.jsonl')
            data=[episode(root,namespace,c,o,h,writer.append,audit=root in audits) for c,o,h in CELLS]
            writer.file.flush();os.fsync(writer.file.fileno());anchor=writer.close();writer=None
            require(source()==snapshot,'Source changed during collection')
            atomic_json(pending/'metrics.json',data)
            atomic_json(pending/'COMPLETE.json',dict(root=root,identity=identity,anchor=anchor,
                events_sha256=sha(pending/'events.jsonl'),metrics_sha256=sha(pending/'metrics.json')))
            os.rename(pending,folder/str(root))
            checkpoint_started=perf_counter()
            verify_root(folder/str(root),identity,namespace,root,root in audits)
            checkpoint_seconds+=perf_counter()-checkpoint_started
            rows.extend(data);commits.append(dict(root=root,manifest_sha256=sha(folder/str(root)/'COMPLETE.json')))
            atomic_json(folder/'CHECKPOINT.json',dict(identity=identity,roots=commits))
            print(f'Completed {len(commits)}/{len(roots)} {phase} roots',flush=True)
        require(source()==snapshot and runtime()==frozen['runtime'],'Final source/runtime mismatch')
        atomic_json(folder/'metrics.json',rows)
        values=matrix(rows,roots);atomic_json(folder/'contrasts.json',values)
        result=plan(values) if phase=='development' else analyze(rows,roots)
        atomic_json(folder/('sample-size.json' if phase=='development' else 'result.json'),result)
        costs={k:sum(row[k] for row in rows) for k in ('policy_queries','policy_gate_checks','measurement_coordinates','scalar_audit_replicas','evaluator_model_queries','decision_seconds','live_seconds','audit_seconds','logging_seconds')}
        costs['current_attempt_elapsed_seconds']=perf_counter()-started
        costs['current_attempt_setup_seconds']=setup_seconds
        costs['checkpoint_validation_seconds']=checkpoint_seconds
        costs['interrupted_attempts']=[p.name for p in folder.glob('interrupted-*')]
        costs['limitation']='Policy and duplicate evaluator-model work separately counted; phase elapsed includes checkpoint validation and excludes separately recorded setup and unmeasured interpreter startup. Interrupted partial work remains in retained traces and is not another observation.'
        atomic_json(folder/'costs.json',costs)
        names=['metrics.json','contrasts.json','costs.json','sample-size.json' if phase=='development' else 'result.json']
        receipt=dict(status='COMPLETED',phase=phase,roots=len(roots),episodes=len(rows),live_transitions=408*len(roots),
            audit_roots=sorted(audits),source_hash=digest(snapshot),zero_violations=all(r['violations']==0 for r in rows),
            all_semantic_audits_passed=True,completed_utc=utc(),files={name:sha(folder/name) for name in names},external_review=False)
        atomic_json(folder/'COMPLETED.json',receipt);return receipt
    except BaseException as error:
        if writer:
            writer.file.flush();writer.close()
        if isinstance(error,OSError): journal(folder/'RECOVERY.jsonl',dict(utc=utc(),event='infrastructure_interruption',error=str(error)))
        else: atomic_json(folder/'INVALIDATED.json',dict(utc=utc(),error_type=type(error).__name__,error=str(error)))
        raise
