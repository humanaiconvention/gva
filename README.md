# GVA

**GVA-0 is closed as a verified synthetic benchmark case study. Independent external replication is still sought.**

The study asks whether stronger optimization finds harmful actions that an incomplete action contract permits. It uses eight persistent synthetic individuals, twelve decisions, a finite 48-action catalogue, biased outcome reports and an enforced action predicate. No language model, human participant data or claim of general alignment is involved.

Twenty fresh paired roots (820 episodes) passed the frozen four-criterion confirmation rule:

| Criterion | Mean K48−K4 difference | Simultaneous lower bound | Required |
|---|---:|---:|---:|
| Nominal harm burden | .118229 | .101448 | >.05 |
| Nominal repeated legal production | .879167 | .851742 | >.20 |
| Shifted harm burden | .193750 | .183779 | >.05 |
| Shifted repeated legal production | .879167 | .851742 | >.20 |

All enforced cells had zero executed contract violations. The result concerns search pressure **within a fixed incomplete contract**; it does not establish that enforcement worsens outcomes relative to unrestricted action. Fusion architecture has no superiority claim and appears only among methodological controls.

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

## Release scope

This repository contains public research artifacts: manuscript, protocol, compact synthetic results, exact computational core, verification/reproduction tools and an independent-replication brief. It excludes private correspondence, pasted source conversations, local environments, credentials, development scratch work, bulky historical archives and full raw logs. Raw synthetic traces can be regenerated with the reproduction runner.

The original GVA-0 definitions, margins and confirmation sample are closed. Corrections will be documented as corrections; extensions such as GVA-1 require separate protocols, development data and sample planning. The GVA-0 choice of twenty roots is not a default for future studies.

Maintained by [HumanAI Convention](https://github.com/humanaiconvention). Implementation and analysis were developed with AI coding assistance. Neither an independent external replication nor a journal acceptance is claimed.
