# Reproduction

Use CPython 3.13.14, install `requirements-replay.txt`, and run:

```sh
python scripts/verify_release.py
python reference/reproduce.py --output reproduction --traces
```

The output directory must not already exist. The fixed-root run is deterministic for outcomes under the pinned runtime. It checks every one of 820 cells against the published root-level metrics. Numerical tolerance is 1e-12; timings are not compared. The wrapper independently checks every live transition and measurement, all candidate scores on the first root, and every endpoint. It reruns the symbolic obligations before episodes.

`--smoke` uses only the first root (41 episodes), explicitly labeled as a smoke check. `--traces` adds reconstructed before/after states, reports, actions and named disturbances to a JSONL file. Generated files belong in ignored `reproduction*` directories, not in the release.

The distributed computational modules are exact copies from the frozen execution. `reference/reproduce.py` is a later portable wrapper that removes dependencies on the private workspace and historical artifact tree. Its full comparison receipt is published separately in provenance. No reproduction is added to the twenty-root inference, and executing these same roots again is not a second independent confirmation.

For an independently authored replication, start with the [written specification](INDEPENDENT-REPLICATION.md) before inspecting the implementation. Report whether you used the reference code, reused archived roots, or generated a prospectively specified new sample.
