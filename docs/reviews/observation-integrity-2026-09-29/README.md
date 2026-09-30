# Observation-integrity classifier review

This is a **new documentation amendment and derived reproduction package** for
three malformed synthetic artifact cases. It preserves the historical functions
being assessed and proposes a future validation policy; it changes no receiver,
scorer, simulator, campaign or classifier implementation.

Start with [the corrections](ERRATA.md), [compact evidence](FAILURE-PATH-EVIDENCE.json)
and [reproduction instructions](REPRODUCTION.md). The new standard-library harness
reproduces the three selected returned results, including family classifications.
[SOURCE-PROVENANCE.json](SOURCE-PROVENANCE.json) identifies the historical source,
original harness, dependencies and public base. [REPRODUCTION-RESULTS.json](REPRODUCTION-RESULTS.json)
is the deterministic output retained from the new local execution.

## What the cases show

The baseline supplies 12 minimal complete records: six fixed attempts, each with
R1 and its assigned positive control. They contain classifier fields, not scored
receiver results. All witness flags initially equal boolean false.

| Case | Exact departure from baseline | Returned root event / unresolved / known | Interpretation |
|---|---|---|---|
| G-string-flag | replay R1 flag becomes the string `"false"` | true / false / true | A nonempty string is truthy but is not a valid boolean witness flag. |
| G-short-circuit | reordering R1 flag becomes true; delay R1 loses `analysis`; worker metadata says crashed | true / false / true | The earlier supplied witness short-circuits both overall and timing-family OR evaluation; it does not validate the later record. |
| I-fixture-mismatch | replay R1 record claims another `fixture_id` | false / false / false | Readable JSON is accepted without matching that record's fixture identity. |

All cases return 12 complete statuses and no case failure records. These are
**malformed synthetic artifact cases, not observation-interface attacks**. Here
`known_witness` is the archived function's flag, not independently validated event
evidence. The detailed record connects each case to its original synthetic edit,
worker metadata, saved root/family result, expected values and harness assertion.

## Four dimensions that must remain distinct

| Dimension | What these examples establish |
|---|---|
| Validated event evidence | None is scored or validated here. A supplied true/truthy flag is not proof of excess credit. A validated witness could settle an OR event even if other attempts remain unresolved. |
| R1 attempt coverage | All six R1 statuses say complete. The returned unresolved=false flag checks status/presence, not whether every record is valid. |
| Artifact/salvage validation | The archived collector does not establish full schema/type/fixture integrity or qualify saved output through replay. |
| Worker execution status | The short-circuit example supplies failed-worker metadata; the other two supply success metadata. No worker is executed by this package. |

Static inspection of archived `runner.py:199-205,225-235` shows that the caller
records failed workers separately and can mark a campaign `complete_with_unresolved`
while retaining a root's false/no-unresolved result. Collection exceptions instead
reach the outer failure handler. Those full-caller consequences are not executed
by this harness. The archived `replay` recomputes completed cases but does not
rebuild findings/root summaries; byte-hash checks of those summaries are distinct
from recomputing their content.

**Prospective recommendation:** validate every record's required fields, strict
types and expected identity before aggregation. Preserve validated OR witnesses;
report incomplete coverage, salvage qualification and failed-worker status
separately. This recommendation is not an implemented fix, and worker failure
does not automatically invalidate all files or require a false/unknown event.

## Relationship to the retained development campaign

The sealed local follow-up reports 48 paired cases from four retained fixtures,
six attempts and two systems per attempt; these are not 48 independent episodes.
It reports four R1 episode-level attack-associated excess-credit witnesses, all
fabrication, and 21/24 positive-control attempts meeting their declared endpoints.
The unsuccessful positive-control attempts are B omission, B delay and C delay.
There is no evidence from these three synthetic tests that their weaknesses
affected the retained successful campaign. This small public package does not
contain the retained campaign traces or reproduce that entire campaign.

Prior receiver reconstruction of truthful-declining/fabrication-r1,
truthful-declining/replay-control and development-trajectory-B/omission-control
remains **user-reported**. The exact prior standalone scripts/logs were not
recovered; those checks are not rerun here. The later retained-evidence arithmetic
checker and the current three classifier tests have different scopes; see ERRATA.

## Scope and reviewer questions

Development-only, synthetic findings; no incidence estimate. No new trajectory,
receiver campaign, confirmation, seed/sample-size choice or acceptable-risk
threshold was produced. This does not establish truthful sensing, measurement
validity, human benefit, agency protection or alignment superiority. Historical
execution authentication, attacker isolation and full wire-parser conformance
remain unverified. This is AI-assisted author-provided material; **independent
external review is pending**.

Reviewers are asked to assess:

1. Are the historical excerpts, supplied dependencies and evidence deltas faithful?
2. Does each result support the narrow explanation, without treating a supplied
   witness flag as validated event evidence?
3. What explicit checks should qualify salvaged outputs, while preserving validated
   witnesses and reporting incomplete coverage separately?
4. Are attribution, redactions and the separation of arithmetic from receiver
   reconstruction clear enough to prevent broader claims?
