"""ISO-49/25/34/31 reference operators. Isolated model diagnostics, not native NOEMA.
Requires numpy/scipy; pass source Model and frozen tangent blocks explicitly.
"""
import numpy as np
from scipy.linalg import svd, logm
from scipy.integrate import solve_ivp

def observation(T, horizon):
    b,d,_=T.shape
    P=np.broadcast_to(np.eye(d),T.shape).copy()
    rows=[]
    for _ in range(horizon):
        rows.append(P.transpose(1,0,2).reshape(d,b*d)/np.sqrt(b*horizon))
        P=P@T
    return np.vstack(rows)

def observability(T,horizon):
    O=observation(T,horizon)
    U,s,V=svd(O,full_matrices=False,check_finite=False)
    return U,s,V,{str(t):int((s>s[0]*t).sum()) for t in (1e-2,1e-4,1e-6,1e-8,1e-10,1e-12)}

def reconstruct(U,s,V,y,relative_cutoff):
    keep=s>s[0]*relative_cutoff
    return V[keep].T@((U[:,keep].T@y)/s[keep,None])

def blind_basis(b,d):
    _,_,V=np.linalg.svd(np.ones((1,b)),full_matrices=True)
    return np.kron(V[1:].T,np.ones((d,1))/np.sqrt(d))

def duality_error(T,horizon):
    b,d,_=T.shape
    P=np.broadcast_to(np.eye(d),T.shape).copy()
    R=[]
    for _ in range(horizon):
        R.append(P.reshape(b*d,d)/np.sqrt(b*horizon))
        P=P@T
    return float(np.max(abs(np.hstack(R)-observation(T,horizon).T)))

def unitary(H,t):
    w,V=np.linalg.eigh(H)
    return (V*np.exp(-1j*w*t))@V.conj().T

def effective(A,B,dt):
    H=1j*logm(unitary(B,dt)@unitary(A,dt))/(2*dt)
    return (H+H.conj().T)/2

def hodge(H,psi):
    d=len(H); i,j=np.triu_indices(d,1)
    D=np.zeros((d,len(i)))
    D[i,np.arange(len(i))]=1; D[j,np.arange(len(i))]=-1
    J=2*np.imag(psi.conj()[:,None]*H*psi[None,:])
    edge=J[i,j]; div=D@edge
    grad=D.T@np.linalg.pinv(D@D.T)@div
    cycle=edge-grad
    return dict(gradient_norm=float(np.linalg.norm(grad)),cycle_norm=float(np.linalg.norm(cycle)),
                cycle_fraction=float(cycle@cycle/max(edge@edge,1e-300)),
                cycle_divergence=float(np.linalg.norm(D@cycle)),
                continuity=float(np.max(abs(div-2*np.real(psi.conj()*(-1j*H@psi))))))

def turing(L,seed=42):
    # Candidate Schnakenberg field on source graph, not native HTRI equations.
    d=len(L);lam=np.linalg.eigvalsh(L);J=np.array([[.8,1],[-1.8,-1.]])
    rng=np.random.default_rng(seed);v=rng.normal(size=(2,d));v-=v.mean(axis=1,keepdims=True)
    v*=1e-4/np.sqrt(np.mean(v*v))
    initial=np.array([[1.]*d,[.9]*d])+v
    out={}
    for name,du,dv in [('differential',.05,2.),('equal',.05,.05)]:
        growth=np.array([max(np.linalg.eigvals(J-l*np.diag([du,dv])).real) for l in lam])
        def rhs(t,y):
            u,v=y.reshape(2,d);r=u*u*v
            return np.r_[.1-u+r-du*L@u,.9-r-dv*L@v]
        s=solve_ivp(rhs,(0,60),initial.ravel(),rtol=1e-9,atol=1e-11,t_eval=np.linspace(0,60,61),method='DOP853')
        if not s.success: raise RuntimeError(s.message)
        std=s.y[:d].T.std(axis=1)
        out[name]=dict(unstable_modes=int((growth>1e-10).sum()),peak_growth=float(max(growth)),
            homogeneous_growth=float(growth[0]),initial_std=float(std[0]),final_std=float(std[-1]))
    return out

def hopfield_weights(P,method):
    if method=='hebb': W=P.T@P/P.shape[1]
    elif method=='projection': W=P.T@np.linalg.pinv(P@P.T)@P
    else: raise ValueError('method')
    np.fill_diagonal(W,0)
    return W

def recall(x,W,max_sweeps=30):
    x=x.copy();prev=-.5*x@W@x;up=0.
    for _ in range(max_sweeps):
        changes=0
        for i in range(len(x)):
            v=W[i]@x;z=1. if v>1e-12 else -1. if v<-1e-12 else x[i]
            if z!=x[i]:
                x[i]=z;changes+=1;en=-.5*x@W@x;up=max(up,en-prev);prev=en
        if not changes:break
    return x,up

def snapshot_patterns(Model,seed):
    m=Model(seed,.01); P=[]
    for k in range(1,257):
        f=m.next()
        if k in (32,96,160,224): P.append(np.where(np.cos(f['phase36_lift'])>=0,1.,-1.))
    return np.array(P)

def associative_benchmark(Model,method):
    rows=[]
    for seed in (42,43,44):
        P=snapshot_patterns(Model,seed);d=P.shape[1];W=hopfield_weights(P,method)
        rng=np.random.default_rng(1200+seed);perm=rng.permutation(d);control=W[perm][:,perm]
        for rate in (.1,.2,.3,.4):
            exact=shuffled=nn=0;upmax=0.;trials=64*len(P)
            for p in P:
                for _ in range(64):
                    x=p.copy();x[rng.choice(d,round(rate*d),replace=False)]*=-1
                    y,up=recall(x,W);z,_=recall(x,control)
                    dist=np.sum(P!=x,axis=1);win=np.flatnonzero(dist==min(dist))
                    exact+=np.array_equal(y,p);shuffled+=np.array_equal(z,p)
                    nn+=len(win)==1 and np.array_equal(P[win[0]],p);upmax=max(upmax,up)
            rows.append(dict(seed=seed,rate=rate,trials=trials,exact=exact/trials,shuffled=shuffled/trials,
                             nearest=nn/trials,energy_increase=upmax,
                             stability=float(np.mean([np.array_equal(recall(p,W)[0],p) for p in P]))))
    return rows
