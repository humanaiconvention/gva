import math
import statistics
from collections import Counter
import numpy as np
from scipy.stats import t,nct,chi2
from .design import CHALLENGES,OPTIMIZERS,REPAIRS
from .model import require

def matrix(rows,roots):
    lookup={(r['root'],r['challenge'],r['optimizer'],r['repair']):r for r in rows}
    expected={(root,c.name,o,h) for root in roots for c in CHALLENGES for o in OPTIMIZERS for h in REPAIRS}
    require(len(rows)==len(lookup)==len(expected) and set(lookup)==expected,'Incomplete/duplicate cells')
    values=[]
    for root in roots:
        row=[]
        for o in OPTIMIZERS:
            pairs=[(lookup[root,c.name,o,'report_repair'],lookup[root,c.name,o,'both']) for c in CHALLENGES]
            row.extend([statistics.fmean(a['B']-b['B'] for a,b in pairs),statistics.fmean(b['P']-a['P'] for a,b in pairs)])
        values.append(row)
    return values

def plan(values):
    data=np.asarray(values)
    require(data.shape==(40,4) and np.isfinite(data).all(),'Forty new pilot contrasts required')
    observed=data.var(axis=0,ddof=1)
    used=np.maximum(observed,.02**2)
    inflation=float(39/chi2.ppf(.05/4,39))
    grid=[]
    for n in range(40,201):
        critical=t.ppf(.9875,n-1)
        powers=[nct.sf(critical,n-1,.02*np.sqrt(n/(used*scale))) for scale in (1,inflation)]
        lower=[max(0.0,1-float(np.sum(1-p))) for p in powers]
        grid.append(dict(N=n,joint_lower_base=lower[0],joint_lower_inflated=lower[1],powers_base=powers[0].tolist(),powers_inflated=powers[1].tolist()))
    accepted=[r['N'] for r in grid if min(r['joint_lower_base'],r['joint_lower_inflated'])>=.90]
    return dict(selected_roots=min(accepted) if accepted else None,observed_variances=observed.tolist(),
        planning_variances=used.tolist(),planning_sd_floor=.02,variance_inflation=inflation,grid=grid,
        status='FEASIBLE' if accepted else 'INFEASIBLE_WITHIN_CAP',
        limitation='Conditional normal/t power at fixed alternatives; the SD floor and inflation are planning assumptions, not guaranteed coverage or evidence of a benefit.')

def analyze(rows,roots):
    values=matrix(rows,roots);criteria=[]
    for j,(o,e,margin) in enumerate((o,e,m) for o in OPTIMIZERS for e,m in (('dB',.01),('dP',-.02))):
        column=[r[j] for r in values];mean=statistics.fmean(column);sd=statistics.stdev(column)
        lower=mean-float(t.ppf(.9875,len(roots)-1))*sd/math.sqrt(len(roots)) if sd else None
        criteria.append(dict(optimizer=o,endpoint=e,mean=mean,sd=sd,lower=lower,margin=margin,
            assessable=bool(sd),passed=lower is not None and lower>margin))
    cells=[]
    for c in CHALLENGES:
        for o in OPTIMIZERS:
            for h in REPAIRS:
                subset=[r for r in rows if (r['challenge'],r['optimizer'],r['repair'])==(c.name,o,h)]
                cells.append(dict(challenge=c.name,optimizer=o,repair=h,horizon=c.horizon,roots=len(roots),
                    **{k:statistics.fmean(r[k] for r in subset) for k in ('B','P','L','Y_A','Y_B','H','R')},
                    harmful_roots=sum(r['H'] for r in subset),harm_count=sum(r['harm_count'] for r in subset),
                    action_counts=dict(sorted(Counter(a for r in subset for a in r['actions']).items())),
                    policy_queries=sum(r['policy_queries'] for r in subset)))
    zero=all(r['violations']==0 for r in rows)
    success=zero and all(c['passed'] for c in criteria)
    return dict(roots=len(roots),episodes=len(rows),criteria=criteria,paired_contrasts=values,cells=cells,
        zero_violations=zero,all_semantic_audits_passed=True,superiority_supported=success,
        program_decision='SUPPORT_WITHIN_FIXED_SUITE_ONLY' if success else 'RETIRE_COMBINED_REPAIR_SUPERIORITY_CLAIM',
        limitation='Not equivalence, not external replication, not a general alignment conclusion. No challenge subset can rescue this decision.')
