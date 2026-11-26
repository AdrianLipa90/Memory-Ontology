"""Classical-isomorphism diagnostics; inject an existing PNAML Model.
No native AUX write. Model units, not physical energy calibration."""
import copy
import math
import numpy as np

def lap(g):
    return np.diag(g.sum(axis=1))-g

def unitary(H,t):
    w,V=np.linalg.eigh(H)
    return (V*np.exp(-1j*w*t))@V.conj().T

def energy(H,z):
    return float(np.vdot(z,H@z).real)

def spectrum(g):
    w=np.linalg.eigvalsh(lap(g))
    return dict(lambda2=float(w[1]),lambda_max=float(w[-1]),
                zero_modes=int(np.sum(abs(w)<1e-9)),
                positive_edges=int(np.count_nonzero(np.triu(g,1)>0)))

def history(Model,recalled,dt=.01,ticks=256):
    m=Model(42,dt); f=m.next()
    p=np.array(f["phase36_lift"]); g=np.array(f["coupling36"])
    H=lap(g); z=np.exp(1j*p)/6; z0=z.copy(); S0=np.sum(z)/6
    a,c=(.4,2.) if recalled else (.2,1.)
    residual=norm_error=zero_error=work=0.; e0=energy(H,z); samples=[]
    for k in range(1,ticks+1):
        inc=dt*a*c*np.sin(np.roll(p,-1)-p)
        f=m.next({"phase_increment36":inc.tolist(),"source_ref":"synthetic candidate memory intervention"})
        p=np.array(f["phase36_lift"]);g=np.array(f["coupling36"]);N=lap(g)
        work+=energy(N,z)-energy(H,z);z=unitary(N,dt)@z;H=N
        a*=math.exp(-.08*dt)
        zero_error=max(zero_error,abs(np.sum(z)/6-S0))
        norm_error=max(norm_error,abs(np.vdot(z,z).real-1))
        residual=max(residual,abs(energy(H,z)-e0-work))
        if k==1 or k%32==0:samples.append(dict(t=k*dt,**spectrum(g)))
    return m,g,z0,z,dict(zero_error=float(zero_error),zero_initial=float(abs(S0)),
                         norm_error=float(norm_error),energy_residual=float(residual),spectrum=samples)

def order_test(A,B,z):
    C=A@B-B@A; rows=[]
    for t in [.08,.04,.02,.01,.005,.0025]:
        AB=unitary(B,t)@unitary(A,t);BA=unitary(A,t)@unitary(B,t)
        avg=(A+B)/2;rot=1j*t*C/4
        gap=float(np.linalg.norm(AB-BA));leading=float(t*t*np.linalg.norm(C))
        rows.append(dict(dt=t,gap=gap,leading=leading,ratio=gap/leading if leading else None,
                         state_gap=float(np.linalg.norm((AB-BA)@z)),
                         mean_error=float(np.linalg.norm(AB-unitary(avg,2*t))),
                         bch_error=float(np.linalg.norm(AB-unitary(avg+rot,2*t))),
                         reverse_error=float(np.linalg.norm(BA-unitary(avg-rot,2*t)))))
    return dict(commutator_norm=float(np.linalg.norm(C)),rows=rows,
                zero_error=float(np.max(abs(C@np.ones(len(A))))),
                commuting_control=float(np.linalg.norm(unitary(A,.01)@unitary(A,.02)-unitary(A,.02)@unitary(A,.01))))

def retention(mA,mB,dt=.01,ticks=256):
    # Test-only cloning: match all current producer variables except batch_g.
    A=copy.deepcopy(mA); B=copy.deepcopy(mA); B.h["batch_g"]=mB.h["batch_g"].copy()
    rows=[]
    for k in range(1,ticks+1):
        a,b=A.next(),B.next()
        if k%32==0:
            ga,gb=np.array(a["coupling36"]),np.array(b["coupling36"])
            pa,pb=np.array(a["phase36_lift"]),np.array(b["phase36_lift"])
            rows.append(dict(t=k*dt,coupling_gap=float(np.linalg.norm(ga-gb)),
                             phase_rms=float(np.sqrt(np.mean((pa-pb)**2)))))
    return rows

def relax_memory(gref,g,z,dt=.01,ticks=256,k=1.,mu=.2):
    """Separate candidate law; projected gradient flow, not native HTRI Hebbian dynamics."""
    if not 0<dt*mu*k<=1 or k<=0 or mu<=0:raise ValueError("stable positive step required")
    i,j=np.triu_indices(len(g),1);ref=gref[i,j];x=g[i,j].copy();z=z.copy()
    def H(x):
        a=np.zeros_like(g);a[i,j]=a[j,i]=x;return lap(a)
    def es(x):return float(k/2*np.sum((x-ref)**2))
    h=H(x);e0=energy(h,z)+es(x);heat=0.;gradient_heat=0.;res=0.;up=0.;gradient_error=0.
    for _ in range(ticks):
        grad=abs(z[i]-z[j])**2+k*(x-ref)
        y=np.maximum(0,x-dt*mu*grad);hn=H(y)
        d=energy(hn,z)+es(y)-energy(h,z)-es(x)
        predicted=float(np.dot(grad,y-x)+k/2*np.sum((y-x)**2))
        heat-=d;gradient_heat-=predicted;gradient_error=max(gradient_error,abs(d-predicted))
        z=unitary(hn,dt)@z;x=y;h=hn
        e=energy(h,z)+es(x);res=max(res,abs(e+heat-e0));up=max(up,d)
    return dict(initial_total=e0,final_total=e,heat=heat,gradient_heat=gradient_heat,
                balance_error=res,max_increase=up,gradient_error=gradient_error)

def run(Model):
    mA,gA,z0,zA,a=history(Model,False);mB,gB,_,zB,b=history(Model,True)
    order=order_test(lap(gA),lap(gB),z0);ret=retention(mA,mB)
    thermo=relax_memory(gA,gB,zB);fine=relax_memory(gA,gB,zB,.005,512)
    assert order["commutator_norm"]>0 and order["commuting_control"]<1e-12
    assert abs(order["rows"][-1]["ratio"]-1)<.01
    assert max(a["zero_error"],b["zero_error"])<1e-10
    assert ret[-1]["phase_rms"]>0
    assert thermo["balance_error"]<1e-10 and thermo["max_increase"]<1e-12
    return dict(unreinforced=a,reinforced=b,order=order,retention=ret,thermo=thermo,fine=fine)
