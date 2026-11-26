"""Imaginal sensor components on a model chart; no hardware or phenomenal claim."""
import numpy as np
import math


def soliton(x,z,eta=1.):
    """Stationary bright soliton of i*u_z + u_xx/2 + |u|^2*u=0."""
    if not math.isfinite(eta) or eta<=0 or not math.isfinite(z):raise ValueError('finite z, positive eta required')
    x=np.asarray(x,dtype=float)
    # stable sech without overflowing cosh at distant coordinates
    a=np.exp(-np.abs(eta*x));return eta*2*a/(1+a*a)*np.exp(0.5j*eta**2*z)


def kernel():
    # Five taps sample the soliton power envelope, not simulated optical propagation.
    w=abs(soliton(np.arange(-2,3)*.75,0.))**2
    return w/w.sum()


def smooth(a):
    w=kernel();h,width=a.shape;pad=np.pad(a,((0,0),(2,2)),mode='edge')
    b=sum(w[i]*pad[:,i:i+width] for i in range(5))
    pad=np.pad(b,((2,2),(0,0)),mode='edge')
    return sum(w[i]*pad[i:i+h,:] for i in range(5))


def read_image(rgb,include_frame=False):
    """Read only current rendered RDSSG linear RGB8. No semantic or actuator output."""
    a=np.asarray(rgb)
    if a.ndim!=3 or a.shape[2]!=3 or min(a.shape[:2])<2 or a.dtype!=np.uint8:raise ValueError('H x W x 3 uint8 linear RGB required')
    # Preserve luminance separately from chromatic means; no pretend color reconstruction.
    y=(a.astype(np.float64)/255.)@np.array([.2126,.7152,.0722]);r=smooth(y)
    gy,gx=np.gradient(r);edge=np.hypot(gx,gy)
    result={'schema':'NOEMA_SOLITON_VISION_V1','height':int(a.shape[0]),'width':int(a.shape[1]),
        'input':'RDSSG_RENDERED_LINEAR_RGB8','mean_luminance':float(r.mean()),'luminance_std':float(r.std()),
        'mean_gradient':float(edge.mean()),'peak_gradient':float(edge.max()),'mean_rgb':(a.mean(axis=(0,1))/255.).tolist(),
        'kernel_power5':kernel().tolist(),'filter_macs':int(10*y.size),'filter':'SEPARABLE_SECH_SQUARED_POWER_ENVELOPE',
        'waveguide':'ANALYTIC_NORMALIZED_1D_FOCUSING_NLSE','hardware_verified':False,'affect':None,'dynamic_hashing':False}
    if include_frame:
        result['raw_luminance']=y.tolist();result['luminance']=r.tolist();result['gradient_magnitude']=edge.tolist()
    return result
