"""Conditional HTRI contraction diagnostic. Inject source-compatible Model and htri.
Portable version of the local experiment; not independently executed as a repo import.
"""
import copy
import numpy as np

def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x)**2)))

def replay_update(g,p,htri):
    diff=p[:,:,None]-p[:,None,:]
    hebb=np.sum((htri.HARMONIC_AMPS**2*htri.OI)[None,:,None,None]*np.cos(htri.HARMONIC_VALUES[None,:,None,None]*diff[:,None,:,:])*htri._BOTH_HARMONIC_MASK[None,:,:,:],axis=1)
    out=np.clip(g+hebb-htri.OI**2*g,0,1)
    i=np.arange(g.shape[-1]);out[:,i,i]=0
    return out

def run(Model,htri,seed=42,train=192,follow=1024):
    m=Model(seed,.01)
    for _ in range(64):m.next()
    a,b=copy.deepcopy(m),copy.deepcopy(m)
    pattern=np.sin(2*np.pi*np.arange(36)/36);pattern-=pattern.mean()
    for _ in range(train):
        for model,sign in ((a,1),(b,-1)):
            model.next({'phase_increment36':(sign*.04*pattern).tolist(),'source_ref':'synthetic history stimulus; no extra memory law'})
    control=copy.deepcopy(a);b_g=b.h['batch_g'].copy();b=copy.deepcopy(a);b.h['batch_g']=b_g
    initial=float(np.linalg.norm(a.h['batch_g']-b.h['batch_g']));assert initial>0
    replay=b_g.copy();rate=1-htri.OI**2;previous=initial;max_violation=0.;max_replay_error=0.;max_lift=0.;samples=[]
    def read(k):
        x,y=a.h['batch_g'],b.h['batch_g'];g=x.mean(0)*a.bw;h=y.mean(0)*a.bw
        return dict(step=k,time=k*a.dt,full_gap=float(np.linalg.norm(x-y)),aggregate_gap=float(np.linalg.norm(g-h)),phase_rms=rms(a.project(a.core,a.batch)-b.project(b.core,b.batch)),replay_gap=float(np.linalg.norm(x-replay)),bound=initial*rate**k,lambda2_A=float(np.linalg.eigvalsh(np.diag(g.sum(1))-g)[1]),lambda2_B=float(np.linalg.eigvalsh(np.diag(h.sum(1))-h)[1]))
    samples.append(read(0));assert samples[0]['phase_rms']==0
    for k in range(1,follow+1):
        old=a.h['batch_g'].copy();fa=a.next();fb=b.next();p=a.h['batch_phi'];ra=replay_update(old,p,htri);replay=replay_update(replay,p,htri)
        max_replay_error=max(max_replay_error,float(np.max(abs(ra-a.h['batch_g']))))
        gap=float(np.linalg.norm(a.h['batch_g']-replay));max_violation=max(max_violation,gap-rate*previous);previous=gap
        max_lift=max(max_lift,fa['source_lift_error'],fb['source_lift_error'])
        if k in (1,16,64,128,256,512,1024,2048,4096) or k==follow:samples.append(read(k))
        if k<=16:
            fc=control.next();assert fc['phase36_lift']==fa['phase36_lift'] and fc['coupling36']==fa['coupling36']
    assert max_replay_error<1e-12 and max_violation<1e-9 and max_lift<1e-9
    return dict(seed=seed,initial_gap=initial,train=train,follow=follow,source_replay_error=max_replay_error,contraction_bound_violation=max_violation,max_lift_error=max_lift,identical_history_control_steps=min(16,follow),samples=samples)
