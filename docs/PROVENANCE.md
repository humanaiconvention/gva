# Provenance and public-release boundary

GVA-0's confirmation completed on 24 September 2026 after a local pre-outcome commitment. The original preregistration SHA-256 is `65b02f083fe4c491ad8cac002028abfd1640937c52d98c4cedaea2dbe7ca5bd6`; the execution source digest is `dd8c7ab9b8327b1c8f11552a41064d07bb37d5da3d3b92aa8be43f25dec7aa29`; the original freeze-file SHA-256 is `c48fd4aa8133d0e4ead40d04e917437383ce73bc794c52351e3eaaa4fce437c4`.

The original scientific protocol is included byte-for-byte. Its historical draft/disabled wording describes the stage before execution was explicitly authorized. Before fresh outcomes, an execution addendum authorized the twenty-root run and documented namespace wiring, fixed audit roots, no interim outcome inspection and source/runtime locking. It did not change D_B, D_R, the bounds (.05,.20,.05,.20), sample size or comparison families.

The confirmation used roots 1000001..1000020 in `gva0-confirm-v0.5-displacement`. Root IDs, canonical named keys and all 1,220 actual 128-bit generator seeds were checked for disjointness from forty development roots, the developmental bank and calibration. Calibration was unchanged. All 820 episodes completed before the statistical analysis was released. No outcome-based exclusions, interim decisions, source changes or reruns occurred during confirmation.

## What the hashes verify

- `FREEZE.original.json` is the exact original commitment record. Some files it commits are intentionally not distributed; the public release does not pretend to contain the complete private archive.
- `original-source-hashes.json` contains the filename/hash map that reproduces the original aggregate source digest, without disclosing withheld source-document contents.
- `published-core-map.json` maps each distributed computational-core file to its exact original hash. All 23 files are byte-identical to the execution archive.
- `RELEASE-MANIFEST.json` separately identifies this curated public release. Publication wrappers and documentation are not represented as part of the earlier execution freeze.
- `runtime.public.json` retains software versions and the hardware description; the local interpreter path was removed and that redaction is declared.

The paper's public edition relocates local links and describes this distribution boundary without changing numerical results. Full raw event chains, prior development code archives and correspondence are retained privately. The published event anchors remain historical receipts; verifying their full original chains requires the retained originals. Reconstructed traces need not share byte-level log hashes because timing and wrapper metadata differ.

The portable publication wrapper is tested against all 820 archived outcome records. It uses the exact frozen physics, measurement, gate, score, seed and primary actor implementations. It is an author-provided reproduction aid; neither that wrapper nor the independently written scalar checks constitute an external replication.

Local hashes provide tamper evidence relative to their commitment under trusted storage. The later GitHub release is a public archive, not proof of an independently timestamped pre-outcome registration.
