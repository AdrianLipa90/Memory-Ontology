import math
import unittest
from cmath import exp
from engines import rdss_relational_dynamics_v32 as m

class RelationalDynamics(unittest.TestCase):
    def test_activity(self):
        self.assertEqual(m.activity(3,3),(6,0,0))
        self.assertEqual(m.duration([(3,3,2),(1,1,1)]),14)
        self.assertEqual(m.lapse((3,3),(1,1)),3)
    def test_seams(self):
        a,b,phi=2+1j,3-2j,.7
        s,d=m.seam(a,b,phi)
        self.assertAlmostEqual(abs(s)**2+abs(d)**2,(abs(a)**2+abs(b)**2)/2)
        aa,bb=m.seam_inverse(s,d,phi)
        self.assertAlmostEqual(abs(aa-a)+abs(bb-b),0)
        ss,dd=m.seam(a*exp(.2j),b*exp(-.8j),phi-1)
        self.assertAlmostEqual(abs(ss),abs(s))
        self.assertAlmostEqual(abs(dd),abs(d))
        s2,d2=m.seam(a,b,phi+2*math.pi)
        self.assertAlmostEqual(abs(s+s2)+abs(d+d2),0)
        left,pairs,right=m.chain_seams([a,b,1j],[phi,.1])
        self.assertAlmostEqual(abs(left)**2+abs(right)**2+sum(abs(x)**2+abs(y)**2 for x,y in pairs),abs(a)**2+abs(b)**2+1)
    def test_wilson(self):
        A=((exp(1j*math.pi/3),0j),(0j,exp(-1j*math.pi/3)))
        G=((0j,1+0j),(-1+0j,0j))
        edges=[("a","b",A),("b","a",m.I2)]
        _,tr=m.wilson_loop(edges)
        self.assertAlmostEqual(tr.real,1)
        altered=[("a","b",m.gauge_transform(A,G,m.I2)),("b","a",m.gauge_transform(m.I2,m.I2,G))]
        _,tr2=m.wilson_loop(altered)
        self.assertAlmostEqual(abs(tr2-tr),0)
        self.assertNotEqual(m.matmul(A,G),m.matmul(G,A))
        with self.assertRaises(ValueError): m.wilson_loop(edges[:1])
    def test_diffusion(self):
        edges=[(0,1,1),(1,2,1)]
        x=m.diffusion_step([6,0,0],edges,.25)
        self.assertEqual(x,[4.5,1.5,0])
        y=m.diffusion_step(x,edges,.25)
        self.assertEqual(y,[3.75,1.875,.375])
        self.assertEqual(sum(y),6)
        with self.assertRaises(ValueError): m.diffusion_step(x,edges,.6)
    def test_phase_network(self):
        self.assertAlmostEqual(abs(m.order_parameter([0,math.pi])),0)
        self.assertAlmostEqual(abs(m.order_parameter([0,math.pi],2)),1)
        v=[0.]*36; q=[.3]*36
        r=m.phase_readout36(v,q)
        self.assertAlmostEqual(r["relation"],1)
        self.assertFalse(m.phase_address_match(v,q,.01))
        self.assertAlmostEqual(m.phase_readout36(v,[0.]*18+[math.pi]*18)["relation"],0)
        for K,locked in [(2,True),(.5,False)]:
            theta=(0.,0.)
            for _ in range(2000):
                theta=m.phase_step(theta,(0.,1.),((0,K/2),(K/2,0)),(0.,0.),.01)
            delta=theta[1]-theta[0]
            if locked: self.assertAlmostEqual(delta,math.pi/6,places=5)
            else: self.assertGreater(delta,5)
    def test_geometry_and_causal_weight(self):
        self.assertAlmostEqual(m.disk_distance(0,.5),math.log(3))
        self.assertAlmostEqual(m.conformal_factor(3),64)
        self.assertAlmostEqual(m.relational_scalar(1,2,3,4,5,.5),.15+m.KAPPA)
        self.assertEqual(m.goal_cost([2,3],4,.5),7)
        a=m.AdaptiveEdge("a","b",.2,1)
        b=a.update("event","source",True,.25,1,1)
        a,b=a.elapse(.1,1),b.elapse(.1,1)
        self.assertGreater(b.phase_weight(),a.phase_weight())
        def step(e):
            return m.phase_step((0.,1.),(0.,0.),((0,e.phase_weight()),(0,0)),(0.,0.),.1)
        self.assertNotEqual(step(a),step(b))
        c=b.update("fail","source",False,.25,1,1)
        self.assertEqual(c.phase_weight(),b.phase_weight())

    def test_ciel_winding_and_ring(self):
        self.assertAlmostEqual(m.ciel_weighted_winding([(math.pi,1,.5)]),1)
        with self.assertRaises(ValueError): m.ciel_weighted_winding([(1,1,0)])
        r=m.ring_intervention()
        self.assertAlmostEqual(r["rms_gap"],.9810776583213893,places=9)
        self.assertEqual(r["control_gap"],0)

if __name__=="__main__":
    unittest.main()
