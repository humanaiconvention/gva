import unittest
from itertools import product
import json
import tempfile
from pathlib import Path
import numpy as np
import gva_transfer
from gva_transfer.design import Challenge,CHALLENGES,CELLS,catalogue
from gva_transfer.model import allowed,transition,reports,numerators,Oracle,Batch
from gva_transfer import scalar,planners
from gva_transfer.engine import episode,endpoints
from gva_transfer.commitment import seeds
from gva_transfer.analysis import plan,analyze
from gva_transfer.runner import execute,verify_root
from gva0.logging import EventWriter
from gva1.common import atomic_json,sha

class TransferTests(unittest.TestCase):
    def test_finite_contract_all_histories(self):
        actions=catalogue(Challenge('fixture',12,20,True))
        self.assertEqual(len(actions),50)
        for history in product((0,1),repeat=8):
            for repaired in (False,True):
                for action in actions:
                    self.assertEqual(allowed(action,np.array(history),repaired),scalar.permitted(action,history,repaired))
        for action in actions[48:]: self.assertTrue(scalar.permitted(action,[0]*8,False))

    def test_vector_scalar_clipping_reporting(self):
        coords=np.array([[0,1000],[1000,0],[430,460],[470,340]]*2)
        previous=np.array([1,0]*4);noise=np.array([[-5,5],[5,-5]]*4)
        for action in catalogue(CHALLENGES[-1]):
            for fatigue in (10,20,30):
                after=transition(coords,previous,action,noise,fatigue)
                self.assertEqual(after.tolist(),scalar.step(coords.tolist(),previous.tolist(),action,noise.tolist(),fatigue))
                raw=reports(after,action,noise)
                self.assertEqual(numerators(raw),scalar.score(scalar.report(after.tolist(),action,noise.tolist())))

    def test_report_repair_before_clipping(self):
        action=catalogue(CHALLENGES[0])[20]
        coords=np.full((8,2),980);sensor=np.zeros((8,2),dtype=int)
        raw=reports(coords,action,sensor)
        self.assertTrue(np.all(raw==980))
        self.assertEqual(numerators(np.full((8,2),np.nan)),(-3600,0))

    def test_two_step_changes_decision(self):
        def query(handle):
            if handle is None: return Batch((0,1,2),((-100,0),(0,10),(0,9)),((0,),(1,),(2,)))
            future=0 if handle==(1,) else 20
            return Batch((0,1,2),((0,future),(-100,0),(-100,0)),())
        self.assertEqual(planners.greedy(query,2)[0],1)
        self.assertEqual(planners.beam2(query,2)[0],2)
        self.assertEqual(planners.beam2(query,1)[0],1)

    def test_noop_and_id_ties(self):
        def query(handle): return Batch((0,1,2),((0,0),)*3,((0,),(1,),(2,)))
        self.assertEqual(planners.greedy(query,2)[0],0)
        self.assertEqual(planners.beam2(query,2)[0],0)

    def test_branch_history_and_full_scalar_layers(self):
        coords=np.full((8,2),500);previous=np.ones(8,dtype=int)
        oracle=Oracle(coords,previous,3000001,2,'gva1-development-repair-v0.1',catalogue(CHALLENGES[-1]),True,audit=True)
        first=oracle.batch();self.assertEqual(oracle.layers[0]['executed_ids'][20],0)
        oracle.batch(first.handles[20]);self.assertEqual(oracle.layers[1]['executed_ids'][20],20)
        self.assertEqual(oracle.audit_replicas,800)
        with self.assertRaises(RuntimeError): oracle.batch(first.handles[20])
        with self.assertRaises(RuntimeError): oracle.batch((20,20,20))

    def test_archived_reference_decisions_and_endpoints(self):
        golden=json.loads((gva_transfer.ROOT/'tests/gva1/pilot-golden.json').read_text())
        for root in (3000001,3000020,3000040):
            for repair in ('report_repair','both'):
                for regime,fatigue in (('NOMINAL',20),('PHYSICAL_SHIFT',40)):
                    old=next(r for r in golden if (r['root_seed'],r['repair'],r['regime'],r['K'])==(root,repair,regime,48))
                    rows=[]
                    got=episode(root,'gva1-development-repair-v0.1',Challenge('compatibility',12,fatigue),'GREEDY',repair,rows.append)
                    self.assertEqual(got['actions'],old['actions'])
                    for key in ('B','P','L','Y_A','Y_B','R','H','harm_count'):
                        self.assertAlmostEqual(got[key],old[key],places=12)
                    self.assertEqual(got['policy_queries'],4608)

    def test_preview_isolation_and_horizon(self):
        for challenge in (CHALLENGES[1],CHALLENGES[-1]):
            events=[]
            row=episode(3000001,'gva1-development-repair-v0.1',challenge,'BEAM2','both',events.append,audit=True)
            a=len(catalogue(challenge));h=challenge.horizon
            self.assertEqual(len(events),h)
            self.assertEqual(row['policy_queries'],a*8*(3*(h-1)+1))
            self.assertEqual(row['scalar_audit_replicas'],row['policy_queries'])
            self.assertTrue(all(e['preview_fatigue']==20 for e in events))
            self.assertEqual(events[-1]['live_fatigue'],challenge.fatigue)
            self.assertEqual(len(events[-1]['preview_layers']),1)
            self.assertEqual(row['violations'],0)

    def test_seed_separation(self):
        self.assertEqual(seeds('development')['stream_count'],5800)
        self.assertTrue(seeds('confirmation',40)['collision_checked'])

    def test_no_execution_without_activation(self):
        with self.assertRaisesRegex(RuntimeError,'activation'):
            execute('confirmation','nonexistent','nonexistent')

    def test_planning_ignores_means_and_respects_floor_cap(self):
        data=np.array([[.001*i,.0005*i,.0002*i,.0004*i] for i in range(40)])
        a,b=plan(data),plan(data+10)
        self.assertEqual(a['selected_roots'],b['selected_roots'])
        self.assertEqual(len(a['grid']),161)
        self.assertTrue(all(v>=.0004 for v in a['planning_variances']))
        huge=plan(np.array([[(-1)**i]*4 for i in range(40)]))
        self.assertIsNone(huge['selected_roots'])

    def test_zero_variance_does_not_support_superiority(self):
        rows=[]
        for root in range(40):
            for c,o,h in CELLS:
                rows.append(dict(root=root,challenge=c.name,optimizer=o,repair=h,B=0,P=.5,L=.5,Y_A=.5,Y_B=.5,
                    H=0,R=0,harm_count=0,actions=[0]*c.horizon,policy_queries=0,violations=0))
        result=analyze(rows,list(range(40)))
        self.assertFalse(result['superiority_supported'])
        self.assertTrue(all(c['lower'] is None for c in result['criteria']))
        with self.assertRaisesRegex(RuntimeError,'Incomplete'):
            analyze(rows[:-1],list(range(40)))

    def test_whole_root_trace_reconstruction_and_corruption(self):
        with tempfile.TemporaryDirectory(prefix='gva-transfer-fixture-') as name:
            folder=Path(name)
            writer=EventWriter(folder/'events.jsonl')
            rows=[episode(3000001,'gva1-development-repair-v0.1',c,o,h,writer.append) for c,o,h in CELLS]
            anchor=writer.close()
            atomic_json(folder/'metrics.json',rows)
            atomic_json(folder/'COMPLETE.json',dict(root=3000001,identity='fixture',anchor=anchor,
                events_sha256=sha(folder/'events.jsonl'),metrics_sha256=sha(folder/'metrics.json')))
            rebuilt,_=verify_root(folder,'fixture','gva1-development-repair-v0.1',3000001,False)
            self.assertEqual(rebuilt,rows)
            rows[0]['B']+=.1
            atomic_json(folder/'metrics.json',rows)
            with self.assertRaisesRegex(RuntimeError,'hashes'):
                verify_root(folder,'fixture','gva1-development-repair-v0.1',3000001,False)

if __name__=='__main__':unittest.main()
