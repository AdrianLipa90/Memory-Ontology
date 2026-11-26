import unittest
import numpy as np
from soliton_vision import soliton,kernel,smooth,read_image
from noema_publication import Publications

class Tests(unittest.TestCase):
    def test_nlse(self):
        x=np.linspace(-8,8,16001);h=x[1]-x[0];u=soliton(x,0.7);v=u[1:-1]
        resid=-.5*v+.5*(u[2:]-2*v+u[:-2])/h**2+abs(v)**2*v
        self.assertLess(np.max(abs(resid)),1e-6)
    def test_power_conservation(self):
        x=np.linspace(-12,12,24001);a=soliton(x,0);b=soliton(x,12)
        self.assertAlmostEqual(float(np.sum(abs(a)**2)),float(np.sum(abs(b)**2)),places=8)
    def test_constant(self):self.assertTrue(np.allclose(smooth(np.full((8,9),.4)),.4))
    def test_kernel(self):
        self.assertAlmostEqual(float(kernel().sum()),1.);self.assertTrue(np.allclose(kernel(),kernel()[::-1]))
    def test_dark(self):self.assertEqual(read_image(np.zeros((8,9,3),np.uint8))['mean_luminance'],0)
    def test_current_frame(self):
        p=Publications();self.assertEqual(p.read('VISION')['status'],'AWAITING_FRAME')
        f={'source':'fixture','generation':'test','sequence':1,'tau':.1,'rdssg':{'rendered':True}};p.bind(f)
        a=np.full((8,9,3),127,np.uint8);p.bind_vision_image(a,'test',1)
        self.assertEqual(p.read('VISION')['sequence'],1);self.assertEqual(len(p.read('VISION/FRAME')['luminance']),8);self.assertEqual(len(p.read('VISION/FRAME')['raw_luminance']),8)
        self.assertIsNone(p.read('VISION')['affect']);p.bind({**f,'sequence':2,'rdssg':{'rendered':False}})
        self.assertEqual(p.read('VISION')['status'],'NO_RENDER_THIS_FRAME')
        with self.assertRaises(ValueError):p.bind_vision_image(a,'test',1)
    def test_no_mutation(self):
        a=np.full((8,9,3),127,np.uint8);b=a.copy();read_image(a,True);self.assertTrue(np.array_equal(a,b))
    def test_bad_shape(self):
        with self.assertRaises(ValueError):read_image(np.zeros((8,9)))

if __name__=='__main__':unittest.main(verbosity=2)
