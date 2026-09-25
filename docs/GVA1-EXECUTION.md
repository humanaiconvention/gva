# GVA-1 execution readiness

This implementation prepares the already published [repair protocol](../gva1-preregistration/PREREGISTRATION.md). It changes no scientific endpoint, margin, intervention, sample size, candidate order or seed commitment. The forty-root development pilot and GVA-0 execution core remain immutable. The updated [research roadmap](RESEARCH-ROADMAP.md) keeps independent review open alongside collection, as recorded in the pre-collection [sequencing note](GVA1-COLLECTION-NOTE.md).

The completed [preflight](../gva1-execution-v0.1/PREFLIGHT.json) passed 19 tests and reproduced all 640 pilot episodes, with 7,680 live scalar checks, 119,808 scalar candidate-replica checks and 1,597,440 policy preview queries. The [source/runtime seal](../gva1-execution-v0.1/FREEZE.json) preserves its historical status `EXECUTION_READY_NOT_STARTED`. It binds source hash `960bcdc5eb005f474b17ddd4252f5ce0832ff3e93b2a2c04f97f7e9feec2ac16`. The later [confirmation run](../paper/GVA1-REPORT.md) completed all 145 roots on 25 September 2026 UTC without changing this seal.

## Preparation commands

Use the exact runtime in `requirements-replay.txt` (CPython 3.13.14). From the repository root:

```sh
python -m gva1.preflight --output /absolute/path/to/new-validation-directory
python -m gva1 freeze --preflight /absolute/path/to/new-validation-directory/PREFLIGHT.json --output /absolute/path/to/new-freeze.json
python -m gva1 verify-freeze --freeze /absolute/path/to/new-freeze.json
```

Preflight runs fault/semantic tests and all 640 development episodes, comparing every original metric and action sequence to the preserved pilot fixture. It does not generate a reserved confirmation initial state or disturbance. The freeze commits runner and test source, the reference core, prospective inputs, fixture, runtime and validation receipt. Changes require a new successful preflight and a new freeze; do not overwrite an old seal.

## Authorization and collection

The implementation is ready only when preflight and freeze verification pass. The separate outside-review step is not satisfied by these author-provided tests. The historical prototype settings retain `confirmation_enabled=false`; the new execution interface requires an explicit confirmation command and a valid execution seal. Preparation never invokes that command.

For the later authorized collection phase, the command is `python -m gva1 run-confirmation --freeze /absolute/path/to/freeze.json --output /absolute/path/to/new-run-directory --execute-confirmation`. The only confirmation design is the fixed 145-root namespace, all sixteen cells and audit root positions 1,20,145. No CLI switch changes K, sample size, margins, regimes, interventions or the family of bounds. Progress reports contain completion counts only. Statistical analysis starts after all 2,320 episodes have committed and passed integrity checks.

## Operational changes from the development prototype

- Every gate verdict, including acceptance and noop, identifies the base rule, repair rule/version, current time, immutable IDs and prior q vector. A digest binds that identity to both candidate previews and final authorization. State-dependent answers are recomputed for each current state. Only the unchanged base predicate uses a shared cache.
- Base symbolic obligations and the finite catalogue's base solver checks run during measured setup. A solver unknown/error aborts without dispatch. The new stateful extension is independently checked over all 256 binary q histories and all 48 actions; this is a finite-domain check, not a new proof about arbitrary programs.
- One captured policy preview batch is independently audited after authorization timing, rather than repeating the policy batch. The retained eight replicas and exact scores are unchanged. Policy queries, measurement-coordinate counts and scalar audit work are reported separately.
- Every live physics/report transition and executed predicate is checked against scalar logic. The trace stores full before/after states, disturbances, reports, original missingness, action identity, candidate order, exact rational scores, gate decisions and timing. Preview arrays are committed by shape/dtype/content digest and reproducible from named streams; full replica arrays are not redundantly written at every decision.
- Root commits contain all sixteen episodes, 192 hash-chained live events, metrics and an external manifest. Source is rechecked at each root boundary and runtime again before completion. Final analysis implements the original eighteen bounds, including zero-variance unassessability and nonzero incidence upper bounds after zero observed events.

## Interrupted runs

Use the same command with `--resume` only for an infrastructure interruption. Completed root blocks must form an ordered prefix and pass hashes, chain checks, trace reconstruction, endpoint and cost checks before reuse. An atomic root commit that completed just before a checkpoint-file interruption is verified and adopted without rerunning it.

An incomplete root is retained in a separate `interrupted-*` directory with a recovery record. Its partial outcomes never enter analysis. The pending root is then deterministically recomputed using the original keys; this is an infrastructure recovery, not a new draw. Audit/semantic failures write `INVALIDATED.json` and block automatic resume. Source/runtime/design changes also prevent resuming the old run.

`costs.json` separates successful policy work, scalar auditing, setup, logging, checkpoint checks and recorded interrupted-attempt overhead. Interrupted overhead is explicitly a lower bound because a process can fail before persisting an event. Decision latency starts when the current observation is available and includes candidates, previews, score comparisons and final authorization; it excludes live execution and evaluator-only work. No wall-clock success claim follows from matched-query results.

## Trust and publication boundary

These checks operate on a trusted local filesystem and fixed actor. Hashes detect differences relative to a commitment; they do not prevent a malicious owner from rewriting both data and hashes or establish independent replication. Full preflight traces remain local because they can be regenerated. Execution source, tests/fixture, compact readiness receipt and source/runtime seal are public. The completed confirmation release adds every root metric, all eighteen bounds, audit/cost receipts and a separately downloadable complete synthetic trace archive. The zero-outcome fields in frozen pre-collection receipts and verification commands describe their historical or command-local scope, not current study status.
