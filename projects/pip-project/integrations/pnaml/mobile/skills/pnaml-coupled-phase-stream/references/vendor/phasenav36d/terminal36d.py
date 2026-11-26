from __future__ import annotations
from pathlib import Path
import hashlib,json,time,os
from .vector_kernel import batch_phase36,order_parameter,batch_sha256
from .concept_gates import concept_gate

class Terminal36D:
    def __init__(self,receipt_dir=None):
        self.receipt_dir=Path(receipt_dir) if receipt_dir else None
        if self.receipt_dir:self.receipt_dir.mkdir(parents=True,exist_ok=True)
        self.capabilities={
          'PHASENAV_VECTORIZE_BATCH':(self.vectorize_batch,False,'VECTORIZE'),
          'PHASENAV_QLIFT36':(self.qlift36,False,'VECTORIZE'),
          'PHASENAV_QLIFT_OVERLAP36':(self.qlift_overlap36,False,'VECTORIZE'),
          'PHASENAV_Q28_CAPACITY':(self.q28_capacity,False,'READ'),
          'PHASENAV_Q28_CIRCUIT':(self.q28_circuit,False,'VECTORIZE'),
          'PHASENAV_HASH_BATCH':(self.hash_batch,False,'READ'),
          'PHASENAV_INSPECT_PATH':(self.inspect_path,False,'READ'),
          'PHASENAV_LIST_DIR':(self.list_dir,False,'READ'),
          'PHASENAV_READ_BYTES':(self.read_bytes,False,'READ'),
          'PHASENAV_VALIDATE_JSON':(self.validate_json,False,'READ'),
          'PHASENAV_WRITE_CANDIDATE':(self.write_candidate,True,'WRITE'),
          'PHASENAV_COPY_ONLY':(self.copy_only,True,'COPY'),
          'PHASENAV_APPEND_RECEIPT':(self.append_receipt,True,'WRITE'),
          'PHASENAV_PHASE_ROUTE':(self.phase_route,False,'VECTORIZE'),
          'PHASENAV_PNV_ACCELERATE':(self.pnv_accelerate,False,'VECTORIZE'),
          'PHASENAV_ORBITAL_ACCELERATE':(self.orbital_accelerate,False,'VECTORIZE'),
          'PHASENAV_NEUTRINO_ACCELERATE':(self.neutrino_accelerate,False,'VECTORIZE'),
          'PHASENAV_RELATION_DISTANCE':(self.relation_distance,False,'READ'),
          'PHASENAV_RECALL_BIND':(self.recall_bind,False,'READ'),
          'PHASENAV_RELATION_VALIDATE':(self.relation_validate,False,'READ'),
          'PHASENAV_SELF_ANCHOR36':(self.self_anchor36,False,'VECTORIZE'),
          'PHASENAV_AFFECT_SALIENCE36':(self.affect_salience36,False,'VECTORIZE'),
          'PHASENAV_HOLONOMY36':(self.holonomy36,False,'VECTORIZE'),
          'PHASENAV_INTENT_BIND36':(self.intent_bind36,False,'VECTORIZE'),
          'PHASENAV_RELATIONAL_STATE36':(self.relational_state36,False,'VECTORIZE'),
          'PHASENAV_AC_MEMORY_ACTIVATE':(self.ac_memory_activate,False,'READ'),
          'PHASENAV_AC_MEMORY_RECALL':(self.ac_memory_recall,False,'READ'),
          'PHASENAV_AC_MEMORY_EVALUATE':(self.ac_memory_evaluate,False,'EXECUTE_TYPED'),
          'PHASENAV_AC_MEMORY_COUPLE36':(self.ac_memory_couple36,False,'VECTORIZE'),
          'PHASENAV_NOEMA_HYDRATE':(self.noema_hydrate,False,'READ'),
          'PHASENAV_STATE_EXPLAIN':(self.state_explain,False,'READ'),
          'PHASENAV_GITHUB_CREDENTIAL_STATUS':(self.github_credential_status,False,'READ'),
          'PHASENAV_GITHUB_REPO_STATUS':(self.github_repo_status,False,'READ'),
          'PHASENAV_GITHUB_REPO_ARCHIVE':(self.github_repo_archive,True,'WRITE'),
          'PHASENAV_GITHUB_REPO_UNARCHIVE':(self.github_repo_unarchive,True,'WRITE'),
          'PHASENAV_GITHUB_REPO_ARCHIVE_BATCH':(self.github_repo_archive_batch,True,'WRITE'),
        }
    def manifest(self):
        return {k:{'implementation_status':'AVAILABLE','mutates':m,'gate':g} for k,(_,m,g) in sorted(self.capabilities.items())}
    def execute(self,p):
        if p.get('schema')!='PHASENAV_ACTION_PACKET_V1':raise ValueError('invalid action packet')
        op=p['operation']
        if op not in self.capabilities:raise KeyError('BLOCKED_MISSING_NATIVE_PRIMITIVE')
        fn,mut,gate=self.capabilities[op]
        gv=concept_gate(gate,p.get('intent',op))
        r={'schema':'PHASENAV_EXECUTION_RECEIPT_V1','action_id':p.get('action_id'),'operation':op,'shell_used':False,'concept_gate':gv.__dict__,'started_unix_ns':time.time_ns()}
        if gv.status!='PASS':r['status']=gv.status
        else:
            try:r['result']=fn(dict(p.get('payload',{})));r['status']='PASS'
            except Exception as e:r['status']='FAIL';r['error']=f'{type(e).__name__}: {e}'
        r['finished_unix_ns']=time.time_ns(); r['receipt_sha256']=self._sha(r); self._persist(r); return r
    @staticmethod
    def _sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    def _persist(self,r):
        if self.receipt_dir:(self.receipt_dir/f"{r.get('action_id') or time.time_ns()}.json").write_text(json.dumps(r,indent=2,ensure_ascii=False))
    def vectorize_batch(self,p):
        v=batch_phase36(p.get('labels',[]));return {'shape':list(v.shape),'vectors':v.tolist(),'R':order_parameter(v).tolist()}
    def qlift36(self,p):
        import numpy as np
        from .phasenav_q28_backend import Q28PhaseNavBackend
        b=Q28PhaseNavBackend()
        state=b.encode_phase36(p["phase36"])
        psi=state.amplitudes[:36]
        return {
            "schema":"PHASENAV_QHTRI_QLIFT36_V1",
            "dimension":36,
            "basis":"QHTRI_SINGLE_EXCITATION_36",
            "mapping":"L:|j>_PhaseNav/CD -> |0...1_j...0>_QHTRI",
            "amplitude_real":psi.real.tolist(),
            "amplitude_imag":psi.imag.tolist(),
            "norm":float(np.vdot(psi,psi).real),
            "semantic_encoder_inserted":False,
            "physical_hardware_superposition_claim":False,
            "qubit_execution":{
                "backend":"PHASENAV_Q28_DYNAMIC_DENSE_V1",
                "address_qubits":6,
                "workspace_qubits":22,
                "max_qubits":28,
                "encoded_state_length":int(state.amplitudes.size),
                "physical_qpu_claim":False,
            },
        }

    def qlift_overlap36(self,p):
        import numpy as np
        from .phasenav_q28_backend import Q28PhaseNavBackend
        b=Q28PhaseNavBackend()
        a=b.encode_phase36(p["phase_a36"]).amplitudes
        c=b.encode_phase36(p["phase_b36"]).amplitudes
        z=complex(np.vdot(a,c))
        return {
            "schema":"PHASENAV_QHTRI_OVERLAP36_V1",
            "overlap_real":float(z.real),
            "overlap_imag":float(z.imag),
            "fidelity":float(abs(z)**2),
            "isometry_identity":True,
            "physical_hardware_superposition_claim":False,
            "qubit_execution":{
                "backend":"PHASENAV_Q28_DYNAMIC_DENSE_V1",
                "address_qubits":6,
                "max_qubits":28,
                "physical_qpu_claim":False,
            },
        }

    def q28_capacity(self,p):
        from .phasenav_q28_backend import Q28PhaseNavBackend
        out=Q28PhaseNavBackend().capacity_receipt()
        out["execution_mode"]="HYBRID_DENSE_6Q_SPARSE_WORKSPACE_EXACT"
        return out

    def q28_circuit(self,p):
        from .phasenav_q28_backend import Q28PhaseNavBackend
        b=Q28PhaseNavBackend()
        state=b.run_sparse_circuit(p["phase36"],p.get("gates",[]))
        return {
            "schema":"PHASENAV_Q28_CIRCUIT_RESULT_V1",
            "backend":"PHASENAV_Q28_DYNAMIC_DENSE_V1",
            "execution_mode":"EXACT_SPARSE_STATEVECTOR_WORKSPACE",
            "n_qubits":int(state.n_qubits),
            "support_size":int(state.indices.size),
            "norm":b.sparse_norm(state),
            "state_sha256":b.sparse_state_sha256(state),
            "address_qubits":6,
            "workspace_qubits":22,
            "max_qubits":28,
            "physical_qpu_claim":False,
        }

    def hash_batch(self,p):
        blobs=[x.encode() if isinstance(x,str) else bytes(x) for x in p.get('items',[])];return {'sha256':batch_sha256(blobs)}
    def inspect_path(self,p):
        q=Path(p['path']); s=q.stat(); return {'path':str(q),'is_file':q.is_file(),'is_dir':q.is_dir(),'is_symlink':q.is_symlink(),'size':s.st_size}
    def list_dir(self,p):
        q=Path(p['path']); return {'entries':[{'name':x.name,'is_file':x.is_file(),'is_dir':x.is_dir(),'is_symlink':x.is_symlink()} for x in sorted(q.iterdir(),key=lambda x:x.name)]}
    def read_bytes(self,p):
        q=Path(p['path']); raw=q.read_bytes(); return {'path':str(q),'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'hex':raw.hex() if p.get('include_hex',False) else None}
    def validate_json(self,p):
        q=Path(p['path']); obj=json.loads(q.read_text(encoding='utf-8')); return {'path':str(q),'type':type(obj).__name__,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
    def write_candidate(self,p):
        q=Path(p['path']);
        if q.exists() and q.is_symlink():raise RuntimeError('FAIL_POLICY symlink')
        q.parent.mkdir(parents=True,exist_ok=True); raw=p['content'].encode() if isinstance(p['content'],str) else bytes(p['content']); tmp=q.with_name(q.name+'.tmp'); tmp.write_bytes(raw); os.replace(tmp,q); return {'path':str(q),'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    def copy_only(self,p):
        s,d=Path(p['src']),Path(p['dst']);
        if s.is_symlink() or d.is_symlink():raise RuntimeError('FAIL_POLICY symlink')
        if d.exists():raise FileExistsError('COPY_ONLY refuses overwrite')
        raw=s.read_bytes();d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(raw);return {'src':str(s),'dst':str(d),'sha256':hashlib.sha256(raw).hexdigest()}
    def append_receipt(self,p):
        q=Path(p['path']);q.parent.mkdir(parents=True,exist_ok=True);line=json.dumps(p['record'],sort_keys=True,ensure_ascii=False)+'\n';
        with q.open('a',encoding='utf-8') as f:f.write(line)
        return {'path':str(q),'appended_sha256':hashlib.sha256(line.encode()).hexdigest()}
    def phase_route(self,p):
        labels=p.get('labels',[]); v=batch_phase36(labels); R=order_parameter(v); order=R.argsort()[::-1]; return {'route':[labels[int(i)] for i in order],'R':[float(R[int(i)]) for i in order]}
    def pnv_accelerate(self,p):
        from . import pnv_accelerators as pa
        import importlib
        mod=importlib.import_module(p['runtime_module'])
        mode=p.get('mode','sentence_phase')
        if mode=='sentence_phase': return {'vector':pa.sentence_phase_v36(p['text'],mod)}
        if mode=='sentence_phase_precise': return {'vector':pa.sentence_phase_precise_v36(p['text'],mod)}
        if mode=='mean_phase': return {'value':pa.mean_phase_v36(p['vector'],mod)}
        if mode=='order_parameter': return {'value':pa.order_parameter_v36(p['vector'],mod)}
        raise ValueError('unsupported accelerator mode')

    def orbital_accelerate(self,p):
        import importlib
        from .system_accelerators import orbital_phase_field_v36, orbital_coherence_v36
        mod=importlib.import_module(p.get('runtime_module','ciel_geometry.orbital_model'))
        spec=p.get('orbits',[])
        u=mod.OrbitalUniverse()
        for row in spec:
            u.add_orbit(str(row['attractor_id']),str(row['satellite_id']),weight=float(row.get('weight',0.5)),phase_shift=float(row.get('phase_shift',0.0)),resonance=str(row.get('resonance','1:1')))
        mode=p.get('mode','coherence')
        if mode=='phase_field': return {'phase_field':orbital_phase_field_v36(u)}
        if mode=='coherence': return {'coherence':orbital_coherence_v36(u)}
        raise ValueError('unsupported orbital accelerator mode')

    def neutrino_accelerate(self,p):
        import importlib, numpy as np
        from .system_accelerators import neutrino_channel_v36
        mod=importlib.import_module(p.get('runtime_module','ciel_geometry.noema_surface_mmap'))
        return neutrino_channel_v36(np.asarray(p['phi'],dtype=np.float64),np.asarray(p['g'],dtype=np.float64),np.asarray(p['flavor'],dtype=np.float64),None if p.get('omega') is None else np.asarray(p['omega'],dtype=np.float64),baseline_steps=float(p.get('baseline_steps',1.0)),runtime=mod)

    def relation_distance(self,p):
        from .relational_runtime import relation_distance_native
        return dict(zip(("distances","paths"),relation_distance_native(
            p["traces"],p.get("seed_ids",[]),p.get("max_hops",2),
            orchestrator_path=p["orchestrator_path"])))

    def recall_bind(self,p):
        from .relational_runtime import recall_binding_native
        return recall_binding_native(p["thought"],p["braid"],bridge_path=p["bridge_path"])

    def relation_validate(self,p):
        from .relational_runtime import validate_relations_native
        errors=validate_relations_native(p["artifacts"],deliberation_path=p["deliberation_path"])
        return {"valid":not errors,"errors":errors}

    def self_anchor36(self,p):
        from .relational_runtime import self_anchor36
        return self_anchor36(p["relational_vector"],p["self_vector"])

    def affect_salience36(self,p):
        from .relational_runtime import explicit_affect_salience36
        return explicit_affect_salience36(p["base_salience"],p.get("affect"),gain=p.get("gain",1.0))

    def holonomy36(self,p):
        from .relational_runtime import temporal_holonomy36
        return temporal_holonomy36(p["path"])

    def intent_bind36(self,p):
        from .relational_runtime import intent_bind36
        return intent_bind36(p["intent"])

    def relational_state36(self,p):
        from .relational_runtime import relational_state36
        return relational_state36(p["relational"],p["self_anchor"],p["affect_salience"],p["holonomy"],p["intent"],p.get("weights"))

    def ac_memory_activate(self,p):
        from .ac_memory_bridge import activate_read_set
        return activate_read_set(p.get("traces",[]))

    def ac_memory_recall(self,p):
        from .ac_memory_bridge import recall_to_m1
        return recall_to_m1(p["cue"],p["traces"],
            orchestrator_path=p["orchestrator_path"],
            bridge_path=p["bridge_path"],
            thought=p["thought"])

    def ac_memory_evaluate(self,p):
        from .ac_memory_bridge import ac_evaluate_with_memory
        return ac_evaluate_with_memory(p["command"],p.get("memory_context",{}),
            evaluator_path=p["evaluator_path"],
            sot_recovered=bool(p.get("sot_recovered",False)),
            no_go_scan_complete=bool(p.get("no_go_scan_complete",False)),
            matched_active_no_go=p.get("matched_active_no_go",[]),
            validation_complete=bool(p.get("validation_complete",False)),
            target_resolved=bool(p.get("target_resolved",True)))

    def ac_memory_couple36(self,p):
        from .ac_memory_bridge import couple_state36
        return couple_state36(p["relational_state"],p["m1_binding"],p.get("memory_traces",[]))

    def noema_hydrate(self,p):
        from .atomic_hydration import hydrate
        return hydrate(p["snapshot"])

    def state_explain(self,p):
        from .atomic_hydration import state_explain
        return state_explain(p["hydration_result"])
    def github_credential_status(self,p):
        from .credential_broker import github_credential_status
        return github_credential_status()

    def github_repo_status(self,p):
        from .github_repo import repo_status
        return repo_status(p["owner"],p["repo"])

    def github_repo_archive(self,p):
        from .github_repo import set_archived
        return set_archived(p["owner"],p["repo"],True,confirm=bool(p.get("confirm",False)))

    def github_repo_unarchive(self,p):
        from .github_repo import set_archived
        return set_archived(p["owner"],p["repo"],False,confirm=bool(p.get("confirm",False)))

    def github_repo_archive_batch(self,p):
        from .github_repo import set_archived_batch
        return set_archived_batch(p["owner"],list(p.get("repos",[])),bool(p.get("archived",True)),confirm=bool(p.get("confirm",False)))

