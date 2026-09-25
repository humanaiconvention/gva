# GVA

**GVA-0 is closed as a verified synthetic mechanism demonstration. Independent external replication is still sought.**

The vulnerability was deliberately constructed and known from development. The frozen run verifies its implementation and within-benchmark variation. It does not establish a surprising empirical discovery or a general law of alignment. The [v0.5.1 review response](paper/REVIEW-RESPONSE.md) narrows the framing and adds explicitly exploratory checks; v0.5.0 and all original scientific inputs/results remain preserved.

The study asks whether stronger optimization finds harmful actions that an incomplete action contract permits. It uses eight persistent synthetic individuals, twelve decisions, a finite 48-action catalogue, biased outcome reports and an enforced action predicate. No language model, human participant data or claim of general alignment is involved.

Twenty fresh paired roots (820 episodes) passed the frozen four-criterion confirmation rule:

| Criterion | Mean K48−K4 difference | Simultaneous lower bound | Required |
|---|---:|---:|---:|
| Nominal harm burden | .118229 | .101448 | >.05 |
| Nominal repeated legal production | .879167 | .851742 | >.20 |
| Shifted harm burden | .193750 | .183779 | >.05 |
| Shifted repeated legal production | .879167 | .851742 | >.20 |

All enforced cells had zero executed contract violations. The result concerns search pressure **within a fixed incomplete contract**; it does not establish that enforcement worsens outcomes relative to unrestricted action. Enforcement reduced harm relative to unrestricted action. The shifted anchor follows the same primary policy under harsher physics and is not an independent replication. Fusion controls are retained in the supplement.

## Read the case study

- [Paper](paper/MANUSCRIPT.md) and [complete supplementary tables](paper/SUPPLEMENT.md).
- [Original frozen scientific protocol](protocol/PREREGISTRATION.original.md).
- [Machine-readable decision](results/gva0/result.json), [root-level results](results/gva0/metrics.json), and [audit record](results/gva0/audit.json).
- [Provenance and publication boundary](docs/PROVENANCE.md).
- [Independent replication specification and invitation](docs/INDEPENDENT-REPLICATION.md).

The pre-run suite passed 166 tests. During confirmation, 9,840 live transitions and 478,080 candidate previews were checked against independent scalar calculations. The original run was locally committed before outcomes. This GitHub publication occurs afterward and is **not retrospective external preregistration or peer-reviewed certification**.

## Verify and reproduce

Verify hashes, seed separation and the four statistical bounds with Python's standard library:

```sh
python scripts/verify_release.py
```

For computational reproduction, use CPython 3.13.14 and the frozen package versions:

```sh
python -m pip install -r requirements-replay.txt
python reference/reproduce.py --output reproduction
```

The publication wrapper runs all 820 episodes and compares B/L/P, both group outcomes, harm counts, repeated legal-production rates, violations and preview counts against every archived cell. Use `--smoke` for one root or `--traces` to save reconstructed synthetic trajectories. The exact execution-core files are retained byte-for-byte; the portable wrapper is clearly identified as a later publication adaptation. This is author-provided reproduction, not independent replication. See [reproduction details](docs/REPRODUCTION.md).

## Exploratory review additions

The added seven-budget sweep is not monotone: nominal harm peaks at K32 and falls at K48. The post hoc channel-by-search comparison, unrestricted K4 cells, all 480 live-state bias replays and 54 fixed-policy sensitivities are in [Supplement S5](paper/SUPPLEMENT.md#s5-post-publication-exploratory-review-not-original-confirmation). None replaces the original primary test.

## Release scope

The separate [GVA-1 prospective repair protocol](gva1-preregistration/PREREGISTRATION.md) specifies report repair, contract repair and their combination. Its sample calculation uses forty new development roots and selected **145 fresh roots / 2,320 episodes**. The [completed confirmation report](paper/GVA1-REPORT.md) retains all sixteen conditions and eighteen simultaneous bounds: **all three repairs met their separate criteria**, with zero observed breaches in repaired episodes and zero executed contract violations. Each repaired K48 regime's harmful-episode incidence upper bound is 3.9781%; zero observed events do not establish zero risk. The result validates specified repairs within this constructed benchmark and does not rank the repairs or establish broad robustness.

The [independent review package](docs/GVA1-INDEPENDENT-REVIEW.md), all root data and a full synthetic trace archive are available. Outside review remains outstanding; the pre-collection [sequencing note](docs/GVA1-COLLECTION-NOTE.md) records the decision to proceed without waiting. The protocol, power calculation and seed commitment are distinct from GVA-0's closed result. Verify with `python scripts/verify_gva1_confirmation.py`; the [report](paper/GVA1-REPORT.md) links the complete archive and reconstruction instructions.

The separately preregistered [bounded transfer study](transfer-protocol/PREREGISTRATION.md) then tested corrected reporting versus corrected reporting plus the stateful contract across seven fixed challenges and two search procedures. Its pilot selected the minimum 40-root confirmation sample. All 28 confirmation cells had zero observed harm, so the added harm-benefit contrasts were exactly zero and unassessable; production margins passed. Under the frozen joint rule, the [transfer report](paper/GVA1-TRANSFER-REPORT.md) retires the combined-repair superiority claim for this benchmark program. This is not an equivalence result or a general claim that alignment work is a dead end.

This repository contains public research artifacts: manuscript, protocol, compact synthetic results, exact computational core, verification/reproduction tools and an independent-replication brief. It excludes private correspondence, pasted source conversations, local environments, credentials, development scratch work, bulky historical archives and full raw logs. Raw synthetic traces can be regenerated with the reproduction runner.

The original GVA-0 definitions, margins and confirmation sample are closed. GVA-1's simpler report repair remains the reference safeguard in this benchmark; additional contract complexity did not demonstrate added value under the declared transfer suite. Corrections will be documented as corrections; extensions require separate protocols, development data and sample planning. The GVA-0 choice of twenty roots is not a default for future studies.

Maintained by [HumanAI Convention](https://github.com/humanaiconvention). Implementation and analysis were developed with AI coding assistance. Neither an independent external replication nor a journal acceptance is claimed.
