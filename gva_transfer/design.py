from dataclasses import dataclass
from itertools import product
from gva0.actions import CATALOGUE
from gva0.types import Action

@dataclass(frozen=True)
class Challenge:
    name: str
    horizon: int
    fatigue: int = 20
    expanded: bool = False

CHALLENGES = (Challenge('REFERENCE',12), Challenge('SHORT',6), Challenge('LONG',24),
    Challenge('MILD',12,10), Challenge('HARSH',12,30), Challenge('EXPANDED',12,20,True), Challenge('JOINT',24,30,True))
OPTIMIZERS = ('GREEDY','BEAM2')
REPAIRS = ('report_repair','both')
CELLS = tuple(product(CHALLENGES, OPTIMIZERS, REPAIRS))
EXTRA = tuple(Action(q=(1,)*8,u=tuple(int(i//4 == group) for i in range(8))) for group in (0,1))

def catalogue(challenge):
    return CATALOGUE + EXTRA if challenge.expanded else CATALOGUE

def phase_design(phase, n=None):
    if phase == 'development':
        if n not in (None,40): raise ValueError('Exactly forty development roots')
        return 'gva1-transfer-development-v0.1', tuple(range(5000001,5000041))
    if phase != 'confirmation' or type(n) is not int or not 40 <= n <= 200:
        raise ValueError('Explicit calculated confirmation sample required')
    return 'gva1-transfer-confirm-v0.1', tuple(range(6000001,6000001+n))

def record():
    return dict(challenges=[vars(c) for c in CHALLENGES], optimizers=OPTIMIZERS, repairs=REPAIRS,
        replicas=8, beam_width=2, depth=2, alpha=.05/4, margins=[.01,-.02,.01,-.02],
        alternatives=[.03,0,.03,0], planning_sd_floor=.02, sample_range=[40,200])
