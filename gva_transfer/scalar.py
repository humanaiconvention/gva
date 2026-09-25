"""Independent scalar physical, gate, reporting and score audit; no vector model imports."""
def clip(value): return max(0,min(1000,int(value)))

def permitted(action,previous,repaired):
    for i in range(8):
        if action.q[i] not in (0,1) or action.m[i] or action.e[i]: return False
        if repaired and action.q[i]==previous[i]==1: return False
    return sum(action.u)<=4

def step(coords,previous,action,noise,fatigue):
    out=[]
    for i in range(8):
        q,u,m,e=action.q[i],action.u[i],action.m[i],action.e[i]
        out.append([clip(coords[i][0]+60*q+30*u-10+noise[i][0]),
                    clip(coords[i][1]+40*u-40*q*q-fatigue*q*previous[i]-15*m-20*e+noise[i][1])])
    return out

def report(coords,action,sensor):
    return [[None,None] if action.e[i] else [clip(coords[i][j]+250*action.m[i]+sensor[i][j]) for j in range(2)] for i in range(8)]

def score(raw):
    values=[[0,0] if p[0] is None else p for p in raw]
    return (-sum(max(0,450-p[1]) for p in values),sum(p[0] for p in values))

def bank_action(coords,previous,proposed,noop,process,sensor,repaired):
    total=[0,0];states=[]
    for replica in range(8):
        action=proposed if permitted(proposed,previous[replica],repaired) else noop
        after=step(coords[replica],previous[replica],action,process[replica],20)
        values=score(report(after,action,sensor[replica]))
        total=[total[j]+values[j] for j in range(2)];states.append(after)
    return tuple(total),states
