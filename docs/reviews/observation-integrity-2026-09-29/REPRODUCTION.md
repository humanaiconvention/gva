# Reproduce the three classifier examples

Use Python 3.10 or later with its standard library. No dependency installation,
network access during execution, repository imports or full source ZIP is needed.
Start from a clean checkout/copy containing this review package. For this PR,
the review branch is `review/observation-integrity-20260929-150726`; the exact
historical public base is recorded in SOURCE-PROVENANCE.json. These functions do
not come from the current public implementation.

From the checkout root in PowerShell:

```powershell
$package = Join-Path (Get-Location) 'docs/reviews/observation-integrity-2026-09-29'
$output = Join-Path (Get-Location) ('reproduction-observation-' + [guid]::NewGuid().ToString('N'))
python -I -B (Join-Path $package 'reproduce_failure_cases.py') --package $package --output $output
if ($LASTEXITCODE -ne 0) { throw 'Classifier reproduction did not complete; existing logs were not overwritten.' }
Get-Content -LiteralPath (Join-Path $output 'stdout.txt')
Get-Content -LiteralPath (Join-Path $output 'RESULTS.json')
```

Do not add `>` or `2>` redirection to those commands. The harness itself creates
the fresh output directory before opening logs with exclusive mode. If that
directory already exists (including a file or symlink at the same name), it exits
2 without opening or replacing logs. Its parent must already exist. Errors after
directory creation exit 1, retaining any partial outputs under that directory.
No successful result is claimed on an exception or unexpected classification.

Explicit portable invocation, with an existing output parent and unused leaf:

```text
python -I -B docs/reviews/observation-integrity-2026-09-29/reproduce_failure_cases.py --package docs/reviews/observation-integrity-2026-09-29 --output reproduction-observation-001
```

All writes are confined to the selected output directory: three directories
containing 12 synthetic JSON inputs each, stdout.txt, stderr.txt and RESULTS.json.
`-B` suppresses bytecode writes; the script also sets `sys.dont_write_bytecode`.
The public files are read only. No random seeds are used; a UUID in the PowerShell
example only chooses a fresh directory name and does not affect test data/results.

## Exact execution scope

The harness parses `historical_excerpts.py`, checks its byte hash and each function
body hash, and compiles only the seven listed function-definition AST nodes. It
does not import that file or execute top-level archived modules. Original source
line locations are restored on the AST nodes without changing their bodies.

- Executed classification: archived `collect_root` and `root_campaign_status`.
- Result-file parsing: archived `read_json`, `strict_loads`, `_object`; `_constant`
  is supplied as the JSON callback. These three examples do not exercise its error
  branch. `_exact_float` is supplied but its exact-number branch is not exercised.
- Globals: standard-library json, pathlib.Path, decimal.Decimal/InvalidOperation,
  ordinary Python builtins, and declared attempt/family mappings.
- Stubs: SimpleNamespace objects supplying only the archived R1/control `.name`
  strings. No receiver constructor, scoring or acceptance method is provided.
- Constants: values in the evidence baseline were checked against archived
  ATTEMPTS, FAMILIES and CONTROL_FOR assignments; the public harness supplies
  those values rather than executing archived module-level assignments.

The original harness hash, exact source references and every stub origin are in
SOURCE-PROVENANCE.json. The input specification is baseline plus exact deltas,
checked during curation against all 12 original synthetic records for each case.

## Expected results and checks

| Case | Event | Unresolved R1 attempts | Known-witness flag | Case status counts |
|---|---|---|---|---|
| G-string-flag | true | false | true | 12 complete |
| G-short-circuit | true | false | true | 12 complete |
| I-fixture-mismatch | false | false | false | 12 complete |

No case failure records are returned. All family results must also equal the
recorded evidence: only replay has a true event in G-string-flag, only
reordering_delay in G-short-circuit, and no family in I-fixture-mismatch.
Success means reproduction of these recorded behaviors, not validation of the
supplied flags or approval of the policy.

RESULTS.json is deterministic: no timestamps, absolute paths, environment dumps
or session identifiers. Compare its bytes to the bundled
REPRODUCTION-RESULTS.json. A second fresh invocation should produce identical
results. Reusing the first output path must exit 2 and leave it unchanged. A
changed historical function body must produce a nonzero exit. These checks were
performed locally for this package, including reproduction from a fresh Git
checkout of the proposed review files. No full campaign or receiver run occurred.

CHECKSUMS.json covers exactly the public package files except itself. Paths are
package-relative; hashes describe their published bytes, not the sealed local
originals. It is an integrity inventory, not independent execution authentication.
