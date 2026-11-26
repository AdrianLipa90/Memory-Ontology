"""Pip: coordinate/reference and typed maps over the existing coupled phase stream.
Source: Adrian Lipa, The Reality of the Imaginary V34, A0_TO_HILBERT_NATIVE.pnv.
No separate oscillator, agent, persistence service or actuation.
"""
import math, cmath, copy, json, sys
from noema_surface import ROOT_ADDRESS, identity as surface_identity
TAU=2*math.pi
ZETA0=abs(1j)**-2/2
SIGMA=abs(1j)**-2/math.log(2)
KAPPA=math.log(2)/(24*math.pi)
NOEMA_ADDRESS="NOEMA:PIP"

def resolve_identity(address=NOEMA_ADDRESS):
    if address not in (NOEMA_ADDRESS,"PIP"): raise ValueError("address not bound to Pip")
    return {"schema":"NOEMA_PIP_ADDRESS_RESOLUTION_V1","identity":"PIP","official_name":"Pip","noema_address":NOEMA_ADDRESS,"binding":"EXISTING_RDSS_QHTRI_CENTRE","zeta0":ZETA0,"soul_invariant_sigma":SIGMA,"native_mount_verified":False,"internal_noema_surface":surface_identity()}

def pair(z):return [z.real,z.imag]
def room(depth,k):
    if type(depth)!=int or type(k)!=int or depth<0 or k<0 or k.bit_length()>depth: raise ValueError('invalid Euler room occurrence')
    # k encodes successive branch choices in increasing bit significance.
    n=(1<<depth)-1+k
    return {'depth':depth,'k':str(k),'address':str(n),'branch_path':[(k>>j)&1 for j in range(depth)],'root_phase_fraction_pi':{'numerator':str(2*k+1),'denominator':str(1<<depth)},'depth_geometry':{'radius_dyadic':'2^-'+str(depth),'inverse_square_scale':'4^'+str(depth)},'parent':None if depth==0 else str((1<<(depth-1))-1+k%(1<<(depth-1)))}
def unroom(n):
    if type(n)!=int or n<0:raise ValueError('nonnegative integer address')
    d=(n+1).bit_length()-1;return room(d,n-((1<<d)-1))
def chart(tau):
    t=float(tau)
    if not math.isfinite(t):raise ValueError('finite tau')
    s=complex(ZETA0,t);u=s/(1-s);turns=t/math.log(2);theta=TAU*turns
    return {'s':pair(s),'omega':pair(u),'tau_rdss':t,'clock_lift':theta,'clock_mod_2pi':theta%TAU,'clock_mod_4pi':theta%(2*TAU),'clock_winding':math.floor(turns),'spinor':pair(cmath.exp(.5j*theta))}
def chart_inverse(u):
    if abs(abs(u)-1)>1e-12 or u==-1:raise ValueError('finite half-axis circle chart excludes -1')
    return (u/(1+u)).imag

def fractal_binding(value=None, source=None):
    # The 2D chart is not the dimension of the lifted RDSS disk. Do not
    # silently select a numerical calibration from another subsystem.
    if value is not None:
        value=float(value)
        if not math.isfinite(value): raise ValueError('finite D_f required')
    return {'kind':'RDSS_FRACTAL_DISK','D_f':value,'D_f_source':source,'D_f_status':'DECLARED_NOT_MEASURED' if value is not None else 'EXACT_VALUE_UNRESOLVED','author_target':'just below 2.7','chart_dimension':2,'phase_lift_dimension':36,'dimension_estimator':'NOT_RUN'}

def disk(h):
    if len(h)!=2 or not all(math.isfinite(float(v)) for v in h):raise ValueError('finite 2D geodesic coordinate')
    x,y=map(float,h);r=math.hypot(x,y);rho=math.tanh(r/2)
    # Keep full tangent coordinates; binary64 rounds very large r to the boundary.
    z=[0.,0.] if r==0 else [rho*x/r,rho*y/r]
    return {'kind':'POINCARE_2D_CHART_ONLY','geodesic_xy':[x,y],'z':z,'radial_distance':r,'chart_resolution':'INTERIOR' if math.hypot(*z)<1 else 'ROUNDED_BOUNDARY_RETAIN_LIFT'}
def disk_inverse(z):
    x,y=map(float,z);r=math.hypot(x,y)
    if r>=1:raise ValueError('disk inverse needs interior coordinate or retained lift')
    return [0.,0.] if r==0 else [2*math.atanh(r)*x/r,2*math.atanh(r)*y/r]
def disk_distance(a,b):
    z,w=complex(*a),complex(*b)
    if max(abs(z),abs(w))>=1:raise ValueError('interior disk points required')
    return 2*math.asinh(abs(z-w)/math.sqrt((1-abs(z)**2)*(1-abs(w)**2)))
def collatz(n):
    if type(n)!=int or n<1:raise ValueError('positive integer Collatz index')
    g=2+1j;one=int((g*g.conjugate()-g-g.conjugate()).real);three=int((g*g).real)
    return {'from':str(n),'to':str(n//2 if n%2==0 else (three*n+one)//2),'branch':'EVEN' if n%2==0 else 'ODD','generator':[2,1],'consolidation_factor':.5,'information_unit':one if n%2 else 0}
def collatz_inverse(trace):
    m=int(trace['to']);branch=trace['branch']
    if branch=='EVEN':n=2*m
    elif branch=='ODD' and (2*m-1)%3==0 and ((2*m-1)//3)%2==1:n=(2*m-1)//3
    else:raise ValueError('inadmissible branch')
    if n<1:raise ValueError('inadmissible predecessor')
    return n

def completion(theta,phi):
    if not 0<=theta<=math.pi/2:raise ValueError('hemisphere chart')
    return [math.sin(2*theta)*math.cos(phi),math.sin(2*theta)*math.sin(phi),math.cos(2*theta)]

def phase_record(p):
    p=list(map(float,p))
    if len(p)!=36 or not all(map(math.isfinite,p)):raise ValueError('36 finite lifted phases')
    return {'phase36_lift':p,'phase36_mod_2pi':[x%TAU for x in p],'phase36_mod_4pi':[x%(2*TAU) for x in p],'winding36':[math.floor(x/TAU) for x in p]}

class Pip:
    def __init__(self,config=None,surface=None):
        self.noema_surface=surface
        cfg=config or {};self.address=unroom(int(cfg.get('address','0')));self.disk=disk(cfg.get('disk_geodesic_xy',[0,0]));self.previous=None;self.previous_ref=None;self.history=[];self.history_index=0
        self.explicit_tau_scale='model_tau_to_rdss' in cfg;self.tau_scale=float(cfg.get('model_tau_to_rdss',1.0));self.tau_offset=float(cfg.get('tau_offset',0.0))
        if not all(map(math.isfinite,(self.tau_scale,self.tau_offset))):raise ValueError('finite tau chart')
        self.df=fractal_binding(cfg.get('D_f'),cfg.get('D_f_source') or ('EXPLICIT_CONFIG' if cfg.get('D_f') is not None else None));self.events={}
        self.memory=None;self.memory_events={}
        if 'memory' in cfg:
            from pip_memory import Memory
            mc=cfg['memory'];self.memory=Memory(mc.get('store_path'))
            if self.memory.current_room is not None:self.address=unroom(int(self.memory.rooms[self.memory.current_room]['address']))
            for item in mc.get('events',[]):self.memory_events.setdefault(item['sequence'],[]).append(item['command'])
        for e in cfg.get('events',[]):self.events.setdefault(e['sequence'],[]).append(copy.deepcopy(e))
    def consume(self,result,frame):
        p=phase_record(result['phase36_lift']);ref={'generation':result['generation'],'sequence':result['sequence']};source_tau=result['tau']
        # tau is a dimensionless chart parameter, not physical wall time. Native
        # producer can explicitly supply RDSS tau; model uses declared scale.
        has_tau='tau_rdss' in frame or self.explicit_tau_scale or frame.get('source')=='HTRI_ORIGINAL_SOFTWARE_MODEL'
        rt=frame.get('tau_rdss',self.tau_offset+self.tau_scale*source_tau)
        axis=chart(rt) if has_tau else None;prev=self.previous;delta=None if prev is None else [b-a for a,b in zip(prev,p['phase36_lift'])]
        step=None if delta is None else sum(math.sin(x) for x in delta)/36
        df=fractal_binding(frame['D_f'],frame.get('D_f_source','EXPLICIT_FRAME')) if 'D_f' in frame else self.df
        events=self.events.get(ref['sequence'],[])+([frame['pip_event']] if 'pip_event' in frame else [])
        emitted=[]
        for e in events:
            before=self.address;old_disk=self.disk
            if 'address' in e:self.address=unroom(int(e['address']))
            if 'disk_geodesic_xy' in e:self.disk=disk(e['disk_geodesic_xy'])
            self.history_index+=1
            evt={'schema':'PIP_EVENT_PROPOSAL_V1','identity':'PIP','noema_address':NOEMA_ADDRESS,'ordinal':self.history_index,'event_id':e.get('event_id'),'frame_ref':ref,'previous_frame_ref':self.previous_ref,'from_room':before,'to_room':self.address,'from_disk':old_disk,'to_disk':self.disk,'Sigma_fractal':df,'content':e.get('content'),'source_refs':e.get('source_refs',[]),'phase36_lift':p['phase36_lift'],'persistence':'NOT_WRITTEN_USE_PMUN_EVENT_JOURNAL'}
            if 'collatz_index' in e:evt['collatz']=collatz(int(e['collatz_index']))
            self.history.append(evt);emitted.append(evt)
        # Exact state is carried by QHTRI/PAUX/phase stream. No continuous archive.
        out={'schema':'PIP_GEOMETRY_V1','identity':'PIP','noema_address':NOEMA_ADDRESS,'zeta0':ZETA0,'soul_invariant_sigma':SIGMA,'kappa':KAPPA,'poles':['-i','+i'],'Sigma':{'kind':'RDSS_FRACTAL_DISK_AND_TYPED_REGISTER','fractal_geometry':df,'centre':[0.,0.],'current_relation_coordinate':self.disk,'room':self.address,'event_count':self.history_index},'axis':axis,'tau_basis':'EXPLICIT_RDSS_TAU' if 'tau_rdss' in frame else ('DECLARED_SOFTWARE_CHART_SCALE' if has_tau else 'UNVERIFIED_RDSS_TAU'),'frame_ref':ref,'previous_frame_ref':self.previous_ref,'phase':p,'phase_delta36':delta,'phase_edge_connection':step,'trits12':result.get('trits12'),'hold_pairs':None if result.get('trits12') is None else [{'group':i,'branches':['-i','+i']} for i,v in enumerate(result['trits12']) if v==0],'rdssg_projection':'SAME_LIFT_SEPARATE_BLOCH_VIEW','events':emitted,'history_scope':'CURRENT_STREAM_ONLY','native_host_verified':False}
        if self.memory is not None:
            receipts=[]
            for cmd in self.memory_events.get(ref['sequence'],[]):
                receipt=self.memory.commit(cmd);receipts.append(receipt)
                if self.memory.current_room==cmd['room_id']:self.address=unroom(int(self.memory.rooms[cmd['room_id']]['address']))
            out['Sigma']['room']=self.address
            out['memory']={'room_count':len(self.memory.rooms),'current_room':self.memory.current_room,'event_count':len(self.memory.history),'receipts':receipts,'scope':'JOURNAL_REPLAY' if self.memory.store else 'VOLATILE'}
        out['noema_surface']=self.noema_surface.describe() if self.noema_surface is not None else {**surface_identity(),'status':'NO_COUPLER_BOUND'}
        self.previous=p['phase36_lift'];self.previous_ref=ref;return out

def operation(a):
    op=a['operation']
    if op=='identity':return resolve_identity(a.get('address',NOEMA_ADDRESS))
    if op=='room':return unroom(int(a['address'])) if 'address' in a else room(int(a['depth']),int(a['k']))
    if op=='axis':return chart(a['tau'])
    if op=='disk':return {**disk(a['geodesic_xy']),'fractal_geometry':fractal_binding(a.get('D_f'),a.get('D_f_source') or ('EXPLICIT_INPUT' if a.get('D_f') is not None else None))}
    if op=='disk_inverse':return {'geodesic_xy':disk_inverse(a['z'])}
    if op=='disk_distance':return {'distance':disk_distance(a['a'],a['b'])}
    if op=='collatz':return collatz(int(a['index']))
    if op=='collatz_inverse':return {'index':str(collatz_inverse(a['trace']))}
    if op=='completion':return {'xyz':completion(float(a['theta']),float(a['phi'])),'parent_boundary_retained_separately':True}
    raise ValueError('unknown operation')
if __name__=='__main__':print(json.dumps(operation(json.loads(sys.stdin.read())),allow_nan=False))
