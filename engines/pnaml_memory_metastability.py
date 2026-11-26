"""Candidate circulation and structural metastability diagnostics.
Requires NumPy/SciPy and source-derived A,B Hermitian graph Laplacians.
No native producer mutation. Model units only."""
import itertools
import numpy as np
from scipy.linalg import logm

def propagator(H,t):
    w,V=np.linalg.eigh(H)
    return (V*np.exp(-1j*w*t))@V.conj().T

def effective(A,B,dt):
    U=propagator(B,dt)@propagator(A,dt)
    return 1j*logm(U)/(2*dt),U

def current(H,z):
    return 2*np.imag(z.conj()[:,None]*H*z[None,:])

def cycle_test(A,B,dt=.01):
    H,U=effective(A,B,dt); K,V=effective(B,A,dt)
    z=np.ones(len(A),complex)/np.sqrt(len(A))
    J,L=current(H,z),current(K,z)
    def score(q):
        a,b,c=J[q[0],q[1]],J[q[1],q[2]],J[q[2],q[0]]
        return min(abs(a),abs(b),abs(c)) if a*b>0 and b*c>0 else -1
    i,j,k=max(itertools.combinations(range(len(z)),3),key=score)
    if score((i,j,k))<0: raise ValueError("no directed triangle found")
    cycle=lambda h:h[i,j]*h[j,k]*h[k,i]
    phase=np.exp(1j*np.linspace(0,2,len(z)))
    G=phase[:,None]*H*phase.conj()[None,:]
    control,_=effective(A,A,dt)
    return dict(current_frob=float(np.linalg.norm(J)),
        reverse_current_error=float(np.linalg.norm(J+L)),
        divergence_error=float(np.max(abs(J.sum(1)))),
        uniform_evolution_error=float(np.linalg.norm(U@z-z)),
        hermiticity_error=float(np.max(abs(H-H.conj().T))),
        gauge_current_error=float(np.linalg.norm(current(G,phase*z)-J)),
        triangle=[i,j,k],triangle_currents=[float(J[i,j]),float(J[j,k]),float(J[k,i])],
        loop_phase=float(np.angle(cycle(H))),reverse_loop_phase=float(np.angle(cycle(K))),
        gauge_loop_error=float(abs(cycle(G)-cycle(H))),
        commuting_current=float(np.linalg.norm(current(control,z))))

def relax(A,B,z0,x0,kind,kappa=50.,mu=.5,dt=.02,T=20.):
    """Separate chosen scalar potential, not a derived source memory law.
    Accessibility is a passive readout in this event-free test."""
    if kind not in ("bistable","convex"): raise ValueError("unknown potential")
    if not 0<=x0<=1 or min(kappa,mu,dt,T)<=0: raise ValueError("domain")
    D=B-A; z=z0.copy(); x=x0; heat=err=up=zerr=0.
    zero=np.sum(z)/np.sqrt(len(z))
    def field(H,z): return float(np.vdot(z,H@z).real)
    def pot(x): return kappa*(x-.2)**2*(x-.8)**2 if kind=="bistable" else kappa*.5*(x-.5)**2
    def grad(x): return 2*kappa*(x-.2)*(x-.8)*(2*x-1) if kind=="bistable" else kappa*(x-.5)
    def E(x,z): return field(A+x*D,z)+pot(x)
    e0=E(x,z); rows=[dict(t=0.,x=x,access=.2,total=e0,heat=0.)]
    for n in range(1,round(T/dt)+1):
        force=field(D,z)+grad(x)
        y=float(np.clip(x-dt*mu*force,0,1)); d=E(y,z)-E(x,z)
        heat-=d; up=max(up,d); z=propagator(A+y*D,dt)@z; x=y; et=E(x,z)
        err=max(err,abs(et+heat-e0)); zerr=max(zerr,abs(np.sum(z)/np.sqrt(len(z))-zero))
        if n%max(1,round(2/dt))==0:
            rows.append(dict(t=n*dt,x=x,access=float(.2*np.exp(-.5*n*dt)),total=et,heat=heat))
    return dict(x_final=x,access_final=float(.2*np.exp(-.5*round(T/dt)*dt)),
        energy_initial=e0,energy_final=et,heat=heat,balance_error=err,
        max_energy_increase=up,zero_error=float(zerr),samples=rows)

def run(A,B,z0):
    c=cycle_test(A,B)
    runs={f"{kind}:{x}":relax(A,B,z0,x,kind) for kind in ("bistable","convex") for x in (.2,.8)}
    fine={x:relax(A,B,z0,x,"bistable",dt=.01) for x in (.2,.8)}
    gap=lambda kind:abs(runs[f"{kind}:0.8"]["x_final"]-runs[f"{kind}:0.2"]["x_final"])
    res=dict(cycle=c,runs=runs,gap_bistable=gap("bistable"),gap_convex=gap("convex"),
        fine_step_difference=max(abs(fine[x]["x_final"]-runs[f"bistable:{x}"]["x_final"]) for x in (.2,.8)),
        max_balance_error=max(v["balance_error"] for v in runs.values()),
        max_energy_increase=max(v["max_energy_increase"] for v in runs.values()))
    assert c["reverse_current_error"]<1e-10 and c["divergence_error"]<1e-10 and c["commuting_current"]<1e-10 and c["current_frob"]>0
    assert res["gap_bistable"]>.4 and res["gap_convex"]<.01 and res["max_energy_increase"]<1e-10 and res["max_balance_error"]<1e-9
    return res
