"""Minimal scalar candidate witness, not the full QHTRI/H200 experiment."""
from collections import Counter
from math import exp, log, log2, sqrt
import json


def entropy_levels(size=4096, depth=20):
    states = list(range(1, size + 1))
    out = []
    for _ in range(depth + 1):
        out.append(sum(c / size * log2(c) for c in Counter(states).values()))
        states = [(3*n+1)//2 if n % 2 else n//2 for n in states]
    return out


LEVELS = entropy_levels()
LOG_PHI = log((1 + sqrt(5))/2)
MASS = .25*.5 + .25*.5 + .20*.5 + .15*.5 + .15*.5  # synthetic, explicit
J, E0, B, K = .65, .35, .08, 2.


def info(r):
    x = abs(log(r))/LOG_PHI
    n = int(x)
    if n >= len(LEVELS)-1:
        raise ValueError('outside calibrated depth')
    u = x-n
    delta = LEVELS[n+1]-LEVELS[n]
    return (LEVELS[n]+delta*u*u*(3-2*u),
            delta*6*u*(1-u)*(1 if r>1 else -1)/(r*LOG_PHI))


def fold(r, branch):
    return 1+branch*(2/3)*(r**-2-r*r)


def recall(a, q=.8, eta=.25):
    return a+eta*q*(1-a)


def rhs(y, gain, branch=1):
    r,p,theta,a,w = y
    I,grad = info(r)
    da = -.08*a  # event-free interval; verified recall occurs before it
    return (p, J*J/r**3-K*(r-1)-4*B*(r**3-r**-5)
            +branch*(4/3)*(r**-3+r)*E0-gain*a*MASS*grad,
            J/r**2, da, -gain*MASS*I*da)


def energy(y,gain,branch=1):
    r,p,theta,a,w = y
    return .5*(p*p+(J/r)**2)+.5*K*(r-1)**2+B*(r**-4+r**4-2)+fold(r,branch)*E0+gain*a*MASS*info(r)[0]


def run(a,gain,dt=.002, duration=4):
    y=(.8,.1,0.,a,0.)  # identical active state; different retained history
    e=energy(y,gain)
    err=0.
    def shift(v,k,h): return tuple(x+h*d for x,d in zip(v,k))
    for _ in range(round(duration/dt)):
        k1=rhs(y,gain); k2=rhs(shift(y,k1,dt/2),gain)
        k3=rhs(shift(y,k2,dt/2),gain); k4=rhs(shift(y,k3,dt),gain)
        y=tuple(x+dt*(a+2*b+2*c+d)/6 for x,a,b,c,d in zip(y,k1,k2,k3,k4))
        err=max(err,abs(energy(y,gain)+y[4]-e))
    return y,err


def witness():
    a0=.2; a1=recall(recall(recall(a0)))
    y0,e0=run(a0,.5); y1,e1=run(a1,.5)
    c0,_=run(a0,0); c1,_=run(a1,0)
    f0,_=run(a0,.5,.001); f1,_=run(a1,.5,.001)
    history_gap=a1-a0; retained_gap=y1[3]-y0[3]
    radial_gap=abs(y1[0]-y0[0]); control_gap=max(abs(x-y) for x,y in zip(c0[:3],c1[:3]))
    conv=max(abs(y0[0]-f0[0]),abs(y1[0]-f1[0]))
    fold_err=max(abs(fold(r,1)+fold(r,-1)-2) for r in (.4,.8,1.,1.5,2.))
    assert history_gap>0 and retained_gap>0
    assert abs(retained_gap-history_gap*exp(-.08*4))<1e-10
    assert radial_gap>1e-4 and control_gap<1e-12
    assert max(e0,e1)<1e-7 and conv<1e-7 and fold_err<1e-12
    return dict(status='PASS_SCALAR_CANDIDATE',history_gap=history_gap,retained_gap=retained_gap,
                radial_gap=radial_gap,control_gap=control_gap,energy_work_error=max(e0,e1),
                radial_step_convergence=conv,fold_error=fold_err,
                scope='dimensionless scalar rotating reference; synthetic inputs; not QHTRI/H200')


if __name__=='__main__':
    print(json.dumps(witness(),indent=2))
