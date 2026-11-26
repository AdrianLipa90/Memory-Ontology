import math
import unittest
from fractions import Fraction
from engines import rdss_memory_mechanics_v32 as m

class RDSSMechanics(unittest.TestCase):
    def test_half_and_action(self):
        self.assertAlmostEqual(m.entropy(.5),math.log(2))
        self.assertEqual(m.defect(.5),0)
        self.assertGreater(m.defect(.1),0)
        self.assertEqual(m.half_interface(.5,2*math.pi),(0,1))
        self.assertAlmostEqual(sum(m.half_interface(.2,1.4)),1)
        self.assertEqual(m.action_defect([(1,0,1,.5)]),0)
        self.assertGreater(m.action_defect([(1,2,1,.5)]),0)
        self.assertAlmostEqual(abs(m.zero_axis(12.)),1)
    def test_address_and_collatz(self):
        self.assertEqual(m.contraction(6),(Fraction(1,64),4096))
        for signs in ((1,1),(-1,1),(1,-1),(-1,-1)):
            angle,genealogy=m.branch_address(iter(signs))
            self.assertEqual(genealogy,signs)
            self.assertEqual((angle*4).denominator,1)
        self.assertEqual(len({m.branch_address(s)[0]%2 for s in ((1,1),(-1,1),(1,-1),(-1,-1))}),4)
        for n in range(1,1001):
            x,tag=m.collatz_step(n)
            self.assertEqual(m.collatz_inverse(x,tag),n)
        for n,q in [(1,Fraction(4,7)),(2,Fraction(2,7)),(4,Fraction(1,7))]:
            self.assertEqual(m.parity_phase(n),q)
        for n in range(1,101):
            nxt=3*n+1 if n%2 else n//2
            self.assertEqual(m.parity_phase(nxt),(2*m.parity_phase(n))%1)
    def test_mass_clock_and_recall(self):
        self.assertAlmostEqual(m.semantic_mass(1,1,1,1,1),1)
        self.assertAlmostEqual(m.semantic_mass(1,0,0,0,0),.25)
        self.assertAlmostEqual(m.ciel_clock(1,.2,.8,.1,.5,1)/m.ciel_clock(1,.8,.8,.1,.5,1),8/3)
        self.assertAlmostEqual(m.kepler_period(2,2),2)
        self.assertAlmostEqual(m.recall(.2,.25,1,1),.4)
        self.assertAlmostEqual(m.decay(.4,math.log(2),1),.2)
        self.assertEqual(m.attraction(1,.8,.8,2,1,3,0),0)
        self.assertEqual(m.routing_probabilities([3,1]),[.75,.25])
    def test_imprint(self):
        n,b,q=(0,0,1),(1,0,0),(1,0,0)
        dm=m.displacement(n,b,q)
        self.assertAlmostEqual(abs(dm),math.pi/4)
        self.assertAlmostEqual(m.kick(0j,2,dm).real,math.pi/2)
        tq,tp=m.transport(n,b,q)
        self.assertAlmostEqual(m.dot(tq,b),0)
        self.assertAlmostEqual(m.dot(tq,tp),0)
        self.assertAlmostEqual(m.norm(tq),1)
        with self.assertRaises(ValueError): m.fs_log(n,(0,0,-1))
        z,v=m.kepler_segment(1+0j,1j,1,.001,1000)
        en,j=m.orbit_invariants(z,v,1)
        self.assertAlmostEqual(en,-.5,places=6)
        self.assertAlmostEqual(j,1,places=10)
    def test_causal_memory_and_provenance(self):
        a=m.Memory("same",.2,(.5,)*5,"PNCS:source")
        b=a.encounter("event","source",True,1,1,.25)
        self.assertGreater(b.accessibility,a.accessibility)
        a,b=a.elapse(.1,1),b.elapse(.1,1)
        self.assertGreater(b.accessibility,a.accessibility)
        self.assertGreater(m.attraction(1,b.accessibility,1,1,1,3,1),m.attraction(1,a.accessibility,1,1,1,3,1))
        self.assertEqual(a.identity,b.identity)
        self.assertEqual(a.exact_realization_mass,b.exact_realization_mass)
        c=b.encounter("failed","source",False,1,1,1)
        self.assertEqual(c.accessibility,b.accessibility)
        with self.assertRaises(ValueError): b.encounter("event","source",True,1,1,.2)
        self.assertEqual(b.elapse(1,10).learned_weight,b.learned_weight)

if __name__=="__main__":
    unittest.main()
