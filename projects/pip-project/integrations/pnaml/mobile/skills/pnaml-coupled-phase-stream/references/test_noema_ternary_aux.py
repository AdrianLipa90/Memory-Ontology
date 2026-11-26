import unittest
from noema_surface import QHTRISurface, AUX_ADDRESS, ROOT_ADDRESS
from vendor.phaseholomotion.aux_ternary_bridge import decode_binary_lanes

class TernarySurfaceTests(unittest.TestCase):
    def setUp(self):
        self.surface=QHTRISurface()
    def bind(self,seq,trits):
        self.surface.bind(dict(phase36_lift=[float(seq)]*36,winding36=[0]*36,
            sequence=seq,tau=seq*.01,generation='test-only',qhtri={},trits12=trits,
            source='TEST_FIXTURE'),[0.]*36,[[0.]*36 for _ in range(36)])
    def test_unbound(self):
        self.assertEqual(self.surface.read(AUX_ADDRESS)['status'],'AWAITING_FRAME')
        self.assertIn('AUX',self.surface.read(ROOT_ADDRESS)['fields'])
    def test_unknown_not_hold(self):
        self.bind(1,None); a=self.surface.read(AUX_ADDRESS)
        self.assertEqual(a['status'],'UNKNOWN_TRITS'); self.assertIsNone(a['binary_downstream']); self.assertIsNone(a['hold_count'])
    def test_explicit_hold_and_reversibility(self):
        trits=[-1,0,1]*4;self.bind(1,trits);a=self.surface.read(AUX_ADDRESS);b=a['binary_downstream']
        self.assertEqual(a['status'],'EXPLICIT_TRITS');self.assertEqual(a['hold_count'],4)
        self.assertEqual(b['hold_potential'],['-i','+i']);self.assertEqual(decode_binary_lanes(b['value_bits'],b['valid_mask']),tuple(trits))
        self.assertFalse(a['dynamic_hashing']);self.assertFalse(a['native_host_verified'])
    def test_zero_is_explicit_hold(self):
        self.bind(1,[0]*12);a=self.surface.read(AUX_ADDRESS)
        self.assertEqual(a['hold_count'],12);self.assertEqual(a['binary_downstream']['hold_mask'],4095)
    def test_same_surface_next_frame_and_unknown_reset(self):
        self.bind(1,[1]*12);self.bind(2,None);a=self.surface.read(AUX_ADDRESS)
        self.assertEqual(a['sequence'],2);self.assertEqual(a['generation'],'test-only');self.assertEqual(a['tau'],.02)
        self.assertEqual(a['phase36_lift'],[2.]*36);self.assertIsNone(a['trits12']);self.assertIsNone(a['binary_downstream'])
    def test_read_isolation(self):
        self.bind(1,[1]*12);a=self.surface.read(AUX_ADDRESS);a['trits12'][0]=-1;a['phase36_lift'][0]=99
        self.assertEqual(self.surface.read(AUX_ADDRESS)['trits12'][0],1);self.assertEqual(self.surface.read(AUX_ADDRESS)['phase36_lift'][0],1.)
if __name__=='__main__': unittest.main()
