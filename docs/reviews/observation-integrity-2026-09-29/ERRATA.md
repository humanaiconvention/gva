# Amendment to the sealed local review documents

This file supplements, and does not replace or rewrite, the sealed
`FAILURE-PATH-REVIEW.md`, `REVIEWER-HANDOFF.md` and `VERIFICATION-ADDENDUM.md`.
Their source and follow-up identities are recorded in SOURCE-PROVENANCE.json.
The historical source ZIP and follow-up manifest matched the expected hashes
before this publication work. Corrections here concern documentation and scope;
no implementation fix is included.

## 1. Reproduction logs must be protected before invocation

The old PowerShell examples use `>` redirection. PowerShell can truncate an
existing log before Python rejects an existing output directory/result file.
Therefore those examples did not guarantee preservation of existing logs.

The new harness claims a fresh output directory with `mkdir(exist_ok=False)`
before opening either log; both logs and all results use exclusive creation.
An existing output path produces exit 2 before any log is opened. REPRODUCTION.md
uses explicit read-only package and new output arguments with **no shell
redirection**. The input package is not used as a writable working directory.

## 2. Dependency-manifest equality is content evidence, not run provenance

The actual top-level `FUNCTION-DEPENDENCIES.json` and
`failure-run-02/FUNCTION-DEPENDENCIES.json` are byte-identical: both are 5,566
bytes with SHA-256
`784749e688e12725dec4b074e496e04b8599c39eae8873b83ab0f03f897b8ff7`.

Inspection found the same `load_functions` and `write` bodies in the initial and
corrected harness scripts. `load_functions` writes the manifest before any case
runs (original harness lines 35-96, called at line 99). It records the same source
and body hashes, relative snippet paths, dependency descriptions and name-only
stubs. It contains no output-root path, run identifier or timestamp. Consequently,
an aborted invocation and a completed invocation can emit identical bytes.

The initial exception log records the harness exception-reporting typo; the final
stdout log records completion of all 24 scenarios. Along with the invocation
layout and generator control flow, these records associate the top-level manifest
with the aborted invocation. The explicitly designated **active completed-run
manifest is `failure-run-02/FUNCTION-DEPENDENCIES.json`**. Equal hashes alone neither
establish that association nor authenticate execution history. The manifests are
content descriptions, not run receipts.

## 3. Positive-control terminology

Use **unsuccessful positive-control attempts** for B omission, B delay and C delay.
They are attempts against deliberately insecure positive controls that did not
meet their declared endpoint on those particular trajectories. They are not a
separate negative-control arm, omitted observations, or successful defenses.

Historical JSON keys such as `negative_controls` and
`negative_control_attempts_retained` remain unchanged in the sealed originals.
Those quoted keys are historical labels; this amendment uses the corrected term.

## 4. Arithmetic checks are not receiver reconstruction

The retained-evidence checker reconstructs warranted scores from retained
outcomes, aggregates saved step scores, evaluates comparisons, and rebuilds
saved findings/control/root summaries. Inspection also shows it recomputes
reference step-score arithmetic from saved assembled arrays and, for PC1, receipt
increments using the **saved accepted-receipt list**. Those are conditional
arithmetic/consistency checks of retained data.

This does not independently decide which messages the receiver should have
accepted, reconstruct receipt-ledger membership from original schedules, or
establish the correctness of receiver dispositions, arrival order, winning IDs
or attribution. Descriptions of the arithmetic checker must not imply that broader
scope. The prior separate three-case receiver reconstruction remains attributed
to the user; its exact scripts/logs were not recovered and it was not rerun for
this amendment. The current derived harness executes only three synthetic
classifier cases and does not rerun the retained-evidence checker.

## 5. Derived publication and material omissions

The public evidence is a newly curated view, not the original results file. It
omits the other 21 scenarios, session/environment details, local filesystem paths,
timestamps and redundant descriptive fields. It retains the selected synthetic
input semantics, worker metadata, all returned case/root/family results and the
historical expected/assertion fields. The original assertion checked the three
root flags and failure count; it did **not** assert full family results or validate
every record. The new harness additionally compares the full recorded result.

Original byte hashes identify the originals, not these derived/redacted files.
CHECKSUMS.json separately covers the public files. The new harness is derived
from original script SHA-256
`637ce08cd8776542a483c5e5b3ce3bd3881e3b1a3ebf6e8e45ad8a5b1621deec`;
it is not represented as the exact historical script. Function bodies themselves
are verbatim excerpts, independently checked against the identified source ZIP.

## Public base and source availability

The publication base is `91474fe5268b90e059a5a637b07e3092ddf69c06`.
The three required historical source paths are absent at that revision.
`historical_excerpts.py` therefore supplies seven small function definitions, with
their original source lines, file hashes and body hashes. The complete archive is
not distributed, and historical execution source is not equated with public HEAD.

No repository LICENSE file/declaration was found at the base; the existing roadmap
leaves licensing unresolved. This amendment adds no license or third-party code.
It publishes only the project-supplied excerpts expressly authorized for this
review; it does not assert a new reuse license.
