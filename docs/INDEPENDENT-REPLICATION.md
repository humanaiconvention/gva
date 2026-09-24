# Independent replication invitation

We seek a researcher or team unaffiliated with the implementation effort to reproduce the GVA-0 mechanism from the written specification. No external replicator is currently claimed. Please open an issue describing the intended scope; a negative result or implementation discrepancy is useful.

## Separation of three activities

1. **Artifact verification:** Check published hashes and recompute the four bounds from root-level data. This is useful but does not verify simulator semantics.
2. **Independent implementation:** Implement the equations, report paths, complete-roster score and gate from the protocol before consulting `reference/`. Commit your source before comparison. Use the archived roots to identify semantic discrepancies; do not count this as fresh inference.
3. **Independent fresh-root replication:** Freeze your implementation, seed namespace, sample size, exclusions and test before examining new outcomes. State whether you are reproducing the exact original contrasts or testing an extension. Any new sample size must have its own justification.

## Required specification

The [scientific protocol](../protocol/PREREGISTRATION.original.md) defines eight IDs, two fixed groups, twelve decisions, the 48-action catalogue, full-roster objective, four measurement controls, physical regimes and statistical families. The [paper methods](../paper/MANUSCRIPT.md) supplies explicit coordinate equations and starting-state ranges. The original [seed manifest](../protocol/seed-manifest.json) specifies all initial, candidate, process and sensor streams.

For complete clarity: create group-targeted actions for both four-person groups with q in {0,1,2} and u,m,e in {0,1}; remove duplicates, include noop and the all-eight support action, and sort by the concatenated q/u/m/e tuple to obtain IDs 0..47. Primary ties prefer noop, then lowest ID. Reject q>1, total u>4, any m or any e in enforced cells. Rejected actions preview and execute as noop. Each candidate has eight full preview replicas, with exact rational component averages and lexicographic comparison.

The primary anchors use channel0 plus enforcement in NOMINAL and PHYSICAL_SHIFT with nominal previews. B counts Y<350 over 96 post-action ID-steps. R counts decisions containing at least one legal q=1 with that same individual's preceding q=1, divided by twelve. D_B and D_R are K48 minus K4. Their vector order is nominal B, nominal R, shifted B, shifted R. Minimum effects are (.05,.20,.05,.20). All four one-sided Bonferroni lower bounds must exceed their thresholds, every enforced cell must have zero executed contract violations, and semantic audits must pass. Zero primary sample variance is unassessable under the original rule.

## Suggested discrepancy probes

- Clipping before versus after report bias; mean scores with exact thirds.
- Missing records remain missing while scoring substitutes X=Y=0 over all eight IDs.
- All original channel0 copies share a realization; repeated readings share bias but use independent noise.
- PHYSICAL_SHIFT changes live fatigue at t=6 while nominal previews retain fatigue=20.
- Rejected candidates, noop ties, candidate nesting and all eight replicas.
- Complete horizon and root-level inference, without treating individuals, times or replicas as independent samples.

## Report back

Provide your source commit, implementation independence statement, runtime, seed commitment, complete root-level B/L/P/R data, violations, all four bounds, discrepancies and exclusions. Preserve negative results. If you test bias removal or contract repair, label it a separately preregistered extension rather than changing GVA-0's confirmed endpoint after the fact.

This invitation does not claim that a replicator has been recruited, promise a positive result, or treat author-provided reproducibility as external validation.
