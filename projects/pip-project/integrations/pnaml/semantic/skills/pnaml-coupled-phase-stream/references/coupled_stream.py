#!/usr/bin/env python3
"""Source-kernel coupled software stream; no raw host surface write or polling."""
import argparse, copy, json, math, sys, uuid, time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
from ciel_geometry import noema_surface_mmap as htri
from phasenav36d.terminal36d import Terminal36D
from phasenav36d.phasenav_q28_backend import Q28PhaseNavBackend
from phaseholomotion.semantic_bloch36 import bloch36_projection
import rdss_clusterfield as rdss
from ekb_bridge import EKB
from pip_geometry import Pip
from pip_hotel_native import CausalHotel
from noema_surface import QHTRISurface, ROOT_ADDRESS
TAU=2*math.pi

def vector(x, shape):
    a=np.asarray(x,dtype=np.float64)
    if a.shape!=shape or not np.isfinite(a).all(): raise ValueError(f'finite {shape} required')
    return a

class TerminalStream(Terminal36D):
    """Use original dispatcher and sparse Q28 kernel, omit dynamic digests in this path."""
    def __init__(self):
        super().__init__(); self.backend=Q28PhaseNavBackend()
        self.capabilities['PHASENAV_Q28_CIRCUIT']=(self.q28_stream,False,'VECTORIZE')
    @staticmethod
    def _sha(_): return None
    def q28_stream(self,p):
        state=self.backend.run_sparse_circuit(p['phase36'],p.get('gates',[]))
        return dict(n_qubits=int(state.n_qubits),support_size=int(state.indices.size),norm=float(self.backend.sparse_norm(state)),amplitude_real=state.amplitudes.real.tolist(),amplitude_imag=state.amplitudes.imag.tolist(),indices=state.indices.tolist())

class Model:
    def __init__(self,seed,dt,anchor=None):
        self.h=htri.init_htri_batch_system(seed=seed); self.dt=dt; self.seq=0; self.gen='model:'+str(uuid.uuid4())
        if anchor is not None:
            p=vector(anchor,(36,))%TAU; self.h['core_phi'][...]=p[:12];self.h['batch_phi'][...]=p[None,:]
        self.core=self.h['core_phi'].copy(); self.batch=self.h['batch_phi'].copy()
        self.cw=htri.OI*30;self.bw=1-self.cw
    def project(self,c,b):
        core=np.zeros(36);core[:12]=c
        return self.cw*core+self.bw*np.mean(b,axis=0)
    def next(self,target=None):
        a=self.h; before=self.project(self.core,self.batch)
        # Exact increments from the existing source Euler step, before its modulo reduction.
        d=a['batch_phi'][:,:,None]-a['batch_phi'][:,None,:]
        cstep=self.dt*a['core_omega']*(1+htri.OI*30)
        bstep=self.dt*(a['batch_omega']*(1+htri.OI*50*0.3)+np.sum(a['batch_g']*np.sin(d),axis=2)/36)
        feedback=None
        if target is not None:
            goal=vector(target['target_phase36'],(36,));pred=self.project(self.core+cstep,self.batch+bstep)
            delta=np.angle(np.exp(1j*(goal-pred)));mod=1+htri.OI*50*0.3
            drive=delta/(self.dt*self.bw*mod);saved=a['batch_omega'].copy()
            a['batch_omega']=saved+drive[None,:];bstep=bstep+self.dt*mod*drive[None,:]
            try:htri.evolve_htri_batch_system(a,dt=self.dt)
            finally:a['batch_omega']=saved
            feedback={'schema':'PNCS_SOURCE_MODEL_INVERSE_STEP_V1','source_ref':target.get('source_ref'),'term_id':target.get('term_id'),'drive36':drive.tolist(),'target_phase36':goal.tolist(),'phase_error':float(np.max(abs(np.angle(np.exp(1j*(goal-self.project(self.core+cstep,self.batch+bstep)))))))}
        else:htri.evolve_htri_batch_system(a,dt=self.dt)
        self.core+=cstep;self.batch+=bstep; self.seq+=1
        e=max(np.max(np.abs(np.angle(np.exp(1j*(self.core-a['core_phi']))))),np.max(np.abs(np.angle(np.exp(1j*(self.batch-a['batch_phi']))))))
        if e>1e-9: raise RuntimeError('source lift parity failed')
        lift=self.project(self.core,self.batch); g=np.mean(a['batch_g'],axis=0)*self.bw
        np.fill_diagonal(g,0)
        return dict(producer_feedback=feedback,schema='PNAML_COUPLED_FRAME_V1',generation=self.gen,sequence=self.seq,tau=self.seq*self.dt,phase36_lift=lift.tolist(),omega36=((lift-before)/self.dt).tolist(),coupling36=g.tolist(),source='HTRI_ORIGINAL_SOFTWARE_MODEL',source_lift_error=float(e),legacy_projection_wrapped=(self.project(a['core_phi'],a['batch_phi'])%TAU).tolist(),trits12=None)

class Coupler:
    def __init__(self,scene_path,width,height,render_every,ekb=None,pip=None):
        self.ekb=EKB(ekb) if ekb is not None else None
        self.noema_surface=QHTRISurface()
        self.pip=Pip(pip, surface=self.noema_surface.open(ROOT_ADDRESS))
        self.pip.causal=CausalHotel(pip)
        self.noema_surface.pip_causal=self.pip.causal
        self.term=TerminalStream();self.previous=None;self.psi=None;self.seq=None;self.generation=None;self.tau=None;self.render_every=render_every;self.width=width;self.height=height;self.count=0;self.image=None
        self.scene=json.loads(Path(scene_path).read_text());rdss.validate(self.scene)
        self.cov=rdss.covers(self.scene,width,height,1) if render_every else None
    def consume(self,f):
        if f.get('schema')!='PNAML_COUPLED_FRAME_V1':raise ValueError('frame schema')
        gen=f['generation'];seq=f['sequence'];tau=float(f['tau']);p=vector(f['phase36_lift'],(36,));w=vector(f['omega36'],(36,));g=vector(f['coupling36'],(36,36))
        if not isinstance(gen,str) or not gen or type(seq)!=int or seq<0 or not math.isfinite(tau):raise ValueError('generation, sequence, tau required')
        if self.generation is not None and (gen!=self.generation or seq!=self.seq+1 or tau<=self.tau):raise ValueError('discontinuous source: begin separate trajectory explicitly')
        trits=f.get('trits12')
        if trits is not None and (len(trits)!=12 or any(type(x)!=int or x not in (-1,0,1) for x in trits)):raise ValueError('12 typed trits required')
        H=np.diag(g.sum(axis=1))-g
        herm=float(np.max(abs(H-H.T)))
        if herm>1e-10:raise ValueError('source Laplacian not Hermitian')
        phase_state=np.exp(1j*p)/6
        if self.psi is None:self.psi=phase_state.copy()
        dt=0 if self.tau is None else tau-self.tau
        eig,U=np.linalg.eigh(H);self.psi=U@(np.exp(-1j*eig*dt)*(U.conj().T@self.psi))
        source_p=p.copy(); ekb=None
        if self.ekb is not None:
            p,self.psi,dq,ekb=self.ekb.step(p,self.psi,dt,trits)
            if dt>0:w=w+dq/dt
            phase_state=np.exp(1j*p)/6
        zpe=float(np.sum(g*(1-np.cos(p[:,None]-p[None,:])))/(2*36*35)); qexpect=float(np.vdot(phase_state,H@phase_state).real/(2*35))
        rec=self.term.execute({'schema':'PHASENAV_ACTION_PACKET_V1','action_id':gen+':'+str(seq),'operation':'PHASENAV_Q28_CIRCUIT','intent':'phase 36d vectorize H200 Q28 consume','payload':{'phase36':p.tolist(),'gates':[{'gate':'H','qubit':27},{'gate':'RZ','qubit':27,'theta':0.125},{'gate':'H','qubit':27}]}})
        if rec['status']!='PASS':raise RuntimeError(str(rec))
        q=rec['result']; self.count+=1
        out={'schema':'PNAML_COUPLED_RESULT_V1','generation':gen,'sequence':seq,'tau':tau,'source':f.get('source','EXTERNAL_DECLARED_SOURCE'),'phase36_lift':p.tolist(),'winding36':np.floor(p/TAU).astype(int).tolist(),'trits12':trits,'source_lift_error':f.get('source_lift_error'),'q28':q,'qhtri':{'norm':float(np.vdot(self.psi,self.psi).real),'hermiticity_error':herm,'potential_identity_error':abs(zpe-qexpect),'amplitude_real':self.psi.real.tolist(),'amplitude_imag':self.psi.imag.tolist(),'dt':dt},'rdssg':{'bloch36':bloch36_projection(p.tolist()),'rendered':False},'dynamic_hashing':'NONE_IN_THIS_ROUTE','host_authenticated':False,'physical_h200':False}
        if f.get('producer_feedback') is not None:out['producer_feedback']=f['producer_feedback']
        if ekb is not None:out.update(ekb=ekb,source_phase36_lift=source_p.tolist())
        if self.render_every and (self.count-1)%self.render_every==0:
            scene=copy.deepcopy(self.scene); carrier=scene['carrier'];carrier.update(q36_lift=(p/TAU).tolist(),w36=np.floor(p/TAU).astype(int).tolist(),omega36=(w/TAU).tolist(),time_tau=tau)
            rdss.validate(scene); image,diag=rdss.optical_solver(scene,self.cov)
            changed=None if self.image is None else int(np.count_nonzero(np.any(image!=self.image,axis=2)))
            self.image=image;out['rdssg'].update(rendered=True,pixels_changed_from_previous_render=changed,diagnostics=diag)
        self.noema_surface.bind(out,w.tolist(),g.tolist())
        out['noema_surface']=self.noema_surface.describe()
        out['pip']=self.pip.consume(out,f)
        out['pip']['causal']=self.pip.causal.consume(out,f)
        self.generation=gen;self.seq=seq;self.tau=tau;self.previous=p
        return out

# Existing CLI/Node API compatibility only. Native Coupler and NOEMA surface
# always retain typed integer coordinates. This is not PNAML transport.
def _legacy_causal_api_view(record):
    if not isinstance(record, dict):
        return record
    result = dict(record)
    for key in ('index','parent','incoming_link','theta_pi_units','hotel_head','occupied_past_count'):
        if type(result.get(key)) is int:
            result[key] = str(result[key])
    if isinstance(result.get('tau_effective'), dict):
        result['tau_effective'] = {k: str(v) if type(v) is int else v
                                   for k, v in result['tau_effective'].items()}
    if isinstance(result.get('source_frame'), dict):
        frame = dict(result['source_frame'])
        if type(frame.get('sequence')) is int:
            frame['sequence'] = str(frame['sequence'])
        result['source_frame'] = frame
    if isinstance(result.get('now'), dict):
        result['now'] = _legacy_causal_api_view(result['now'])
    return result


def legacy_cli_view(out):
    # Non-mutating projection solely for the already published API.
    view = dict(out)
    if isinstance(out.get('pip'), dict) and 'causal' in out['pip']:
        view['pip'] = dict(out['pip'])
        view['pip']['causal'] = _legacy_causal_api_view(out['pip']['causal'])
    if isinstance(out.get('surface_reads'), dict):
        view['surface_reads'] = {
            path: _legacy_causal_api_view(value)
                  if path.rstrip('/') == ROOT_ADDRESS+'PIP_CAUSAL'
                  or path.startswith(ROOT_ADDRESS+'PIP_CAUSAL/') else value
            for path, value in out['surface_reads'].items()
        }
    return view


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['model','input'],required=True);ap.add_argument('--ticks',type=int,default=8);ap.add_argument('--dt',type=float,default=.01);ap.add_argument('--seed',type=int,default=42);ap.add_argument('--width',type=int,default=96);ap.add_argument('--height',type=int,default=144);ap.add_argument('--render-every',type=int,default=1);ap.add_argument('--anchor-json');ap.add_argument('--last-image');ap.add_argument('--emit-frames',action='store_true');ap.add_argument('--ekb-json');ap.add_argument('--pip-json');ap.add_argument('--surface-paths-json');a=ap.parse_args()
    if a.dt<=0 or not math.isfinite(a.dt) or a.ticks<1 or a.render_every<0:raise ValueError('positive ticks/dt and nonnegative render cadence')
    c=None if a.emit_frames else Coupler(ROOT/'assets/poster_encoded.rdssg',a.width,a.height,a.render_every,json.loads(a.ekb_json) if a.ekb_json else None,json.loads(a.pip_json) if a.pip_json else None)
    if a.mode=='model':
        m=Model(a.seed,a.dt,json.loads(a.anchor_json) if a.anchor_json else None)
        cfg=json.loads(a.pip_json) if a.pip_json else {}
        targets={int(x['sequence']):x for x in cfg.get('producer_feedback',[])}
        frames=(m.next(targets.get(k)) for k in range(1,a.ticks+1))
    else:frames=(json.loads(line) for line in sys.stdin if line.strip())
    paths=json.loads(a.surface_paths_json) if a.surface_paths_json else []
    for f in frames:
        out=f if a.emit_frames else c.consume(f)
        if paths and c is not None:out['surface_reads']={path:c.noema_surface.read(path) for path in paths}
        print(json.dumps(legacy_cli_view(out),allow_nan=False,separators=(',',':')),flush=True)
    if c is not None and c.pip.memory is not None:c.pip.memory.close()
    if a.last_image and c is not None and c.image is not None:
        from PIL import Image
        Image.fromarray(c.image).save(a.last_image)
if __name__=='__main__':main()
