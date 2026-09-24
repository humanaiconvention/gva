from itertools import product
from .types import Action
from .config import digest


def catalogue():
    values = set()
    for group in (range(4), range(4, 8)):
        for levels in product(range(3), range(2), range(2), range(2)):
            values.add(Action(*(tuple(level if i in group else 0 for i in range(8)) for level in levels)))
    values.add(Action(u=(1,) * 8))
    return tuple(sorted(values, key=lambda a: a.key))


CATALOGUE = catalogue()
NOOP = CATALOGUE.index(Action())
ALL_AID = CATALOGUE.index(Action(u=(1,) * 8))
CATALOGUE_HASH = digest([a.key for a in CATALOGUE])


def parse_id(value):
    if type(value) is not int or not 0 <= value < len(CATALOGUE):
        raise ValueError("Expected catalogue action ID")
    return CATALOGUE[value]
