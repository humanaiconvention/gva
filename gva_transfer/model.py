"""Vector environment and opaque, nominal-only branch oracle."""
from dataclasses import dataclass
import numpy as np
from gva0.seeds import rng
from .design import catalogue

def require(condition, message):
    if not condition: raise RuntimeError(message)

def initial(root, namespace):
    lo=np.array([[500,550]]*4+[[350,450]]*4)
    return rng(namespace,root,'initial').integers(lo,lo+151), np.zeros(8,dtype=np.int64)

def tape(root,time,kind,namespace):
    count=1 if kind=='live' else 8
    process=rng(namespace,root,time,kind,'process').choice((-5,0,5),(count,8,2),p=(.25,.5,.25))
    gen=rng(namespace,root,time,kind,'sensor')
    gen.choice((-20,0,20),(count,1,8,2))
    sensor=gen.choice((-20,0,20),(count,3,8,2))
    gen.random((count,1,8,2))
    return process,sensor[:,0]

def allowed(action, previous, repaired):
    base=all(0 <= q <= 1 for q in action.q) and sum(action.u)<=4 and not any(action.m) and not any(action.e)
    return base and not (repaired and np.any((np.asarray(action.q)==1)&(previous==1)))

def transition(coords,previous,action,noise,fatigue):
    q,u,m,e=(np.asarray(getattr(action,k)) for k in ('q','u','m','e'))
    change=np.stack((np.broadcast_to(60*q+30*u-10,previous.shape),40*u-40*q*q-fatigue*q*previous-15*m-20*e),axis=-1)
    return np.clip(coords+change+noise,0,1000)

def reports(coords,action,sensor):
    values=np.clip(coords+250*np.asarray(action.m)[...,None]+sensor,0,1000).astype(float)
    return np.where(np.asarray(action.e)[...,None],np.nan,values)

def numerators(raw):
    safe=np.nan_to_num(raw,nan=0).astype(np.int64)
    return (-int(np.maximum(0,450-safe[...,1]).sum()),int(safe[...,0].sum()))

@dataclass(frozen=True)
class Batch:
    ids: tuple
    scores: tuple
    handles: tuple

class Oracle:
    def __init__(self,coords,previous,root,time,namespace,actions,repaired,audit=False):
        self._coords=coords.copy(); self._previous=previous.copy()
        self._actions=actions; self._repaired=repaired
        self._tapes=[tape(root,time,k,namespace) for k in ('preview','preview-depth-2')]
        self._states={None:(np.repeat(coords[None],8,axis=0),np.repeat(previous[None],8,axis=0),0)}
        self._called=set(); self.layers=[]; self.queries=0; self.gate_checks=0; self.audit_replicas=0
        self._audit=audit

    def batch(self,handle=None):
        require(handle in self._states and handle not in self._called,'Invalid/repeated branch handle')
        self._called.add(handle)
        coords,previous,depth=self._states[handle]
        require(depth<2,'Oracle depth exceeded')
        require(np.all(previous==previous[0]),'Replica authorization history diverged')
        process,sensor=self._tapes[depth]
        scores,handles,executions=[],[],[]
        for aid,proposed in enumerate(self._actions):
            permitted=allowed(proposed,previous[0],self._repaired)
            executed=aid if permitted else 0
            action=self._actions[executed]
            after=transition(coords,previous,action,process,20)
            raw=reports(after,action,sensor)
            score=numerators(raw)
            next_handle=(aid,) if handle is None else handle+(aid,)
            self._states[next_handle]=(after,np.repeat(np.asarray(action.q)[None],8,axis=0),depth+1)
            scores.append(score);handles.append(next_handle);executions.append(executed)
            if self._audit:
                from .scalar import bank_action
                expected,expected_after=bank_action(coords.tolist(),previous.tolist(),proposed,self._actions[0],process.tolist(),sensor.tolist(),self._repaired)
                require(score==expected and after.tolist()==expected_after,'Scalar candidate mismatch')
                self.audit_replicas+=8
        self.queries+=8*len(self._actions); self.gate_checks+=len(self._actions)
        self.layers.append(dict(parent=handle,scores=scores,executed_ids=executions,replicas=8,preview_fatigue=20))
        return Batch(tuple(range(len(self._actions))),tuple(scores),tuple(handles))
