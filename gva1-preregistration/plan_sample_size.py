"""Recompute the prospective GVA-1 repair sample from new pilot contrasts only."""
from pathlib import Path
import json
import numpy as np
from scipy.stats import beta,binom,chi2,nct,t

def calculate(matrix):
    assert matrix.shape==(40,12) and np.isfinite(matrix).all()
    variances=matrix.var(axis=0,ddof=1)
    assert (variances>0).all()
    inflation=39/chi2.ppf(.05/12,39)
    alpha=.05/18;grid=[]
    for N in range(40,501):
        critical=t.ppf(1-alpha,N-1)
        powers=[nct.sf(critical,N-1,np.array([.03,.05]*6)/np.sqrt(variances*scale/N)) for scale in (1,inflation)]
        accepted=[k for k in range(N) if beta.ppf(1-alpha,k+1,N-k)<.10]
        binary=float(binom.cdf(max(accepted),N,.01)) if accepted else 0.0
        bounds=[max(0.0,1-float(np.sum(1-p))-6*(1-binary)) for p in powers]
        grid.append(dict(N=N,joint_lower_base=bounds[0],joint_lower_inflated=bounds[1],incidence_power=binary))
        if min(bounds)>=.90:return N,variances,float(inflation),grid
    return None,variances,float(inflation),grid

if __name__=='__main__':
    base=Path(__file__).resolve().parent
    matrix=np.asarray(json.loads((base/'pilot-contrast-matrix.json').read_text()))
    N,variances,inflation,grid=calculate(matrix)
    archived=json.loads((base/'sample-size.json').read_text())
    assert N==archived['selected_roots']==145
    assert np.allclose(variances,archived['continuous_variances'],rtol=0,atol=1e-15)
    for computed,old in zip(grid,archived['grid']):
        assert computed['N']==old['N']
        assert abs(computed['joint_lower_inflated']-old['joint_power_union_lower_inflated_variance'])<1e-12
    print(json.dumps(dict(status='VERIFIED',roots=N,episodes=16*N,variance_inflation=inflation,selected=grid[-1],preceding=grid[-2])))
