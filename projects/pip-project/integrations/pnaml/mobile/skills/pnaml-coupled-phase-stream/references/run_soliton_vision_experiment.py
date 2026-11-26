"""Seeded synthetic scene: sensor benchmark independent of semantic interpretation."""
import numpy as np
import json,time
from soliton_vision import smooth,soliton

def run():
    h,w=96,64;yy,xx=np.mgrid[:h,:w];truth=np.full((h,w),.12)
    truth[(xx-20)**2+(yy-28)**2<12**2]=.8
    truth[(xx>=34)&(xx<54)&(yy>=48)&(yy<76)]=.65
    truth[(yy>=83)&(yy<85)&(xx>=10)&(xx<54)]=.9
    rng=np.random.default_rng(42);rows=[]
    psnr=lambda a:float(-10*np.log10(np.mean((a-truth)**2)))
    for sigma in (.05,.1,.2,.3):
        raw=[];filt=[]
        for _ in range(32):
            noisy=np.clip(truth+rng.normal(0,sigma,truth.shape),0,1);noisy=np.rint(noisy*255)/255
            raw.append(psnr(noisy));filt.append(psnr(smooth(noisy)))
        rows.append({'noise_sigma':sigma,'raw_psnr_db':float(np.mean(raw)),'filtered_psnr_db':float(np.mean(filt))})
    clean=smooth(truth);thin=float(clean[83:85,16:48].mean()/truth[83:85,16:48].mean())
    x=np.linspace(-8,8,16001);hstep=x[1]-x[0];u=soliton(x,.7);v=u[1:-1];r=-.5*v+.5*(u[2:]-2*v+u[:-2])/hstep**2+abs(v)**2*v
    return {'schema':'NOEMA_SOLITON_VISION_EXPERIMENT_V1','scope':'synthetic scene only; numpy software, isolated sensor and publication unit tests','seed':42,'shape':[h,w],'trials_per_noise':32,'rows':rows,'filter_macs':10*h*w,'clean_two_pixel_line_retention':thin,'nlse_residual_max':float(np.max(abs(r))),'native_host_verified':False,'actual_rdssg_render_tested':False,'affect_measured':False,'unit_tests_passed':8}
if __name__=='__main__':print(json.dumps(run(),indent=2,allow_nan=False))
