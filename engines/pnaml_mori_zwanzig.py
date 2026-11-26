"""ISO-32: exact discrete reduction for frozen phase tangent blocks.

Pass an existing PNAML Model snapshot; no native producer writes.
The 12 core perturbations, frequencies and coupling weights are held fixed
in the tangent calculation. Full nonlinear trajectory control is separate.
"""
import numpy as np

def tangent_blocks(model):
    p=model.h["batch_phi"]; g=model.h["batch_g"]; d=p.shape[1]
    W=g*np.cos(p[:,:,None]-p[:,None,:])/d
    J=-W; i=np.arange(d); J[:,i,i]+=W.sum(axis=2)
    return np.eye(d)[None,:,:]+model.dt*J

def kernels(T,steps):
    A=T.mean(axis=0); Y=T-A; K=[]
    for _ in range(steps-1):
        TY=T@Y; mean=TY.mean(axis=0); K.append(mean); Y=TY-mean
    return A,np.array(K)

def hidden_force(T,h0,steps):
    h=h0.copy(); out=[]
    for _ in range(steps):
        th=T@h; f=th.mean(axis=0); out.append(f); h=th-f
    return np.array(out)

def full(T,z0,h0,steps):
    x=np.broadcast_to(z0,(len(T),*z0.shape)).copy()+h0
    out=[x.mean(axis=0)]
    for _ in range(steps):
        x=T@x; out.append(x.mean(axis=0))
    return np.array(out)

def reduced(A,K,z0,f,steps,L):
    out=[z0]
    for k in range(steps):
        v=A@out[-1]+f[k]
        for j in range(min(k,L)): v=v+K[j]@out[k-1-j]
        out.append(v)
    return np.array(out)

def rms(x):
    return float(np.sqrt(np.mean(x*x)))

def witness(Model,seed=42,steps=128):
    m=Model(seed,.01)
    for _ in range(256): m.next()
    T=tangent_blocks(m); A,K=kernels(T,steps)
    rng=np.random.default_rng(20261126)
    # Advance the RNG identically to the executed local finite-difference check.
    rng.normal(size=m.h["batch_phi"].shape)
    z0=rng.normal(size=(36,64)); z0-=z0.mean(axis=0); z0*=.001/rms(z0)
    h0=np.zeros((32,36,64)); f=hidden_force(T,h0,steps)
    truth=full(T,z0,h0,steps)
    errors={}
    for L in (0,4,16,32,64,steps):
        err=reduced(A,K,z0,f,steps,L)-truth
        errors[str(L)]=rms(err[1:])
    h=rng.normal(size=h0.shape); h-=h.mean(axis=0); h*=.001/rms(h)
    target=full(T,z0,h,steps); forcing=hidden_force(T,h,steps)
    exact=reduced(A,K,z0,forcing,steps,steps)
    _,control=kernels(np.broadcast_to(A,T.shape).copy(),steps)
    assert errors[str(steps)]<1e-10
    assert rms(exact-target)<1e-10
    assert np.max(abs(control))<1e-12
    return dict(seed=seed,errors=errors,kernel_norms=[float(np.linalg.norm(k)) for k in K],
                hidden_forcing_error=rms(reduced(A,K,z0,f,steps,steps)-target),
                exact_hidden_error=rms(exact-target))
