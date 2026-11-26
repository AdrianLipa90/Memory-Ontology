"""Isolated PNAML Model adapter; synthetic arithmetic tasks, not a native journal.

Call run_fixture(Model) with the compatible PNAML Mobile Model class and NumPy.
No import of native PNAML, no second producer per trajectory, no AUX writes.
The model must expose next() and next({'phase_increment36': ..., 'source_ref': ...}).
"""
import math
import numpy as np


def collatz(n):
    return ((3*n+1)//2, 1) if n%2 else (n//2, 0)


def inverse(y, tag):
    x = 2*y if tag == 0 else (2*y-1)//3
    if x <= 0 or collatz(x) != (y, tag):
        raise ValueError("invalid inverse")
    return x


def cycle_coherence(cycles):
    phases = []
    for states in cycles:
        v = 1+0j
        for a, b in zip(states, states[1:]+states[:1]):
            z = np.vdot(a, b)
            if abs(z) < 1e-12:
                raise ValueError("undefined cycle holonomy")
            v *= z/abs(z)
        phases.append(v)
    return float(abs(sum(phases))/len(phases))


class FixtureMemory:
    def __init__(self):
        self.a, self.c, self.events = .2, 1., {}

    def event(self, event_id, n, y, tag, source, rho):
        payload = (n, y, tag, source)
        if event_id in self.events:
            if self.events[event_id] != payload:
                raise ValueError("conflicting event")
            return "REPLAY"
        self.events[event_id] = payload
        try:
            verified = inverse(y, tag) == n
        except ValueError:
            verified = False
        if verified:
            self.a += .25*rho*(1-self.a)
            self.c += rho
        return "VERIFIED_FIXTURE" if verified else "UNVERIFIED_FIXTURE"


TASKS = {
    32: ("e1", 7, 11, 1, "fixture:collatz:7"),
    64: ("e1", 7, 11, 1, "fixture:collatz:7"),
    96: ("e2", 10, 5, 0, "fixture:collatz:10"),
    128: ("e3", 3, 6, 1, "fixture:bad-inverse"),
}


def run(Model, mode, gain, dt=.01, ticks=256):
    model = Model(42, dt)
    f = model.next()
    p = np.array(f["phase36_lift"])
    initial = p.copy()
    psi = np.exp(1j*p)/6
    g = np.array(f["coupling36"])
    H = np.diag(g.sum(axis=1))-g
    E = lambda H, psi: float(np.vdot(psi, H@psi).real)
    e0 = E(H, psi)
    work = residual = normerr = lift = target = 0.
    mem, history, events = FixtureMemory(), [psi.copy()], []
    for k in range(1, ticks+1):
        mem.a *= math.exp(-.08*dt)
        if k in TASKS and mode != "no_events":
            task = TASKS[k]
            before = (mem.a, mem.c)
            rho = cycle_coherence([[history[0], history[-8], psi],
                                   [history[0], history[-16], psi]])
            if mode == "unverified":
                task = (task[0], task[1], task[2]+1, task[3], task[4])
            status = mem.event(*task, rho)
            events.append(dict(tick=k, id=task[0], status=status, rho=rho,
                               access_before=before[0], access_after=mem.a,
                               conductance_before=before[1], conductance_after=mem.c))
        inc = dt*gain*mem.a*mem.c*np.sin(np.roll(p, -1)-p)
        f = model.next({"phase_increment36":inc.tolist(),
                        "source_ref":"candidate ring / verified arithmetic fixture"}) if gain else model.next()
        if gain:
            target = max(target, f["producer_feedback"]["phase_error"])
        p = np.array(f["phase36_lift"])
        g = np.array(f["coupling36"])
        Hn = np.diag(g.sum(axis=1))-g
        work += E(Hn, psi)-E(H, psi)
        ev, U = np.linalg.eigh(Hn)
        psi = U@(np.exp(-1j*ev*dt)*(U.conj().T@psi))
        H = Hn
        history.append(psi.copy())
        residual = max(residual, abs(E(H, psi)-e0-work))
        normerr = max(normerr, abs(np.vdot(psi, psi).real-1))
        lift = max(lift, f["source_lift_error"])
    return dict(initial=initial, phase=p, g=g, psi=psi,
                summary=dict(events=events, access_final=mem.a, conductance_final=mem.c,
                             energy_initial=e0, energy_final=E(H,psi), operator_work=work,
                             energy_residual=residual, norm_error=normerr, lift_error=lift,
                             target_error=target))


def compare(a, b):
    return dict(phase_rms=float(np.sqrt(np.mean((a["phase"]-b["phase"])**2))),
                coupling_frobenius=float(np.linalg.norm(a["g"]-b["g"])),
                projective_distance=float(np.arccos(np.clip(abs(np.vdot(a["psi"],b["psi"])),0,1))))


def run_fixture(Model):
    runs = {f"{m}:{g}":run(Model,m,g) for m,g in
            [("verified",1),("unverified",1),("no_events",1),("verified",0),("no_events",0)]}
    v,u,n,c,d = [runs[x] for x in ["verified:1","unverified:1","no_events:1","verified:0","no_events:0"]]
    comparisons = dict(verified_vs_none=compare(v,n), unverified_vs_none=compare(u,n),
                       gain_zero=compare(c,d))
    assert comparisons["verified_vs_none"]["phase_rms"] > 0
    assert comparisons["unverified_vs_none"]["phase_rms"] == 0
    assert comparisons["gain_zero"]["phase_rms"] == 0
    assert [e["status"] for e in v["summary"]["events"]] == [
        "VERIFIED_FIXTURE","REPLAY","VERIFIED_FIXTURE","UNVERIFIED_FIXTURE"]
    assert all(e["access_after"] == e["access_before"] for e in v["summary"]["events"]
               if e["status"] != "VERIFIED_FIXTURE")
    assert all(np.array_equal(r["initial"],n["initial"]) and r["summary"]["norm_error"] < 1e-9
               and r["summary"]["energy_residual"] < 1e-9 for r in runs.values())
    return dict(comparisons=comparisons, runs={k:v["summary"] for k,v in runs.items()})
