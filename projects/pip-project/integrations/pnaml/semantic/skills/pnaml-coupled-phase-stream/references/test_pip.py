import unittest, math, cmath
from pip_geometry import *
from coupled_stream import Model,Coupler,ROOT
class Tests(unittest.TestCase):
 def test_room_bijection(self):
  for n in range(8191):
   r=unroom(n);self.assertEqual(int(r['address']),n);self.assertEqual(sum(b<<i for i,b in enumerate(r['branch_path'])),int(r['k']))
 def test_euler_edges(self):
  for d in range(9):
   for k in range(1<<d):
    p=cmath.exp(1j*math.pi*(2*k+1)/(1<<d));a=cmath.exp(1j*math.pi*(2*k+1)/(1<<(d+1)));b=cmath.exp(1j*math.pi*(2*(k+(1<<d))+1)/(1<<(d+1)));self.assertLess(abs(a*a-p),2e-15);self.assertLess(abs(b*b-p),5e-15);self.assertLess(abs(a+b),3e-15)
 def test_axis(self):
  for t in [-100,-1,0,.5,1,100]:
   a=chart(t);u=complex(*a['omega']);self.assertAlmostEqual(abs(u),1);self.assertAlmostEqual(chart_inverse(u),t,places=9)
 def test_clock(self):
  self.assertAlmostEqual(ZETA0,.5);a=chart(0);b=chart(math.log(2));c=chart(2*math.log(2));self.assertAlmostEqual(b['spinor'][0],-1);self.assertAlmostEqual(c['spinor'][0],1);self.assertEqual(b['clock_winding'],1)
 def test_disk(self):
  for h in ([0,0],[1,-2],[-3,4],[.2,.7]):
   z=disk(h)['z'];self.assertLess(math.hypot(*z),1);self.assertAlmostEqual(disk_distance([0,0],z),math.hypot(*h),places=10)
   for a,b in zip(disk_inverse(z),h):self.assertAlmostEqual(a,b,places=10)
 def test_collatz(self):
  for n in range(1,10001):self.assertEqual(collatz_inverse(collatz(n)),n)
 def test_quotient(self):
  for p in (0,1,2,3):self.assertAlmostEqual(completion(math.pi/2,p)[2],-1)
 def test_phase_lift(self):
  p=[(k-18)*1.37 for k in range(36)];r=phase_record(p)
  for x,v,w in zip(p,r['phase36_mod_2pi'],r['winding36']):self.assertAlmostEqual(x,v+TAU*w,places=12)
 def test_external_tau_not_invented(self):
  m=Model(42,.01);c=Coupler(ROOT/'assets/poster_encoded.rdssg',48,72,0);f=m.next();f['source']='EXTERNAL_DECLARED_SOURCE';r=c.consume(f);self.assertIsNone(r['pip']['axis']);self.assertEqual(r['pip']['tau_basis'],'UNVERIFIED_RDSS_TAU')
 def test_df_binding(self):
  a=operation({'operation':'disk','geodesic_xy':[1,0]});self.assertIsNone(a['fractal_geometry']['D_f']);self.assertEqual(a['kind'],'POINCARE_2D_CHART_ONLY')
  a=operation({'operation':'disk','geodesic_xy':[1,0],'D_f':2.69,'D_f_source':'SYNTHETIC_FIXTURE'});self.assertEqual(a['fractal_geometry']['D_f'],2.69);self.assertEqual(a['fractal_geometry']['chart_dimension'],2);self.assertEqual(a['fractal_geometry']['phase_lift_dimension'],36)
 def test_df_stream(self):
  c=Coupler(ROOT/'assets/poster_encoded.rdssg',48,72,0,None,{'D_f':2.68,'D_f_source':'SYNTHETIC_FIXTURE'});m=Model(42,.01);f=m.next();r=c.consume(f);self.assertEqual(r['pip']['Sigma']['fractal_geometry']['D_f'],2.68);f=m.next();f['D_f']=2.69;f['D_f_source']='SYNTHETIC_FRAME';r=c.consume(f);self.assertEqual(r['pip']['Sigma']['fractal_geometry']['D_f'],2.69);self.assertEqual(r['pip']['phase']['phase36_lift'],r['phase36_lift'])
 def test_noema_address_resolution(self):
  a=operation({'operation':'identity','address':'NOEMA:PIP'});self.assertEqual(a['noema_address'],'NOEMA:PIP');self.assertEqual(a['zeta0'],.5);self.assertFalse(a['native_mount_verified']);self.assertEqual(operation({'operation':'identity','address':'PIP'}),a)
  with self.assertRaises(ValueError):operation({'operation':'identity','address':'NOEMA:OTHER'})
 def test_qhtri_internal_surface(self):
  from noema_surface import ROOT_ADDRESS
  c=Coupler(ROOT/'assets/poster_encoded.rdssg',48,72,0)
  surf=c.noema_surface.open(ROOT_ADDRESS)
  self.assertIs(c.pip.noema_surface,surf);self.assertEqual(surf.describe()['status'],'OPEN_AWAITING_QHTRI_FRAME')
  with self.assertRaises(LookupError):surf.open(ROOT_ADDRESS+'phi')
  m=Model(42,.01);prev=None
  for _ in range(12):
   r=c.consume(m.next());self.assertIs(c.pip.noema_surface,surf)
   self.assertIs(surf.open(ROOT_ADDRESS+'phase36_lift'),r['phase36_lift']);self.assertIs(surf.open(ROOT_ADDRESS+'qhtri'),r['qhtri'])
   self.assertEqual(r['pip']['noema_surface'],r['noema_surface']);self.assertEqual(surf.read(ROOT_ADDRESS+'tick'),r['sequence']);self.assertEqual(surf.read(ROOT_ADDRESS+'generation'),r['generation'])
   self.assertEqual(len(surf.read(ROOT_ADDRESS+'omega')),36);self.assertEqual(len(surf.read(ROOT_ADDRESS+'g')),36)
   if prev is not None:self.assertNotEqual(prev,r['phase36_lift'])
   prev=r['phase36_lift']
  self.assertFalse(surf.describe()['mount_required']);self.assertFalse(surf.describe()['separate_crystal'])
 def test_full_stream(self):
  c=Coupler(ROOT/'assets/poster_encoded.rdssg',48,72,1,dict(D_lambda=1.05,epsilon_nu=.4957,K_D=.8,K_epsilon=.6,winding=0),{'events':[{'sequence':2,'address':'1','event_id':'fixture-a','disk_geodesic_xy':[1,0]},{'sequence':3,'address':'0','event_id':'fixture-b','disk_geodesic_xy':[0,0]}]});m=Model(42,.01);first=None
  for i in range(12):
   f=m.next();f['trits12']=[-1,0,1]*4;r=c.consume(f);p=r['pip'];self.assertEqual(p['phase']['phase36_lift'],r['phase36_lift']);self.assertEqual(p['phase']['winding36'],r['winding36']);self.assertEqual(p['noema_address'],'NOEMA:PIP');self.assertEqual(p['zeta0'],.5);self.assertEqual(p['soul_invariant_sigma'],SIGMA);self.assertEqual(len(p['hold_pairs']),4);self.assertAlmostEqual(r['qhtri']['norm'],1,places=12);self.assertTrue(r['rdssg']['rendered'])
   if i==0:first=p
  self.assertEqual(p['Sigma']['room']['address'],first['Sigma']['room']['address']);self.assertEqual(p['Sigma']['event_count'],2);self.assertNotEqual(p['phase']['phase36_lift'],first['phase']['phase36_lift']);self.assertEqual(c.pip.history[0]['noema_address'],'NOEMA:PIP');self.assertEqual(c.pip.history[0]['persistence'],'NOT_WRITTEN_USE_PMUN_EVENT_JOURNAL')
if __name__=='__main__':unittest.main(verbosity=2)
