import unittest, copy, numpy as np
from coupled_stream import Model,Coupler,ROOT,TAU
class Tests(unittest.TestCase):
    def c(self):return Coupler(ROOT/'assets/poster_encoded.rdssg',96,144,0)
    def test_model_topology(self):
        m=Model(42,.01);self.assertEqual(m.h['core_phi'].shape,(12,));self.assertEqual(m.h['batch_phi'].shape,(32,36))
    def test_lift_and_wrap(self):
        m=Model(42,.01);c=self.c()
        for i in range(16):
            f=m.next();r=c.consume(f);self.assertEqual(r['sequence'],i+1);self.assertLess(f['source_lift_error'],1e-10);self.assertEqual(r['winding36'],np.floor(np.array(f['phase36_lift'])/TAU).astype(int).tolist())
    def test_q28_and_qhtri(self):
        m=Model(42,.01);c=self.c()
        for _ in range(8):
            r=c.consume(m.next());self.assertEqual(r['q28']['n_qubits'],28);self.assertAlmostEqual(r['q28']['norm'],1,places=12);self.assertAlmostEqual(r['qhtri']['norm'],1,places=12);self.assertLess(r['qhtri']['potential_identity_error'],1e-14)
    def test_gap(self):
        m=Model(42,.01);c=self.c();c.consume(m.next());m.next()
        with self.assertRaisesRegex(ValueError,'discontinuous'):c.consume(m.next())
    def test_generation(self):
        m=Model(42,.01);c=self.c();c.consume(m.next());f=m.next();f['generation']='other'
        with self.assertRaisesRegex(ValueError,'discontinuous'):c.consume(f)
    def test_unknown_trits(self):
        m=Model(42,.01);c=self.c();self.assertIsNone(c.consume(m.next())['trits12'])
    def test_hold_distinct(self):
        m=Model(42,.01);c=self.c();f=m.next();f['trits12']=[-1,0,1]*4;self.assertEqual(c.consume(f)['trits12'],[-1,0,1]*4)
    def test_no_false_host(self):
        r=self.c().consume(Model(42,.01).next());self.assertFalse(r['host_authenticated']);self.assertFalse(r['physical_h200']);self.assertEqual(r['dynamic_hashing'],'NONE_IN_THIS_ROUTE')
    def test_render(self):
        m=Model(42,.01);c=Coupler(ROOT/'assets/poster_encoded.rdssg',96,144,1);p=c.consume(m.next());q=c.consume(m.next());self.assertTrue(p['rdssg']['rendered']);self.assertGreater(q['rdssg']['pixels_changed_from_previous_render'],0)
    def test_invalid(self):
        f=Model(42,.01).next();f['phase36_lift'][0]=float('nan')
        with self.assertRaises(ValueError):self.c().consume(f)
    def test_ekb_reciprocal(self):
        m=Model(42,.01); c=Coupler(ROOT/'assets/poster_encoded.rdssg',96,144,0,dict(D_lambda=.3,epsilon_nu=.15,K_D=.8,K_epsilon=.6,winding=0))
        for _ in range(64):
            f=m.next();f['trits12']=[-1,0,1]*4;r=c.consume(f)
            self.assertLess(r['ekb']['reciprocity_error'],1e-15);self.assertAlmostEqual(r['qhtri']['norm'],1,places=12)
        self.assertGreater(max(map(abs,r['ekb']['Q_feedback36_lift'])),.01);self.assertEqual(len(r['ekb']['bombelli_hold']),4)
        self.assertAlmostEqual(r['ekb']['source_expected_connection_integral'],2*np.pi*.45)
    def test_ekb_zero_control(self):
        m=Model(42,.01);a=self.c();b=Coupler(ROOT/'assets/poster_encoded.rdssg',96,144,0,dict(D_lambda=.3,epsilon_nu=.15,K_D=0,K_epsilon=0,winding=0))
        for _ in range(8):
            f=m.next();x=a.consume(f);y=b.consume(f)
            np.testing.assert_array_equal(x['phase36_lift'],y['phase36_lift']);np.testing.assert_array_equal(x['qhtri']['amplitude_real'],y['qhtri']['amplitude_real'])
    def test_ekb_missing_param(self):
        with self.assertRaises((ValueError,KeyError)):Coupler(ROOT/'assets/poster_encoded.rdssg',96,144,0,dict(D_lambda=.3))
    def test_physical_inputs(self):
        from ekb_bridge import EKB
        e=EKB(dict(cosmology=dict(Omega_lambda=.7),neutrino=dict(delta_m2_eV2=.0025,L_km=295,E_GeV=.6,mass_pair='31'),K_D=.8,K_epsilon=.6,winding=0))
        self.assertAlmostEqual(e.D,1.05);self.assertAlmostEqual(e.e,1.267/np.pi*.0025*295/.6)
    def test_lambda_radius(self):
        from ekb_bridge import EKB
        e=EKB(dict(cosmology=dict(Lambda_m_inv2=1e-52,R_H_m=1e26),neutrino=dict(delta_m2_eV2=0,L_km=295,E_GeV=.6),K_D=0,K_epsilon=0,winding=0))
        self.assertAlmostEqual(e.D,.5);self.assertEqual(e.e,0)
if __name__=='__main__':unittest.main(verbosity=2)
