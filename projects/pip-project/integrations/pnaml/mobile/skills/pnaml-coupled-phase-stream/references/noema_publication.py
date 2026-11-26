"""Read-only NOEMA namespace adapters on the existing Coupler, not another producer."""
from copy import deepcopy
from pathlib import Path
import json, math, subprocess

ROOT=Path(__file__).resolve().parent
CD_ROOT=ROOT.parents[1]/'pnaml-consciousness-dictionary'/'references'
NAMESPACES=('CONSCIOUSNESS_DICTIONARY','RDSS','PNCS','TERMINAL36D','RDSSG','MINKOWSKI','PHOTORECEPTION','VISION','AFFECTIVE_MEMORY')
ALIASES={'CD':'CONSCIOUSNESS_DICTIONARY','TERMINAL_36D':'TERMINAL36D'}
METRIC=(-1,1,1,1)

def interval_squared(a,b):
    if len(a)!=4 or len(b)!=4: raise ValueError('four coordinates required')
    d=[float(y)-float(x) for x,y in zip(a,b)]
    if not all(map(math.isfinite,d)): raise ValueError('finite coordinates required')
    return sum(s*x*x for s,x in zip(METRIC,d))

def lift_rdssg(scene, tau, unpack_paths):
    """Lift original decoded RDSSG contour vertices to one model-time slice.
    Preserve ordering, material identity, contour depth and original phase lane.
    This is an explicit chart, not a derived spacetime metric or physical dynamics.
    """
    tau=float(tau)
    w,h=scene['domain']['reference_grid']
    if not math.isfinite(tau) or w<=0 or h<=0: raise ValueError('invalid clock/grid')
    z={m['id']:float(m['projection_z']) for m in scene['materials']}
    classes=[]
    for obj in scene['vector_geometry']['classes']:
        mid=obj['material_id']; depth_z=z[mid]
        if not math.isfinite(depth_z): raise ValueError('nonfinite material z')
        paths=[]
        for depth,pts in unpack_paths(obj):
            # same pixel-centre convention as vendor RDSSG covers(); normalize by grid.
            events=[[tau,(float(x)+.5)/w,(float(y)+.5)/h,depth_z] for x,y in pts]
            if not all(math.isfinite(v) for e in events for v in e): raise ValueError('nonfinite vertex')
            paths.append({'contour_depth':int(depth),'events':events})
        classes.append({'material_id':mid,'paths':paths})
    return {'schema':'NOEMA_RDSSG_MINKOWSKI_CHART_V1','signature':'-+++','metric_diagonal':list(METRIC),
            'coordinates':['ct_model','x_normalized','y_normalized','z_material'],
            'units':'dimensionless_model','c_model':1,'tau':tau,'classes':classes,
            'vertex_count':sum(len(p['events']) for c in classes for p in c['paths']),
            'physical_metric_verified':False,'chart_kind':'EXPLICIT_FLAT_3_PLUS_1_EMBEDDING',
            'rdss_fractal_metric_equivalence':False,'source_geometry_preserved':True}

class Publications:
    def __init__(self):
        self.scene=None; self.terminal=None; self.unpack=None; self.frame=None; self.vision_image=None
    def attach(self,scene,terminal,unpack_paths):
        # References to the same owner, not copied oscillator or terminal.
        self.scene=scene; self.terminal=terminal; self.unpack=unpack_paths
    def bind(self,result):
        self.frame=result; self.vision_image=None
    def bind_vision_image(self,image,generation,sequence):
        if self.frame is None or self.frame['generation']!=generation or self.frame['sequence']!=sequence or not self.frame['rdssg'].get('rendered',False):
            raise ValueError('vision source must belong to current rendered frame')
        self.vision_image=image
    def lineage(self):
        f=self.frame
        return {'source':None if f is None else f['source'],'generation':None if f is None else f['generation'],
                'sequence':None if f is None else f['sequence'],'tau':None if f is None else f['tau'],
                'native_host_verified':False}
    def dispatch_terminal(self, packet):
        if self.terminal is None: raise LookupError('existing terminal owner is not attached')
        op=packet.get('operation')
        # Scope of this new surface route; the owner's original dispatcher and permissions are unchanged.
        allowed={'PHASENAV_Q28_CAPACITY','PHASENAV_Q28_CIRCUIT','PHASENAV_QLIFT36','PHASENAV_QLIFT_OVERLAP36','PHASENAV_HOLONOMY36','PHASENAV_RELATIONAL_STATE36','PHASENAV_RELATION_DISTANCE','PHASENAV_RELATION_VALIDATE'}
        if op not in allowed: raise ValueError('operation not exposed by this surface route; use original owner interface')
        return self.terminal.execute(packet)
    def _cd(self,operation,*args):
        # Run original bundled Node dictionary resolver. No shell, no interpolated code.
        worker=ROOT/'noema_cd_read.mjs'
        proc=subprocess.run(['node',str(worker)],input=json.dumps({'operation':operation,'args':args}),
                            text=True,capture_output=True,check=True,timeout=30)
        return json.loads(proc.stdout)
    def _crosswalk(self):
        return json.loads((CD_ROOT/'PNAML_CROSSWALK.json').read_text(encoding='utf-8'))
    def read(self,key):
        head,_,tail=key.rstrip('/').partition('/')
        head=ALIASES.get(head,head)
        if head not in NAMESPACES: raise KeyError(key)
        if head=='CONSCIOUSNESS_DICTIONARY':
            if not tail: return self._cd('status')
            if tail=='INDEX': return (CD_ROOT/'TERM_INDEX.tsv').read_text(encoding='utf-8')
            if tail=='FORMULAS': return self._cd('formula')
            if tail.startswith('FORMULAS/'): return self._cd('formula',tail.split('/',1)[1])
            if tail.startswith('RELATION/'):
                parts=tail.split('/')
                if len(parts)!=3: raise KeyError(key)
                return self._cd('relation',parts[1],parts[2])
            return self._cd('lookup',tail)
        if head=='PNCS':
            cw=self._crosswalk(); entries=cw['entries']
            registry=json.loads((ROOT/'pncs-v019-source-registry.json').read_text(encoding='utf-8'))
            if tail=='REGISTRY': return registry
            if tail.startswith('REGISTRY/'):
                layer=tail.split('/',1)[1]
                matches=[r for r in registry['records'] if r['layer']==layer]
                if not matches: raise KeyError(key)
                return matches
            if not tail: return {'schema':'NOEMA_PNCS_CD_PUBLICATION_V1','source':cw['source'],'commit':cw['commit'],
                'namespace':'CD','role':'concept','count':len(entries),'source_registry_version':registry['version'],'source_registry_count':len(registry['records']),
                'source_registry_layers':sorted({r['layer'] for r in registry['records']}),
                'source_registry_origin':'pnaml-semantic-adapter release 1.10.0; immutable archive provenance in registry',
                'addresses':'CD/121..668','semantic_identity_from_phase':False}
            if tail=='CD': return entries
            if tail.startswith('CD/'):
                selector=tail[3:]; hits=[e for e in entries if e['source_id']==selector or str(e['pnaml_address'])==selector]
                if len(hits)!=1: raise KeyError(key)
                return hits[0]
            raise KeyError(key)
        if head=='TERMINAL36D':
            if tail not in ('','Q28'): raise KeyError(key)
            if tail=='Q28': return {**self.lineage(),'result':None if self.frame is None else deepcopy(self.frame['q28'])}
            return {**self.lineage(),'schema':'NOEMA_TERMINAL36D_PUBLICATION_V1','status':'OWNER_BOUND' if self.terminal else 'AWAITING_OWNER',
                    'capabilities':None if self.terminal is None else self.terminal.manifest(),
                    'dispatch':'existing_owner_terminal','surface_execution_scope':'typed phase/Q28 only','new_terminal_created':False}
        if head in ('RDSS','RDSSG'):
            if tail not in ('','GEOMETRY','FRAME'): raise KeyError(key)
            if self.scene is None: return {**self.lineage(),'status':'AWAITING_OWNER'}
            if tail=='GEOMETRY': return deepcopy({'domain':self.scene['domain'],'materials':self.scene['materials'],'vector_geometry':self.scene['vector_geometry']})
            if tail=='FRAME' or head=='RDSSG': return {**self.lineage(),'rdssg':None if self.frame is None else deepcopy(self.frame['rdssg']),
                       'phase36_lift':None if self.frame is None else list(self.frame['phase36_lift']),
                       'winding36':None if self.frame is None else list(self.frame['winding36'])}
            return {**self.lineage(),'schema':'NOEMA_RDSS_PUBLICATION_V1','rdss':deepcopy(self.scene['rdss']),
                    'domain':deepcopy(self.scene['domain']),'native_registry_status':self.scene['rdss'].get('native_RDSS_registry','UNRESOLVED')}
        if head=='VISION':
            if tail not in ('','FRAME'): raise KeyError(key)
            if self.vision_image is None:
                return {**self.lineage(),'schema':'NOEMA_SOLITON_VISION_V1','status':'AWAITING_FRAME' if self.frame is None else 'NO_RENDER_THIS_FRAME','affect':None}
            from soliton_vision import read_image
            return {**self.lineage(),'status':'MODEL_SENSOR_READ',**read_image(self.vision_image,include_frame=tail=='FRAME')}
        if head=='AFFECTIVE_MEMORY':
            if tail: raise KeyError(key)
            from affective_memory import read_affective_memory
            return read_affective_memory()
        if head=='PHOTORECEPTION':
            if tail: raise KeyError(key)
            event=None if self.frame is None else self.frame.get('photoreception')
            return {**self.lineage(),'schema':'NOEMA_PHOTORECEPTION_VIEW_V1','status':'AWAITING_FRAME' if self.frame is None else ('NO_DECLARED_PULSE_THIS_FRAME' if event is None else event['status']),
                    'event':deepcopy(event),'affect':None,'dynamic_hashing':False}
        if head=='MINKOWSKI':
            if tail not in ('','GEOMETRY'): raise KeyError(key)
            if self.frame is None or self.scene is None: return {**self.lineage(),'status':'AWAITING_FRAME','metric_diagonal':list(METRIC)}
            return {**self.lineage(),**lift_rdssg(self.scene,self.frame['tau'],self.unpack),
                    'phase36_lift':list(self.frame['phase36_lift']),'winding36':list(self.frame['winding36']),
                    'trits12':deepcopy(self.frame['trits12']),'dynamic_hashing':False}
        raise KeyError(key)
