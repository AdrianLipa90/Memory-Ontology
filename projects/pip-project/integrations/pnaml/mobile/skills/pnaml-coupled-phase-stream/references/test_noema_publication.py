import json, math, unittest
from pathlib import Path
from unittest.mock import patch
from noema_publication import Publications, lift_rdssg, interval_squared, ROOT

# Explicit isolated fixture; not native RDSSG or measured AUX.
SCENE={'domain':{'reference_grid':[100,200]},'materials':[{'id':0,'projection_z':-.05},{'id':1,'projection_z':.025}],
       'vector_geometry':{'classes':[{'material_id':0},{'material_id':1}]},'rdss':{'cluster_order':[0,1],'native_RDSS_registry':'UNRESOLVED'}}
def unpack(obj): return [(obj['material_id'],[(0,0),(3,5),(99,199)])]
class Term:
    def manifest(self):return {'PHASENAV_Q28_CIRCUIT':{'mutates':False}}
    def execute(self,packet):return {'owner_test_fixture':True,'packet':packet}
def frame(seq,trits=None):return dict(source='TEST_FIXTURE',generation='fixture',sequence=seq,tau=seq*.1,phase36_lift=[float(seq)]*36,winding36=[0]*36,trits12=trits,rdssg={'rendered':False},q28={'n_qubits':28})

class PublicationsTest(unittest.TestCase):
    def setUp(self):self.p=Publications();self.t=Term()
    def test_unbound_no_invention(self):
        self.assertEqual(self.p.read('MINKOWSKI')['status'],'AWAITING_FRAME')
        self.assertEqual(self.p.read('TERMINAL36D')['status'],'AWAITING_OWNER')
    def test_lift_preserves_vertex_order_depth_and_material(self):
        r=lift_rdssg(SCENE,.5,unpack)
        self.assertEqual(r['vertex_count'],6); self.assertEqual(r['classes'][1]['paths'][0]['contour_depth'],1)
        self.assertEqual(r['classes'][0]['paths'][0]['events'][0],[.5,.005,.0025,-.05])
        self.assertEqual(r['classes'][1]['paths'][0]['events'][-1],[.5,.995,.9975,.025])
        self.assertFalse(r['physical_metric_verified']);self.assertFalse(r['rdss_fractal_metric_equivalence'])
    def test_interval_and_boost(self):
        a=[0,0,0,0];b=[2,1,.2,.3];v=.6;g=1/math.sqrt(1-v*v)
        boost=lambda x:[g*(x[0]-v*x[1]),g*(x[1]-v*x[0]),x[2],x[3]]
        self.assertAlmostEqual(interval_squared(a,b),interval_squared(boost(a),boost(b)))
        self.assertEqual(interval_squared(a,[1,1,0,0]),0)
        self.assertLess(interval_squared(a,[1,0,0,0]),0)
        self.assertGreater(interval_squared(a,[0,1,0,0]),0)
    def test_bound_owner_and_frame_lineage(self):
        self.p.attach(SCENE,self.t,unpack); self.p.bind(frame(1,[-1,0,1]*4)); a=self.p.read('MINKOWSKI')
        self.p.bind(frame(2));b=self.p.read('MINKOWSKI')
        self.assertIs(self.p.terminal,self.t);self.assertIs(self.p.scene,SCENE)
        self.assertEqual(a['sequence'],1);self.assertEqual(b['sequence'],2);self.assertIsNone(b['trits12'])
        self.assertEqual(b['phase36_lift'],[2.]*36);self.assertEqual(b['classes'][0]['paths'][0]['events'][0][0],.2)
        self.assertEqual(self.p.read('RDSS')['rdss']['cluster_order'],[0,1]);self.assertEqual(self.p.read('RDSSG')['sequence'],2)
        self.assertEqual(self.p.read('TERMINAL36D/Q28')['result']['n_qubits'],28)
    def test_dispatch_existing_owner(self):
        self.p.attach(SCENE,self.t,unpack); packet={'operation':'PHASENAV_Q28_CIRCUIT'}
        self.assertIs(self.p.dispatch_terminal(packet)['packet'],packet)
        with self.assertRaises(ValueError):self.p.dispatch_terminal({'operation':'PHASENAV_WRITE_CANDIDATE'})
    def test_source_registry(self):
        r=json.loads((ROOT/'pncs-v019-source-registry.json').read_text());self.assertEqual(len(r['records']),27)
        self.assertTrue(r['no_semantic_relabel']);self.assertEqual({v['layer'] for v in r['records']},{'definitions','classes','files','clusters','hierarchy'})
        cw={'source':'fixture','commit':'fixture','entries':[{'source_id':'CLX2-FIXTURE','pnaml_address':121}]}
        with patch.object(self.p,'_crosswalk',return_value=cw):
            self.assertEqual(self.p.read('PNCS')['source_registry_count'],27)
            self.assertEqual(self.p.read('PNCS/REGISTRY')['archive_sha256'],r['archive_sha256'])
            self.assertEqual(self.p.read('PNCS/CD/121')['source_id'],'CLX2-FIXTURE')
    def test_dictionary_routing(self):
        with patch.object(self.p,'_cd',return_value={'fixture':True}) as cd:
            self.assertEqual(self.p.read('CD/CLX2-META-001'),{'fixture':True}); cd.assert_called_once_with('lookup','CLX2-META-001')
        with self.assertRaises(KeyError):self.p.read('RDSS/NO_SUCH')

if __name__=='__main__':unittest.main(verbosity=2)
