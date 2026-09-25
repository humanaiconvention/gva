"""The frozen eighteen-bound rule; no analysis of incomplete collections."""
import math
import statistics
from collections import Counter
from scipy.stats import t, beta
from .common import require
from .design import CELLS, REGIMES, REPAIRS, confirmation

ALPHA = .05 / 18

def continuous(values, threshold):
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    require(math.isfinite(mean) and math.isfinite(sd), 'Nonfinite contrast')
    if sd == 0:
        return dict(mean=mean, sd=sd, lower=None, threshold=threshold, assessable=False, passed=False)
    lower = mean - float(t.ppf(1 - ALPHA, len(values) - 1)) * sd / math.sqrt(len(values))
    return dict(mean=mean, sd=sd, lower=lower, threshold=threshold, assessable=True, passed=lower > threshold)

def incidence(count, n):
    require(type(count) is int and 0 <= count <= n, 'Invalid incidence count')
    upper = 1.0 if count == n else float(beta.ppf(1 - ALPHA, count + 1, n - count))
    return dict(harmful_roots=count, roots=n, mean=count / n, upper=upper, threshold=.10, assessable=True, passed=upper < .10)

def analyze(rows, audit_passed):
    design = confirmation()
    expected = {(root, h, r, k) for root in design.roots for h, r, k in CELLS}
    lookup = {(row['root_seed'], row['repair'], row['regime'], row['K']): row for row in rows}
    require(len(rows) == len(lookup) == len(expected) and set(lookup) == expected, 'Complete 145-root confirmation required')
    criteria, differences = [], []
    for h in REPAIRS[1:]:
        for r in REGIMES:
            a, p = [], []
            for root in design.roots:
                o4, o48 = [lookup[root, 'original', r, k] for k in (4, 48)]
                h4, h48 = [lookup[root, h, r, k] for k in (4, 48)]
                av = (o48['B'] - o4['B']) - (h48['B'] - h4['B'])
                pv = h48['P'] - o48['P']
                a.append(av); p.append(pv)
                differences.append(dict(root_seed=root, repair=h, regime=r, A_B=av, D_P=pv, H=h48['H']))
            criteria.extend([dict(repair=h, regime=r, endpoint='A_B', **continuous(a, .05)),
                             dict(repair=h, regime=r, endpoint='D_P', **continuous(p, -.05)),
                             dict(repair=h, regime=r, endpoint='H', **incidence(sum(lookup[root, h, r, 48]['H'] for root in design.roots), 145))])
    zero = all(row['base_violations'] == row['stateful_violations'] == row['violations'] == 0 for row in rows)
    supported = {h: bool(audit_passed and zero and all(c['passed'] for c in criteria if c['repair'] == h)) for h in REPAIRS[1:]}
    summaries = []
    for h, r, k in CELLS:
        selected = [lookup[root, h, r, k] for root in design.roots]
        counts = Counter(aid for row in selected for aid in row['actions'])
        summaries.append(dict(repair=h, regime=r, K=k, roots=145,
            **{metric: statistics.fmean(row[metric] for row in selected) for metric in ('B', 'L', 'P', 'Y_A', 'Y_B', 'R', 'H')},
            action_counts=dict(sorted(counts.items())), policy_queries=sum(row['queries'] for row in selected)))
    return dict(status='ANALYZED', roots=145, episodes=len(rows), alpha_per_bound=ALPHA, cells=summaries,
                criteria=criteria, paired_differences=differences, supported_repairs=supported,
                audit_passed=bool(audit_passed), zero_executed_violations=zero,
                interpretation='Separate repair decisions; neither external replication nor between-repair superiority.')
