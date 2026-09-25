from dataclasses import dataclass
from . import ROOT
from .common import read, require, sha, digest

REPAIRS = ('original', 'report_repair', 'contract_repair', 'both')
REGIMES = ('NOMINAL', 'PHYSICAL_SHIFT')
CELLS = tuple((h, r, k) for h in REPAIRS for r in REGIMES for k in (4, 48))
PROTOCOL = ROOT / 'gva1-preregistration'
INPUT_HASHES = {
    'PREREGISTRATION.md': '44d65a132eaf44be7a29d28811944e2701b22c5acbf8d8764fa68fa47d0aca94',
    'settings.json': 'f6a4ffb1990ff6f3b618706db0c800348788d1d8ad6eaf75c80978c9a7efb45a',
    'sample-size.json': 'b325756623a9af2cd9049f9aca9d3658f0157e7e0ed32bf84008237e09c746ec',
    'SEED-COMMITMENT.json': '46b97074672a2c073f1f93dd19fd1ee137652f5b1cac1e6f2d105e7e950c403e',
}

@dataclass(frozen=True)
class Design:
    mode: str
    namespace: str
    roots: tuple
    audit_roots: tuple

    def record(self):
        return dict(mode=self.mode, namespace=self.namespace, roots=list(self.roots),
                    audit_roots=list(self.audit_roots), cells=[list(c) for c in CELLS])

def development(roots=None):
    roots = tuple(range(3000001, 3000041)) if roots is None else tuple(roots)
    require(bool(roots) and all(type(r) is int and 3000001 <= r <= 3000040 for r in roots), 'Development roots only')
    require(tuple(sorted(set(roots))) == roots, 'Ordered unique development roots required')
    # Same audit positions as the pilot; small fixtures audit their first root.
    audits = tuple(r for r in roots if r in (3000001, 3000020, 3000040)) or roots[:1]
    return Design('development', 'gva1-development-repair-v0.1', roots, audits)

def confirmation():
    return Design('confirmation', 'gva1-confirm-repair-v0.1', tuple(range(4000001, 4000146)),
                  (4000001, 4000020, 4000145))

def validate_design(design):
    require(isinstance(design, Design), 'Explicit design required')
    expected = confirmation() if design.mode == 'confirmation' else development(design.roots)
    require(design == expected, 'Namespace, roots or audit positions changed')

def verify_inputs():
    for name, expected in INPUT_HASHES.items():
        require(sha(PROTOCOL / name) == expected, 'Prospective input changed: ' + name)
    commitment = read(PROTOCOL / 'COMMITMENT.json')
    for name, expected in commitment['files'].items():
        require(sha(PROTOCOL / name) == expected, 'Protocol commitment mismatch: ' + name)
    require(read(PROTOCOL / 'sample-size.json')['selected_roots'] == 145, 'Sample size changed')
    require(read(PROTOCOL / 'SEED-COMMITMENT.json')['roots'] == list(confirmation().roots), 'Root commitment changed')
    original = read(ROOT / 'provenance/original-source-hashes.json')['files']
    for public, old in read(ROOT / 'provenance/published-core-map.json').items():
        require(sha(ROOT / public) == original[old], 'Frozen reference changed: ' + public)
    return digest(INPUT_HASHES)
