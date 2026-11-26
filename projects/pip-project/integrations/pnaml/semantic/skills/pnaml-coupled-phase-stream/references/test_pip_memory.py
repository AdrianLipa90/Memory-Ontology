import math, tempfile, unittest, subprocess, sys, json
from pathlib import Path
import numpy as np
from coupled_stream import Model, Coupler, ROOT
from pip_memory import *

def event(id,op,**kw):return {'event_id':id,'op':op,'room_id':'room-a','t':0,'source_ref':'TEST_FIXTURE',**kw}
def register():return event('create','register',content_id='fixture:source-a',a=.2,lam=.1,address='7',status='DERIVED')
class Tests(unittest.TestCase):
    def test_kernel(self):
        self.assertEqual(kernel(0,1,2.69),1)
        self.assertAlmostEqual(kernel(2,1,3),1/9)
        self.assertGreater(kernel(2,1,2.69),kernel(2,1,3))
        self.assertAlmostEqual(attraction(1,.5,.9,2,1,3,.4),.5*.9*.4/9)
    def test_holonomy_gauge(self):
        r=np.random.default_rng(19);p=r.uniform(-math.pi,math.pi,(5,36));g=holonomy(p);h=holonomy(p+r.uniform(-3,3,(5,1)))
        self.assertLess(abs(np.angle(np.exp(1j*(g-h)))),1e-12)
        self.assertAlmostEqual(coherence([{'phase36_cycle':p,'weight':1}]),1)
        self.assertIsNone(coherence([]))
        self.assertIsNone(holonomy([np.zeros(36),[0]*18+[math.pi]*18]))
    def test_recall_and_decay(self):
        a=.2
        for _ in range(3):a=reinforce(a,.25,1,1)
        self.assertAlmostEqual(a,.6625)
        self.assertAlmostEqual(decay(a,math.log(2),1),.33125)
        self.assertAlmostEqual(entropy([.5,.5]),math.log(2))
        self.assertAlmostEqual(entropy([1,0]),0)
    def test_kick(self):
        r=memory_kick([0,0,1],[1,0,0],.5,[1,0],[0,1]); self.assertAlmostEqual(r['d_FS'],math.pi/4)
        self.assertAlmostEqual(r['delta_v'][0],math.pi/8);self.assertAlmostEqual(r['delta_h'],0)
        self.assertAlmostEqual(r['delta_E'],.5*(math.pi/8)**2)
        self.assertEqual(memory_kick([0,0,1],[0,0,-1],.5,[1,0],[0,1])['status'],'ANTIPODAL_CHART_UNRESOLVED')
    def test_kepler_and_transport(self):
        r=kepler_segment([1,0],[0,1],1,2*math.pi,10000)
        self.assertLess(np.linalg.norm(np.asarray(r['position'])-[1,0]),1e-5)
        self.assertLess(abs(r['final']['h']-r['initial']['h']),1e-12)
        a=transport_frame([0,0,1],[1,0,0],[1,0,0]);self.assertTrue(np.allclose(a['e_Q'],[0,0,-1]));self.assertTrue(np.allclose(a['e_P'],[0,1,0]))
    def test_orbit_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'journal.sqlite3');m=Memory(path);m.commit(register())
            m.commit(event('orbit','orbit_init',position=[1,0],velocity=[0,1],mu=1))
            m.commit(event('kick','orbit_kick',n=[0,0,1],b=[1,0,0],q=.2));m.commit(event('segment','orbit_segment',t=1,steps=1000));expected=m.rooms.copy();m.close()
            m=Memory(path);self.assertEqual(m.rooms,expected);self.assertEqual(m.store.verify()['status'],'PASS');m.close()
    def test_replay_fresh_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'journal.sqlite3');m=Memory(path)
            m.commit(register());m.commit(event('recall','recall',t=1,eta=.25,q=1,rho=1));m.commit(event('visit','visit',t=1));m.commit(event('route','collatz',t=1));before=m.rooms.copy();m.close()
            out=subprocess.run([sys.executable,str(ROOT/'pip_memory.py')],input=json.dumps({'operation':'restore','store_path':path}),text=True,capture_output=True,check=True);rest=json.loads(out.stdout)
            self.assertEqual(rest['rooms'],before);self.assertEqual(rest['current_room'],'room-a');self.assertEqual(rest['journal']['status'],'PASS');self.assertEqual(rest['journal']['events_checked'],4)
            m=Memory(path);self.assertEqual(m.commit(event('route','collatz',t=1))['status'],'DUPLICATE');self.assertEqual(m.rooms,before);m.close()
    def test_counterfactual(self):
        m=Memory();m.commit(register());b={**register(),'event_id':'create-b','room_id':'room-b','content_id':'fixture:source-b'};m.commit(b)
        query=[{'room_id':k,'rho':1,'distance':1,'relation_match':1} for k in ('room-a','room-b')]
        m.commit({**event('recall-b','recall',eta=.25,q=1,rho=1),'room_id':'room-b'});self.assertEqual(m.rank(query,0,1,3,1)[0]['room_id'],'room-b')
        m.commit(event('recall-a1','recall',eta=.25,q=1,rho=1));m.commit(event('recall-a2','recall',eta=.25,q=1,rho=1));self.assertEqual(m.rank(query,0,1,3,1)[0]['room_id'],'room-a')
    def test_producer_feedback(self):
        m=Model(42,.01);baseline=Model(42,.01);goal=np.linspace(-3,3,36);f=m.next({'target_phase36':goal.tolist(),'source_ref':'TEST_FIXTURE'});b=baseline.next()
        self.assertLess(np.max(abs(np.angle(np.exp(1j*(goal-np.asarray(f['phase36_lift'])))))),1e-12)
        self.assertLess(f['producer_feedback']['phase_error'],1e-12)
        self.assertFalse(np.array_equal(m.h['batch_phi'],baseline.h['batch_phi']));self.assertFalse(np.array_equal(m.h['batch_g'],baseline.h['batch_g']))
        self.assertTrue(np.array_equal(m.h['batch_omega'],baseline.h['batch_omega']))
        c=Coupler(ROOT/'assets/poster_encoded.rdssg',48,72,0);r=c.consume(f);self.assertEqual(r['producer_feedback'],f['producer_feedback']);self.assertAlmostEqual(r['qhtri']['norm'],1,places=12);self.assertIs(c.pip.noema_surface,c.noema_surface)
        self.assertFalse(np.allclose(m.next()['phase36_lift'],baseline.next()['phase36_lift']))
    def test_pip_memory_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'journal.sqlite3');cfg={'memory':{'store_path':path,'events':[{'sequence':1,'command':register()},{'sequence':2,'command':event('visit','visit',t=1)}]}}
            c=Coupler(ROOT/'assets/poster_encoded.rdssg',48,72,0,pip=cfg);m=Model(42,.01);c.consume(m.next());r=c.consume(m.next());self.assertEqual(r['pip']['Sigma']['room']['address'],'7');c.pip.memory.close()
            c=Coupler(ROOT/'assets/poster_encoded.rdssg',48,72,0,pip={'memory':{'store_path':path}});r=c.consume(Model(42,.01).next());self.assertEqual(r['pip']['Sigma']['room']['address'],'7');self.assertEqual(r['pip']['memory']['event_count'],2);c.pip.memory.close()
if __name__=='__main__':unittest.main(verbosity=2)
