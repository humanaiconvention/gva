"""Whole-root execution, no interim analysis, and explicit confirmation activation."""
from pathlib import Path
from time import perf_counter
import os
from gva0.actor import ActorProcess
from gva0.gate import FormalGate
from formal.gate_obligations import obligations
from .common import AuditFailure, InfrastructureFailure, require, read, atomic_json, digest, sha, utc, journal
from .design import CELLS, validate_design, verify_inputs
from .engine import episode
from .freeze import source_files, runtime, validate_freeze
from .storage import RootWriter, recover, verify_root, cost_report
from .statistics import analyze

def execute(design, output, *, resume=False, freeze_path=None, execute_confirmation=False, fault=None):
    validate_design(design)
    verify_inputs()
    # No initial state or named disturbance is generated before these checks.
    if design.mode == 'confirmation':
        require(execute_confirmation and freeze_path is not None, 'Confirmation requires explicit activation and verified freeze')
        require(fault is None, 'Fault injection is development-only')
        validate_freeze(freeze_path)
    else:
        require(not execute_confirmation, 'Confirmation activation cannot relabel development')
    snapshot = source_files()
    metadata = dict(design=design.record(), source_hash=digest(snapshot), runtime=runtime(),
                    execution_freeze_sha256=sha(freeze_path) if freeze_path else None)
    identity = digest(metadata)
    output = Path(output)
    if resume:
        require(output.is_dir(), 'Resume needs an existing run')
        require(read(output / 'RUN.json')['identity'] == identity, 'Resume source/runtime/design changed')
        journal(output / 'RECOVERY.jsonl', dict(utc=utc(), event='resume_requested', run_identity=identity))
    else:
        output.mkdir(parents=True, exist_ok=False)
        atomic_json(output / 'RUN.json', dict(identity=identity, created_utc=utc(), **metadata))
    writer = None
    try:
        commits, rows = recover(output, design, identity)
        if (output / 'COMPLETED.json').exists():
            receipt = read(output / 'COMPLETED.json')
            require(len(commits) == len(design.roots), 'Completion with missing roots')
            require(sha(output / 'metrics.json') == receipt['metrics_sha256'], 'Final metrics changed')
            require(read(output / 'metrics.json') == rows, 'Final metrics differ from checkpoints')
            require(sha(output / 'costs.json') == receipt['costs_sha256'], 'Final cost ledger changed')
            if design.mode == 'confirmation':
                require(sha(output / 'result.json') == receipt['result_sha256'], 'Final analysis changed')
            return receipt
        setup_started = perf_counter()
        proof = obligations()
        require(all(c['result'] == 'unsat' for c in proof), 'Original symbolic obligations failed')
        base = FormalGate()
        for aid in range(48):
            verdict = base(aid)
            require('SOLVER_UNCHECKED' not in verdict.reason_codes, 'Indeterminate setup gate')
        proof_seconds = perf_counter() - setup_started
        actor_started = perf_counter()
        with ActorProcess() as actor:
            startup_seconds = perf_counter() - actor_started
            journal(output / 'SETUP.jsonl', dict(utc=utc(), formal_and_gate_seconds=proof_seconds,
                    actor_startup_seconds=startup_seconds, formal=proof, solver_log=base.solver_log))
            for root in design.roots[len(commits):]:
                writer = RootWriter(output, root, identity)
                metrics = []
                def emit(event):
                    writer.emit(event)
                    if fault:
                        fault('event', root, event)
                for cell in CELLS:
                    metrics.append(episode(design, root, cell, actor, base, emit))
                require(source_files() == snapshot, 'Source changed during collection')
                writer.commit(metrics)
                writer = None
                if fault:
                    fault('root_renamed', root, None)
                verify_started = perf_counter()
                verify_root(output / str(root), design, root, identity)
                journal(output / 'CHECKPOINT-AUDITS.jsonl', dict(root_seed=root, seconds=perf_counter() - verify_started))
                commits.append(dict(root_seed=root, manifest_sha256=sha(output / str(root) / 'COMPLETE.json')))
                rows.extend(metrics)
                atomic_json(output / 'CHECKPOINT.json', dict(run_identity=identity, roots=commits))
                print(f'Completed {len(commits)}/{len(design.roots)} {design.mode} root blocks', flush=True)
        require(source_files() == snapshot and runtime() == metadata['runtime'], 'Source/runtime changed during collection')
        require(len(rows) == len(design.roots) * 16, 'Incomplete collection')
        atomic_json(output / 'metrics.json', rows)
        atomic_json(output / 'costs.json', cost_report(output, rows))
        result_sha = None
        if design.mode == 'confirmation':
            atomic_json(output / 'result.json', analyze(rows, audit_passed=True))
            result_sha = sha(output / 'result.json')
        receipt = dict(status='COMPLETED', mode=design.mode, roots=len(design.roots), episodes=len(rows),
            live_transitions=len(rows) * 12, policy_queries=sum(r['queries'] for r in rows),
            scalar_audit_replicas=sum(r['audit_replicas'] for r in rows),
            zero_violations=all(r['violations'] == r['base_violations'] == r['stateful_violations'] == 0 for r in rows),
            metrics_sha256=sha(output / 'metrics.json'), result_sha256=result_sha,
            costs_sha256=sha(output / 'costs.json'),
            run_identity=identity, completed_utc=utc(), confirmation_roots_executed=len(design.roots) if design.mode == 'confirmation' else 0)
        atomic_json(output / 'COMPLETED.json', receipt)
        return receipt
    except (OSError, InfrastructureFailure) as error:
        if writer:
            writer.close_incomplete()
        journal(output / 'RECOVERY.jsonl', dict(utc=utc(), event='infrastructure_interruption', error_type=type(error).__name__, message=str(error)))
        raise
    except BaseException as error:
        if writer:
            writer.close_incomplete()
        # Semantic/unknown errors never silently become infrastructure retries.
        atomic_json(output / 'INVALIDATED.json', dict(utc=utc(), error_type=type(error).__name__, message=str(error)))
        raise
