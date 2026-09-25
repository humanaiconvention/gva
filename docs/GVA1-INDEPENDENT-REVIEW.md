# GVA-1 independent review package

Prepared 25 September 2026 UTC before confirmation collection. Independent external review is outstanding. Collection will proceed under the unchanged published protocol while this invitation remains open; review completion is not a preregistered eligibility criterion.

## Choose a bounded review

| Package | Question | Inputs | Requested output |
|---|---|---|---|
| A: arithmetic and planning | Do the sample calculation and eighteen bounds implement the written rule? | Protocol, contrast matrix, sample-size grid; after collection, all root metrics | Recomputed numbers, assumptions challenged, discrepancies |
| B: implementation semantics | Does the simulator implement the intended interventions? | Written equations, protocol, seed schedule, development fixture | Independently calculated cases and minimal counterexamples |
| C: collection integrity | Was the fixed experiment executed completely and without changes? | Source/runtime freeze, run metadata, checkpoint commitments, costs, completion receipt | Coverage, hash, seed, exclusion and audit assessment |

Do any one package; do not imply that arithmetic verification alone independently validates simulator semantics. State affiliation, implementation independence, files inspected and any AI assistance. Author-provided scalar checks are useful cross-checks, not outside replication.

## Stable starting points

- [Prospective protocol release](https://github.com/humanaiconvention/gva/releases/tag/gva1-prereg-v0.1).
- [Frozen execution release](https://github.com/humanaiconvention/gva/releases/tag/gva1-execution-v0.1), including 19 tests and the complete 640-episode development replay receipt.
- [Scientific protocol](../gva1-preregistration/PREREGISTRATION.md), [sample calculation](../gva1-preregistration/plan_sample_size.py), [pilot contrast matrix](../gva1-preregistration/pilot-contrast-matrix.json), [seed commitment](../gva1-preregistration/SEED-COMMITMENT.json).
- [Execution instructions](GVA1-EXECUTION.md) and [review report template](REVIEW-REPORT-TEMPLATE.md).

The execution source aggregate is `960bcdc5eb005f474b17ddd4252f5ce0832ff3e93b2a2c04f97f7e9feec2ac16`; protocol SHA-256 is `44d65a132eaf44be7a29d28811944e2701b22c5acbf8d8764fa68fa47d0aca94`. Preserve the published tags when comparing later results.

## Package A: arithmetic and planning

Recalculate A_B = (B48_original - B4_original) - (B48_repair - B4_repair), D_P = P48_repair - P48_original, and repaired K48 episode incidence H. The independent unit is a paired root, not an ID, step or preview. Each repair has six strict criteria across the two correlated regimes: lower(A_B) > .05, lower(D_P) > -.05, upper(Pr(H)) < .10. There are eighteen simultaneous one-sided bounds at alpha=.05/18, plus zero executed violations and successful audits. Zero continuous variance is unassessable under this frozen rule.

Review whether the normal/t approximation, pilot variance inflation and prospective alternatives support the stated conditional sample-size calculation. In particular, the one-percent incidence alternative is an assumption, not an estimate of zero from the pilot. Reproduce the N=145 selection and the N144/N145 discrete acceptance change; assess power sensitivity separately without replacing the frozen sample after outcomes. Simultaneous Bonferroni reporting is deliberately stronger than an all-pass intersection-union test requires. The protocol makes separate repair decisions and no between-repair superiority claim.

From a checkout, using the pinned runtime:

```sh
python scripts/verify_release.py
python scripts/verify_followups.py
python gva1-preregistration/plan_sample_size.py
```

These commands do not simulate confirmation roots. The historical follow-up verifier's `confirmation_outcomes_generated: 0` describes its own operation; it is not a current study-status declaration. The immutable freeze's zero count records its pre-collection state.

## Package B: implementation semantics

For a genuinely independent implementation, start with the protocol and [GVA-0 equations](../paper/MANUSCRIPT.md), commit your code before opening `gva1/` or `reference/`, then compare development roots 3000001..3000040. Keep the exact eight-ID roster, twelve decisions, 48 actions, K4/K48 nesting, eight previews and noop/lowest-ID tie rule.

Prioritize these falsification cases:

1. Remove the explicit +100q report term before clipping; preserve noise, missingness and physical q effects. Test both live reports and previews at clipping boundaries.
2. Reject repeated q=1 for any individual's actual previous executed q. Rejection becomes noop, so history follows executed actions. Verify accepted and rejected gate metadata and final authorization.
3. Under PHYSICAL_SHIFT, change live physics at the specified time while every preview remains nominal. Share named initial, candidate, process and sensor streams across paired cells.
4. Score missing X/Y as zero only in the full-roster objective; preserve missingness in the measurement record. Fully evaluate eight replicas for every competing candidate.
5. Reconstruct B, L, P, group outcomes, R and H from post-action states; check all steps, including the last. R is descriptive, not evidence of efficacy.

Author-provided development reproduction (not independent implementation):

```sh
python -m unittest discover -s tests/gva1 -v
python -m gva1.preflight --output /absolute/path/to/new-development-review
```

## Package C: collection integrity

Require exactly roots 4000001..4000145, namespace `gva1-confirm-repair-v0.1`, sixteen cells per root, 2,320 episodes and 27,840 live transitions. Require 5,790,720 policy previews and 119,808 separately counted scalar candidate-replica audits on root positions 1,20,145. All live transitions and executed predicates are checked. Inspect all failed criteria as well as successful ones.

Verify source and runtime against the pre-collection seal, all complete-root commitments, final metrics and analysis hashes, explicit interruption records and any deviations. Check that no partial root enters inference and that no semantic failure is treated as a routine retry. Complete synthetic traces should be supplied as a separate downloadable archive with hashes, keeping the repository compact. Replaying archived roots is reproducibility evidence, not a fresh sample.

## Returning findings

Use the report template and open a repository issue or pull request. Report negative findings and unresolved questions with equal prominence. A later semantic discrepancy can invalidate affected claims; preserve the original version and publish a correction rather than silently overwriting results. No reviewer is currently recruited or endorsed.
