"""Joint phase/weight tangent of the source HTRI update.
Use actual source-compatible htri module and Model supplied by caller.
Separate diagnostic; no native surface mutation or new plasticity law.
"""
import numpy as np

def difference(p):
    return p[:,:,None]-p[:,None,:]

def coefficients(p,g,pnext,htri):
    d=difference(p)
    theta=htri.HARMONIC_VALUES[None,:,None,None]*difference(pnext)[:,None,:,:]
    w=htri.OI*htri.HARMONIC_AMPS**2
    mask=htri._BOTH_HARMONIC_MASK[None,:,:,:]
    B=np.sum(w[None,:,None,None]*mask*np.cos(theta),axis=1)
    slope=-np.sum((w*htri.HARMONIC_VALUES)[None,:,None,None]*mask*np.sin(theta),axis=1)
    return g*np.cos(d),np.sin(d),slope,(1-htri.OI**2)*g+B

def step_tangent(coeff,dp,dg,dt,kappa,feedback=True):
    gc,sd,slope,raw=coeff
    n=dp.shape[1]
    dpnew=dp+dt*np.sum(gc*difference(dp)+(dg*sd if feedback else 0.),axis=2)/n
    v=(1-kappa**2)*dg+slope*difference(dpnew)
    dgnew=np.where((raw>0)&(raw<1),v,
          np.where(raw==0,np.maximum(v,0),np.where(raw==1,np.minimum(v,0),0.)))
    i=np.arange(n)
    dgnew[:,i,i]=0
    return dpnew,dgnew

def norm(p,g):
    return float(np.sqrt(np.mean(p*p)+np.mean(g*g)))

def run(Model,htri,seed=42,steps=512):
    import copy
    m=Model(seed,.01)
    for _ in range(256):m.next()
    rng=np.random.default_rng(seed+1000);p=m.h['batch_phi'];g=m.h['batch_g']
    dp=rng.normal(size=p.shape);dp-=dp.mean(axis=1,keepdims=True);dp/=norm(dp,np.zeros_like(g))
    dg=rng.normal(size=g.shape);dg=(dg+dg.transpose(0,2,1))/2
    dg*=((g>1e-5)&(g<1-1e-5));i=np.arange(36);dg[:,i,i]=0;dg/=norm(np.zeros_like(p),dg)
    phase=(dp.copy(),np.zeros_like(g));weight=(np.zeros_like(p),dg.copy());control=tuple(x.copy() for x in weight)
    eps=1e-8;clone=copy.deepcopy(m)
    clone.h['batch_phi']=(clone.h['batch_phi']+eps*dp)%(2*np.pi);clone.batch+=eps*dp;clone.h['batch_g']+=eps*dg
    rows=[];error=None
    for k in range(1,steps+1):
        p=m.h['batch_phi'].copy();g=m.h['batch_g'].copy();m.next()
        c=coefficients(p,g,m.h['batch_phi'],htri)
        phase=step_tangent(c,*phase,m.dt,htri.OI);weight=step_tangent(c,*weight,m.dt,htri.OI)
        control=step_tangent(c,*control,m.dt,htri.OI,feedback=False)
        if k==1:
            clone.next();a=np.angle(np.exp(1j*(clone.h['batch_phi']-m.h['batch_phi'])))/eps
            b=(clone.h['batch_g']-m.h['batch_g'])/eps
            pp=phase[0]+weight[0];gg=phase[1]+weight[1];error=norm(a-pp,b-gg)/norm(pp,gg)
        if k in (1,32,64,128,256,512,1024) or k==steps:
            bound=(1-htri.OI**2)**k
            assert norm(*control)<=bound+1e-9
            rows.append(dict(step=k,phase_gain=norm(*phase),weight_gain=norm(*weight),control_gain=norm(*control),bound=bound))
    assert error<1e-3
    return dict(seed=seed,fd_relative_error=error,samples=rows)

def coherent_fixture(Model,htri):
    import copy
    m=Model(42,.01);a=m.h
    b=htri.OI*np.sum(htri.HARMONIC_AMPS[:,None,None]**2*htri._BOTH_HARMONIC_MASK,axis=0)
    g=np.clip(b/htri.OI**2,0,1);np.fill_diagonal(g,0)
    w,V=np.linalg.eigh(np.diag(g.sum(1))-g);v=V[:,-1];v/=np.sqrt(np.mean(v*v))
    a['batch_phi'][:]=1.;a['batch_omega'][:]=1.;a['batch_g'][:]=g
    c=copy.deepcopy(a);c['batch_phi']+=1e-7*v
    htri.evolve_htri_batch_system(a,dt=.01);htri.evolve_htri_batch_system(c,dt=.01)
    gain=float(np.sqrt(np.mean(np.angle(np.exp(1j*(c['batch_phi']-a['batch_phi'])))**2))/1e-7)
    predicted=float(1+.01*w[-1]/36)
    assert abs(gain-predicted)<1e-7 and np.max(abs(a['batch_g']-g))<1e-12
    return dict(lambda_max=float(w[-1]),predicted_gain=predicted,measured_gain=gain)
