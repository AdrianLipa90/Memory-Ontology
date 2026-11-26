"""RDSS Book I V32: computational memory mechanics, not physical claims."""
from math import acos, cos, exp, isfinite, log, pi, sqrt
from fractions import Fraction
from dataclasses import dataclass, replace

KAPPA = log(2)/(24*pi)
WEIGHTS = (.25,.25,.20,.15,.15)

def unit(x):
    if not isfinite(x) or not 0 <= x <= 1: raise ValueError("expected [0,1]")
    return x

def positive(x):
    if not isfinite(x) or x <= 0: raise ValueError("expected positive finite")
    return x

def nonnegative(x):
    if not isfinite(x) or x < 0: raise ValueError("expected nonnegative finite")
    return x

def entropy(p):
    unit(p)
    return -sum(x*log(x) for x in (p,1-p) if x)

def defect(p):
    return max(0.,log(2)-entropy(p))

def half_interface(p, lifted):
    unit(p)
    s=(1+2*sqrt(p*(1-p))*cos(lifted/2))/2
    return s,1-s

def action_defect(terms):
    # Each tuple: positive weight, metric norm squared, positive lambda, probability.
    return sum(positive(w)*(nonnegative(norm2)+positive(lam)*defect(p))
               for w,norm2,lam,p in terms)

def zero_axis(tau):
    return (.5+1j*tau)/(.5-1j*tau)

def contraction(depth):
    if type(depth) is not int or depth<0: raise ValueError("invalid depth")
    return Fraction(1,2**depth),4**depth

def branch_address(signs):
    # Euler-root address: e^(i*pi * odd numerator / 2^d), retained genealogy.
    signs=tuple(signs)
    numerator,denominator=1,1
    for sign in signs:
        if sign not in (-1,1): raise ValueError("expected signed branch")
        if sign==-1: numerator+=denominator*2
        denominator*=2
    return Fraction(numerator,denominator), tuple(signs)

def collatz_step(n):
    if type(n) is not int or n<=0: raise ValueError("positive integer required")
    odd=n%2
    return ((3*n+1)//2 if odd else n//2),odd

def collatz_inverse(n,odd):
    if type(n) is not int or n<=0 or odd not in (0,1): raise ValueError("invalid tag")
    x=2*n if not odd else (2*n-1)//3
    if x<=0 or collatz_step(x)!=(n,odd): raise ValueError("invalid inverse")
    return x

def parity_phase(n, max_steps=10000):
    # Unreduced itinerary until 1; repeating tail 100..., exact rational.
    if type(n) is not int or n<=0: raise ValueError("positive integer required")
    prefix=[]
    while n!=1:
        if len(prefix)>=max_steps: raise ValueError("unresolved finite itinerary")
        prefix.append(n%2)
        n=3*n+1 if n%2 else n//2
    q=Fraction(4,7)
    for b in reversed(prefix): q=(b+q)/2
    return q

def semantic_mass(e,z,d,p,b):
    # Explicit externally derived scores; no default imputation.
    return sum(w*unit(x) for w,x in zip(WEIGHTS,(e,z,d,p,b)))

def ciel_clock(dt,r,coherence,delta,mass,attractor,tau_ref=.353):
    unit(r)
    if r==1: raise ValueError("open disk")
    return nonnegative(dt)/positive(tau_ref)*(1-r*r)*unit(coherence)/(1+nonnegative(delta))*sqrt(nonnegative(mass)*nonnegative(attractor))

def kepler_period(a,m):
    return sqrt(positive(a)**3/positive(m))

def kernel(x,x0,d_eff):
    # PNCS candidate regularized kernel [20]; dimension is independent of depth.
    if not isfinite(d_eff) or d_eff<1: raise ValueError("invalid effective dimension")
    return (positive(x0)/(x0+nonnegative(x)))**(d_eff-1)

def attraction(F0,a,rho,x,x0,d_eff,typed_match):
    return nonnegative(F0)*unit(a)*unit(rho)*kernel(x,x0,d_eff)*unit(typed_match)

def decay(a,gamma,dt):
    return unit(a)*exp(-nonnegative(gamma)*nonnegative(dt))

def recall(a,eta,quality,rho):
    return unit(a)+unit(eta)*unit(quality)*unit(rho)*(1-a)

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def cross(a,b):
    x,y,z=a; u,v,w=b
    return (y*w-z*v,z*u-x*w,x*v-y*u)

def norm(a):
    return sqrt(dot(a,a))

def unitvec(a):
    if len(a)!=3 or not all(isfinite(x) for x in a) or abs(norm(a)-1)>1e-9: raise ValueError("unit Bloch vector required")
    return tuple(a)

def fs_log(n,b):
    n,b=unitvec(n),unitvec(b)
    c=max(-1.,min(1.,dot(n,b)))
    if c < -1+1e-12: raise ValueError("antipodal chart ambiguous")
    if c > 1-1e-15: return (0.,0.,0.)
    t=tuple(y-c*x for x,y in zip(n,b))
    return tuple(x*acos(c)/(2*norm(t)) for x in t)

def frame(n,e_q):
    n,e_q=unitvec(n),unitvec(e_q)
    if abs(dot(n,e_q))>1e-9: raise ValueError("non-tangent frame")
    return e_q,cross(n,e_q)

def displacement(n,b,e_q):
    x=fs_log(n,b); q,p=frame(n,e_q)
    return complex(dot(x,q),dot(x,p))

def transport(n,b,e_q):
    # Sphere parallel transport along selected shortest geodesic.
    n,b=unitvec(n),unitvec(b); q,_=frame(n,e_q)
    d=1+dot(n,b)
    if d<1e-12: raise ValueError("antipodal chart ambiguous")
    f=dot(q,b)/d
    v=tuple(t-f*(x+y) for t,x,y in zip(q,n,b))
    return frame(b,v)

def kick(v,q,dm):
    return v+nonnegative(q)*dm

def kepler_segment(z,v,mu,dt,steps):
    positive(mu); positive(dt)
    if type(steps) is not int or steps<0: raise ValueError("invalid steps")
    def acc(x): return -mu*x/positive(abs(x))**3
    for _ in range(steps):
        vh=v+dt*acc(z)/2
        z=z+dt*vh
        v=vh+dt*acc(z)/2
    return z,v

def orbit_invariants(z,v,mu):
    return abs(v)**2/2-positive(mu)/positive(abs(z)),(z.conjugate()*v).imag

@dataclass(frozen=True)
class Memory:
    identity: str
    accessibility: float
    mass_inputs: tuple
    exact_realization_mass: str
    history: tuple=()
    learned_weight: float=1.
    def __post_init__(self):
        unit(self.accessibility); semantic_mass(*self.mass_inputs)
        positive(self.learned_weight)
        if not self.identity or not self.exact_realization_mass: raise ValueError("identity/mass provenance required")
    @property
    def mass(self): return semantic_mass(*self.mass_inputs)
    def elapse(self,gamma,dt):
        return replace(self,accessibility=decay(self.accessibility,gamma,dt))
    def encounter(self,event_id,source_ref,verified,quality,rho,eta):
        if not event_id or not source_ref or any(e[0]==event_id for e in self.history):
            raise ValueError("unique event and provenance required")
        if type(verified) is not bool: raise ValueError("explicit evidence status required")
        a=recall(self.accessibility,eta,quality,rho) if verified else self.accessibility
        return replace(self,accessibility=a,learned_weight=self.learned_weight+(unit(quality)*unit(rho) if verified else 0),
                       history=self.history+((event_id,source_ref,verified),))

def routing_probabilities(weights):
    w=[positive(x) for x in weights]
    if not w: raise ValueError("no eligible route")
    return [x/sum(w) for x in w]
