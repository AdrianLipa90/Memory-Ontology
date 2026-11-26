"""PNCS memory law 2026-11-09 and IDT 06A/06C, local candidate. Event storage uses original PNAML continuity journal."""
import math, json, copy
import numpy as np
from pip_geometry import collatz
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"vendor"))
from pnaml_continuity import MemoryStore

def unit(x):
    x=float(x)
    if not math.isfinite(x) or not 0<=x<=1: raise ValueError('unit interval')
    return x

def kernel(x,x0,d_eff):
    x,x0,d_eff=map(float,(x,x0,d_eff))
    if not all(map(math.isfinite,(x,x0,d_eff))) or x<0 or x0<=0 or d_eff<1:raise ValueError('kernel domain')
    return (x0/(x0+x))**(d_eff-1)

def holonomy(phases):
    a=np.asarray(phases,dtype=float)
    if a.ndim!=2 or a.shape[1]!=36 or len(a)<2 or not np.isfinite(a).all():raise ValueError('closed cycle requires >=2 finite phase36 states; last-to-first closure is explicit')
    z=np.exp(1j*a)/6
    overlaps=np.einsum('ij,ij->i',z.conj(),np.roll(z,-1,axis=0))
    if np.any(abs(overlaps)<=np.finfo(float).eps*36):return None # numerical zero overlap, phase undefined
    return float(np.angle(np.prod(overlaps/abs(overlaps))))

def coherence(cycles):
    v=[(holonomy(c['phase36_cycle']),float(c['weight'])) for c in cycles]
    if any(not math.isfinite(w) or w<0 for _,w in v):raise ValueError('nonnegative finite cycle weight')
    if not v or sum(w for _,w in v)==0 or any(g is None and w>0 for g,w in v):return None
    return min(1.,float(abs(sum(w*np.exp(1j*g) for g,w in v if w>0))/sum(w for _,w in v)))

def decay(a,lam,dt):
    a=unit(a);lam,dt=float(lam),float(dt)
    if not all(map(math.isfinite,(lam,dt))) or min(lam,dt)<0:raise ValueError('nonnegative decay/time')
    return a*math.exp(-lam*dt)

def reinforce(a,eta,q,rho):
    a,eta,q,rho=map(unit,(a,eta,q,rho));return a+eta*q*rho*(1-a)

def attraction(F0,a,rho,x,x0,d_eff,r):
    F0=float(F0)
    if not math.isfinite(F0) or F0<0:raise ValueError('nonnegative scale')
    return F0*unit(a)*unit(rho)*kernel(x,x0,d_eff)*unit(r)

def entropy(p):
    p=np.asarray(p,float)
    if p.ndim!=1 or not np.isfinite(p).all() or np.any(p<0) or not np.isclose(p.sum(),1):raise ValueError('probability distribution required')
    return float(-sum(x*math.log(x) for x in p if x>0))

def fs_log(n,b):
    n,b=np.asarray(n,float),np.asarray(b,float)
    if n.shape!=(3,) or b.shape!=(3,) or not np.isfinite([n,b]).all() or not np.isclose(np.linalg.norm(n),1) or not np.isclose(np.linalg.norm(b),1):raise ValueError('unit Bloch vectors')
    dot=float(np.clip(n@b,-1,1));u=b-dot*n;norm=np.linalg.norm(u);theta=math.atan2(norm,dot)
    if norm<1e-14:
        if dot<0:return None # antipodal direction not specified
        return np.zeros(3)
    return .5*theta*u/norm

def memory_kick(n,b,q,position,velocity,e_q=None):
    n=np.asarray(n,float);xi=fs_log(n,b);q=float(q)
    if not math.isfinite(q) or q<0:raise ValueError('nonnegative q')
    if xi is None:return {'status':'ANTIPODAL_CHART_UNRESOLVED'}
    m,v=complex(*position),complex(*velocity)
    if e_q is None:
        if np.linalg.norm(xi)==0:return {'status':'ZERO_DISPLACEMENT','delta_v':[0.,0.],'velocity':list(velocity),'delta_E':0.,'delta_h':0.}
        e_q=xi/np.linalg.norm(xi)
    else:
        e_q=np.asarray(e_q,float)
        if e_q.shape!=(3,) or not np.isclose(np.linalg.norm(e_q),1) or not np.isclose(n@e_q,0):raise ValueError('unit tangent frame')
    e_p=np.cross(n,e_q);dm=complex(xi@e_q,xi@e_p);dv=q*dm
    pair=lambda z:[z.real,z.imag]
    return {'status':'OK','delta_m':pair(dm),'delta_v':pair(dv),'velocity':pair(v+dv),'delta_E':(v.conjugate()*dv).real+.5*abs(dv)**2,'delta_h':(m.conjugate()*dv).imag,'d_FS':float(np.linalg.norm(xi)),'e_Q':e_q.tolist(),'e_P':e_p.tolist()}

def transport_frame(n,b,e_q):
    n,b,e=np.asarray(n,float),np.asarray(b,float),np.asarray(e_q,float)
    xi=fs_log(n,b)
    if xi is None:return None
    if e.shape!=(3,) or not np.isclose(np.linalg.norm(e),1) or not np.isclose(n@e,0):raise ValueError('unit tangent frame')
    cross=np.cross(n,b);sn=np.linalg.norm(cross);cs=float(np.clip(n@b,-1,1))
    if sn>1e-14:
        k=cross/sn;e=cs*e+sn*np.cross(k,e)+(1-cs)*k*(k@e)
    return {'e_Q':e.tolist(),'e_P':np.cross(b,e).tolist()}

def kepler_segment(position,velocity,mu,dt,steps):
    # IDT 06A: L=|v|²/2+mu/|m|, acceleration -mu*m/|m|³.
    # Velocity Verlet is a numerical realization, not an extra physical law.
    x,v=np.asarray(position,float),np.asarray(velocity,float);mu,dt=float(mu),float(dt)
    if x.shape!=(2,) or v.shape!=(2,) or not np.isfinite([x,v]).all() or not math.isfinite(mu) or not math.isfinite(dt) or mu<0 or dt<0 or type(steps)!=int or steps<1:raise ValueError('valid explicit Kepler reference inputs')
    def accel(p):
        r=np.linalg.norm(p)
        if r==0:raise ValueError('Kepler collision at zero radius')
        return -mu*p/r**3
    def inv(p,u):return {'E':float(u@u/2-mu/np.linalg.norm(p)),'h':float(p[0]*u[1]-p[1]*u[0])}
    before=inv(x,v);h=dt/steps
    for _ in range(steps):
        vh=v+.5*h*accel(x);x=x+h*vh;v=vh+.5*h*accel(x)
    return {'position':x.tolist(),'velocity':v.tolist(),'initial':before,'final':inv(x,v),'dt':dt,'steps':steps,'integrator':'VELOCITY_VERLET_REFERENCE'}

class Memory:
    """Derived state from selected immutable PNAML events. No live AUX samples or dynamic-state hashes."""
    def __init__(self,store_path=None):
        self.rooms={};self.history=[];self.current_room=None;self.store=MemoryStore(store_path) if store_path else None
        if self.store:
            for row in self.store.db.execute('SELECT event_id,summary,cid FROM events ORDER BY seq'):
                if not row['event_id'].startswith('NOEMA:PIP:MEM:'):continue
                event=json.loads(row['summary'])
                if event.get('schema')=='PIP_MEMORY_EVENT_V1':self.apply(event['command']);self.history.append(row['event_id'])
    def close(self):
        if self.store:self.store.close()
    def apply(self,c):
        op=c['op'];key=c.get('room_id');t=float(c['t'])
        if not math.isfinite(t):raise ValueError('finite event time')
        if op=='register':
            if key in self.rooms:raise ValueError('existing room identity')
            self.rooms[key]={'room_id':key,'content_id':c['content_id'],'source_ref':c['source_ref'],'a':unit(c['a']),'lam':float(c['lam']),'t':t,'recalls':0,'address':str(c['address']),'status':c['status'],'relations':copy.deepcopy(c.get('relations',[]))}
            decay(0,c['lam'],0)
        elif op=='recall':
            r=self.rooms[key];r['a']=reinforce(decay(r['a'],r['lam'],t-r['t']),c['eta'],c['q'],c['rho']);r['t']=t;r['recalls']+=1
        elif op=='orbit_init':
            r=self.rooms[key];kepler_segment(c['position'],c['velocity'],c['mu'],0.,1);r['orbit']={'position':c['position'],'velocity':c['velocity'],'mu':c['mu'],'t':t}
        elif op=='orbit_kick':
            r=self.rooms[key];o=r['orbit'];k=memory_kick(c['n'],c['b'],c['q'],o['position'],o['velocity'],c.get('e_Q'))
            if k['status']=='ANTIPODAL_CHART_UNRESOLVED':raise ValueError('explicit geodesic required for antipodal imprint')
            if t!=o['t']:raise ValueError('supply prior Kepler segment to event time')
            o['velocity']=k['velocity'];o['last_kick']=k
        elif op=='orbit_segment':
            r=self.rooms[key];o=r['orbit'];res=kepler_segment(o['position'],o['velocity'],o['mu'],t-o['t'],c['steps']);o.update(position=res['position'],velocity=res['velocity'],t=t,last_segment=res)
        elif op=='visit':
            r=self.rooms[key];self.current_room=key
        elif op=='collatz':
            r=self.rooms[key];trace=collatz(int(r['address']));r['address']=trace['to'];r['last_collatz']=trace
        else:raise ValueError('unknown memory event')
        return copy.deepcopy(self.rooms[key])
    def commit(self,c):
        event_id='NOEMA:PIP:MEM:'+c['event_id']; key=c['room_id']
        allowed={'event_id','op','room_id','t','source_ref','importance','content_id','a','lam','address','status','relations','eta','q','rho','position','velocity','mu','n','b','e_Q','steps'}
        if set(c)-allowed:raise ValueError('not a typed semantic memory event')
        for k in ('event_id','room_id','source_ref','content_id','status','address'):
            if k in c and not isinstance(c[k],str):raise ValueError('typed text field: '+k)
        for k in ('t','importance','a','lam','eta','q','rho','mu'):
            if k in c and (isinstance(c[k],bool) or not isinstance(c[k],(int,float)) or not math.isfinite(c[k])):raise ValueError('finite scalar: '+k)
        for k,n in [('position',2),('velocity',2),('n',3),('b',3),('e_Q',3)]:
            if k in c and (not isinstance(c[k],list) or len(c[k])!=n or not all(type(v) in (int,float) and math.isfinite(v) for v in c[k])):raise ValueError('typed projective event coordinate '+k)
        if 'steps' in c and (type(c['steps'])!=int or c['steps']<1):raise ValueError('positive integration steps')
        for rel in c.get('relations',[]):
            if set(rel)!={'source','type','target','status'} or not all(isinstance(v,str) for v in rel.values()):raise ValueError('typed relation required')
        if self.store:
            old=self.store.get_event(event_id)
            if old:
                if json.loads(old['summary'])['command']!=c:raise ValueError('event identity collision')
                return {'status':'DUPLICATE','cid':old['cid'],'room':copy.deepcopy(self.rooms[key])}
        before=copy.deepcopy(self.rooms);prior_room=self.current_room
        try:
            r=self.apply(c)
            if self.store:
                # This shard is the immutable semantic command, never the raw evolving phase field.
                p={'event_id':event_id,'kind':'memory_revision','title':'Pip memory '+c['op'],'summary':json.dumps({'schema':'PIP_MEMORY_EVENT_V1','command':c},sort_keys=True,allow_nan=False),'importance':c.get('importance',1.),'source_ref':c['source_ref'],'tags':['PIP','KEPLER_COLLATZ'],'context':{'topic':'NOEMA:PIP','object_id':key},'relations':c.get('relations',[])}
                receipt=self.store.remember(p)
            else:receipt={'status':'VOLATILE_ONLY'}
        except Exception:self.rooms=before;self.current_room=prior_room;raise
        self.history.append(event_id);return {**receipt,'room':r}
    def rank(self,query,t,x0,d_eff,F0):
        # Caller supplies typed relational distance/match and actual cycle coherence; no inferred physical distance.
        out=[]
        for q in query:
            r=self.rooms[q['room_id']];a=decay(r['a'],r['lam'],float(t)-r['t']);rho=coherence(q['cycles']) if 'cycles' in q else q.get('rho')
            score=None if rho is None else attraction(F0,a,rho,q['distance'],x0,d_eff,q['relation_match'])
            out.append({'room_id':r['room_id'],'content_id':r['content_id'],'a':a,'rho':rho,'F':score,'source_ref':r['source_ref'],'status':r['status']})
        return sorted(out,key=lambda r:float('-inf') if r['F'] is None else r['F'],reverse=True)


def operation(a):
    op=a['operation']
    if op=='kernel':return {'K':kernel(a['x'],a['x0'],a['d_eff'])}
    if op=='holonomy':return {'gamma':holonomy(a['phase36_cycle'])}
    if op=='coherence':return {'rho':coherence(a['cycles'])}
    if op=='transport':return {'frame':transport_frame(a['n'],a['b'],a['e_Q'])}
    if op=='segment':return kepler_segment(a['position'],a['velocity'],a['mu'],a['dt'],a['steps'])
    if op=='entropy':return {'entropy':entropy(a['probabilities'])}
    if op=='kick':return memory_kick(a['n'],a['b'],a['q'],a['position'],a['velocity'],a.get('e_Q'))
    m=Memory(a.get('store_path'))
    try:
        if op=='commit':return m.commit(a['event'])
        if op=='rank':return {'rank':m.rank(a['query'],a['t'],a['x0'],a['d_eff'],a['F0'])}
        if op=='daily':
            if m.store is None:raise ValueError('explicit journal store_path required')
            return m.store.finalize_day(a['day'],a.get('metrics'))
        if op=='restore':return {'rooms':m.rooms,'current_room':m.current_room,'event_ids':m.history,'journal':m.store.verify() if m.store else None}
        raise ValueError('unknown memory operation')
    finally:m.close()
if __name__=='__main__':
    import sys
    from pathlib import Path
    print(json.dumps(operation(json.loads(sys.stdin.read())),allow_nan=False))
