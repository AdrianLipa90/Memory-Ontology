import math, unittest
from photoreception import photo_target, HC_EV_NM
from noema_publication import Publications

SCENE={'materials':[{'id':0},{'id':1},{'id':2},{'id':3}]}
PULSE={'position_xy':[.36,.48],'material_id':2,'wavelength_nm':450.,'photon_count':100,
 'work_function_ev':2.,'absorption_fraction':.8,'quantum_yield':.5,'phase_gain_rad_per_ev':.02,'source_ref':'FIAT_LUX_TEST_FIXTURE'}
class PhotoTest(unittest.TestCase):
 def test_threshold(self):
  t=photo_target(SCENE,{**PULSE,'wavelength_nm':700.})
  self.assertEqual(t['phase_increment36'],[0.]*36);self.assertEqual(t['photoreception']['expected_emitted_electrons'],0)
 def test_dark(self):
  self.assertEqual(photo_target(SCENE,{**PULSE,'photon_count':0})['phase_increment36'],[0.]*36)
 def test_energy_and_balance(self):
  t=photo_target(SCENE,PULSE);e=t['photoreception']; self.assertAlmostEqual(e['photon_energy_ev'],HC_EV_NM/450.)
  self.assertEqual(e['expected_emitted_electrons'],40.)
  self.assertAlmostEqual(e['kinetic_energy_proxy_ev']+e['nonkinetic_absorbed_energy_ev'],e['absorbed_energy_ev'])
  self.assertAlmostEqual(sum(t['phase_increment36']),.02*e['kinetic_energy_proxy_ev'])
  self.assertIsNone(e['affect'])
 def test_spatial(self):
  a=photo_target(SCENE,PULSE)['phase_increment36'];b=photo_target(SCENE,{**PULSE,'position_xy':[.95,.95]})['phase_increment36']
  self.assertEqual(sum(x!=0 for x in a),4);self.assertNotEqual(a,b);self.assertAlmostEqual(sum(a),sum(b))
 def test_invalid(self):
  for q in [{'wavelength_nm':0},{'quantum_yield':1.1},{'position_xy':[.5,float('nan')]},{'material_id':99},{'phase_gain_rad_per_ev':10}]:
   with self.assertRaises(ValueError):photo_target(SCENE,{**PULSE,**q})
 def test_surface(self):
  p=Publications(); self.assertEqual(p.read('PHOTORECEPTION')['status'],'AWAITING_FRAME')
  f={'generation':'fixture','sequence':1,'tau':.01,'source':'TEST'};p.bind(f)
  self.assertEqual(p.read('PHOTORECEPTION')['status'],'NO_DECLARED_PULSE_THIS_FRAME')
  p.bind({**f,'sequence':2,'photoreception':photo_target(SCENE,PULSE)['photoreception']})
  a=p.read('PHOTORECEPTION');self.assertEqual(a['sequence'],2);self.assertEqual(a['status'],'PHOTOELECTRIC_RESPONSE');a['event']['wavelength_nm']=1
  self.assertEqual(p.read('PHOTORECEPTION')['event']['wavelength_nm'],450.)
  p.bind({**f,'sequence':3});self.assertIsNone(p.read('PHOTORECEPTION')['event'])
if __name__=='__main__':unittest.main()
