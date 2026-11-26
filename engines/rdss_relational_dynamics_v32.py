"""V32 relational transport, clocks and network mechanics (model units)."""
from dataclasses import dataclass
from math import acosh, cos, exp, isfinite, log, pi, sin, sqrt
from cmath import exp as cexp
from .rdss_memory_mechanics_v32 import KAPPA, nonnegative, positive, unit, recall, decay


def relational_scalar(B, omega, N, A, R, phi):
    # V32 p.120: R is not the Ricci scalar.
    if A == 0 or R == 0: raise ValueError("singular source denominator")
    result=B*omega*N*phi/(A*R)+KAPPA
    if not isfinite(result): raise ValueError("nonfinite scalar")
    return result


def conformal_factor(depth):
    # Prescribed D(x), not a dynamical field equation.
    return exp(2*depth*log(2))


def disk_distance(z,w):
    if not abs(z)<1 or not abs(w)<1: raise ValueError("open Poincare disk")
    return acosh(1+2*abs(z-w)**2/((1-abs(z)**2)*(1-abs(w)**2)))


def activity(Wp,Wm):
    Wp,Wm=positive(Wp),positive(Wm)
    eta=Wp+Wm
    return eta,Wp-Wm,(Wp-Wm)/eta


def duration(segments):
    # Piecewise constant traffic densities on the relation parameter.
    return sum(activity(p,m)[0]*nonnegative(dl) for p,m,dl in segments)


def lapse(x,ref):
    return activity(*x)[0]/activity(*ref)[0]


def seam(a,b,phi):
    x=cexp(1j*phi/2)*a
    y=cexp(-1j*phi/2)*b
    return (x+y)/2,(x-y)/2


def seam_inverse(b,d,phi):
    return cexp(-1j*phi/2)*(b+d),cexp(1j*phi/2)*(b-d)


def chain_seams(frames,phases):
    if not frames or len(phases)!=len(frames)-1: raise ValueError("chain shape")
    return (frames[0]/sqrt(2),tuple(seam(a,b,p) for a,b,p in zip(frames,frames[1:],phases)),frames[-1]/sqrt(2))


def matmul(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)) for i in range(2))


def adjoint(a):
    return tuple(tuple(a[j][i].conjugate() for j in range(2)) for i in range(2))


I2=((1+0j,0j),(0j,1+0j))


def su2(a,tol=1e-9):
    if len(a)!=2 or any(len(row)!=2 for row in a): raise ValueError("2x2 required")
    if any(not isfinite(abs(x)) for row in a for x in row): raise ValueError("nonfinite matrix")
    if abs(a[0][0]*a[1][1]-a[0][1]*a[1][0]-1)>tol: raise ValueError("determinant")
    z=matmul(adjoint(a),a)
    if max(abs(z[i][j]-I2[i][j]) for i in range(2) for j in range(2))>tol: raise ValueError("not unitary")
    return a


def gauge_transform(edge,g_source,g_target):
    return matmul(matmul(su2(g_target),su2(edge)),adjoint(su2(g_source)))


def wilson_loop(edges):
    # Ordered triples (source occurrence, target occurrence, SU2 transport).
    if not edges: raise ValueError("empty loop")
    first=edges[0][0]; node=first; W=I2
    for source,target,U in edges:
        if source!=node: raise ValueError("noncomposable path")
        W=matmul(su2(U),W); node=target
    if node!=first: raise ValueError("not occurrence closed")
    return W,W[0][0]+W[1][1]


def diffusion_step(values,edges,dt):
    # Nonnegative symmetric conductance on each undirected edge (once).
    dt=nonnegative(dt); a=list(map(nonnegative,values)); out=a.copy()
    degree=[0.]*len(a); seen=set()
    for i,j,g in edges:
        if not 0<=i<len(a) or not 0<=j<len(a) or i==j: raise ValueError("edge")
        key=tuple(sorted((i,j)))
        if key in seen: raise ValueError("duplicate undirected edge")
        seen.add(key); g=nonnegative(g); degree[i]+=g; degree[j]+=g
        flux=dt*g*(a[i]-a[j]); out[i]-=flux; out[j]+=flux
    if any(dt*d>1 for d in degree): raise ValueError("explicit positivity bound")
    return out


def order_parameter(phases,harmonic=1):
    if not phases or type(harmonic)!=int or harmonic<1: raise ValueError("invalid harmonic")
    return sum(cexp(1j*harmonic*x) for x in phases)/len(phases)


def phase_rhs(theta,omega,A,drive):
    n=len(theta)
    if not n or len(omega)!=n or len(drive)!=n or len(A)!=n or any(len(row)!=n for row in A):
        raise ValueError("phase network dimensions")
    return tuple(omega[i]+sum(A[i][j]*sin(theta[j]-theta[i]) for j in range(n))+drive[i] for i in range(n))


def phase_step(theta,omega,A,drive,dt):
    # Explicit Euler reference; preserve unwrapped history.
    return tuple(t+nonnegative(dt)*v for t,v in zip(theta,phase_rhs(theta,omega,A,drive)))


def phase_readout36(V,Q,permutation=None):
    if len(V)!=36 or len(Q)!=36: raise ValueError("36 coordinates required")
    p=tuple(range(36)) if permutation is None else tuple(permutation)
    if sorted(p)!=list(range(36)): raise ValueError("invalid permutation")
    residual=tuple((Q[p[i]]-V[i]+pi)%(2*pi)-pi for i in range(36))
    z=order_parameter(residual)
    return {"residual":residual,"complex_overlap":z,"relation":abs(z)**2,
            "novelty":max(0.,1-abs(z)),"max_wrapped":max(map(abs,residual))}


def phase_address_match(V,Q,tolerance):
    return phase_readout36(V,Q)["max_wrapped"]<=nonnegative(tolerance)


def relative_phase(u,v):
    if abs(abs(u)-1)>1e-9 or abs(abs(v)-1)>1e-9: raise ValueError("unit phases required")
    return u*v.conjugate()


def goal_cost(costs,weight,discrepancy):
    return sum(map(nonnegative,costs))+nonnegative(weight)*nonnegative(discrepancy)


@dataclass(frozen=True)
class AdaptiveEdge:
    source: str
    target: str
    accessibility: float
    conductance: float
    history: tuple=()
    def __post_init__(self):
        unit(self.accessibility); nonnegative(self.conductance)
        if not self.source or not self.target or self.source==self.target: raise ValueError("typed edge")
    def elapse(self,gamma,dt):
        return AdaptiveEdge(self.source,self.target,decay(self.accessibility,gamma,dt),self.conductance,self.history)
    def update(self,event_id,source_ref,verified,eta,quality,rho):
        if not event_id or not source_ref or any(x[0]==event_id for x in self.history): raise ValueError("event provenance")
        if type(verified)!=bool: raise ValueError("evidence flag")
        a=recall(self.accessibility,eta,quality,rho) if verified else self.accessibility
        # Candidate bridge: persistent conductance reinforced only on verified events.
        c=self.conductance+unit(quality)*unit(rho) if verified else self.conductance
        return AdaptiveEdge(self.source,self.target,a,c,self.history+((event_id,source_ref,verified),))
    def phase_weight(self):
        # Candidate coupling, not source CIEL score or physical energy.
        return self.accessibility*self.conductance
