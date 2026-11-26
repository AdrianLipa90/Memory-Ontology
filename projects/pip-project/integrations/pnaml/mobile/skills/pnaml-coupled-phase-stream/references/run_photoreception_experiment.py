"""Finite reproducible experiment using installed PNAML Model and vendor kernel.
No user state, native owner, or persistence. Prints only derived aggregate observations.
"""
import json
import numpy as np
from coupled_stream import Model
from photoreception import photo_target
from test_photoreception import SCENE,PULSE
models={k:Model(42,.01) for k in ('dark','red','blue')}
for p in models.values():p.next()
assert all(np.array_equal(models['dark'].h['batch_phi'],p.h['batch_phi']) for p in models.values())
targets={'dark':None,'red':photo_target(SCENE,{**PULSE,'wavelength_nm':700.}),'blue':photo_target(SCENE,PULSE)}
base_freq={k:p.h['batch_omega'].copy() for k,p in models.items()}
rows=[]; first=None
for step in range(1,52):
 frames={k:p.next(targets[k] if step==1 else None) for k,p in models.items()}
 for k,p in models.items():assert np.array_equal(p.h['batch_omega'],base_freq[k]);assert frames[k]['trits12'] is None
 a=np.array(frames['dark']['phase36_lift']);b=np.array(frames['blue']['phase36_lift']);c=np.array(frames['red']['phase36_lift']);d=b-a
 assert np.max(abs(c-a))<1e-12
 if step==1:
  first=frames['blue']['producer_feedback']['photoreception'];assert np.max(abs(d-np.array(first['requested_phase_increment36'])))<1e-12
 row={'sequence':frames['dark']['sequence'],'tau':frames['dark']['tau'],'phase_delta_rms_rad':float(np.sqrt(np.mean(d*d))),'red_delta_rms_rad':float(np.sqrt(np.mean((c-a)**2))),'coupling_delta_frobenius':float(np.linalg.norm(np.array(frames['blue']['coupling36'])-frames['dark']['coupling36'])),'coherence_dark':float(abs(np.mean(np.exp(1j*a)))),'coherence_blue':float(abs(np.mean(np.exp(1j*b)))),'circular_overlap':float(abs(np.mean(np.exp(1j*d)))),'max_lift_error':max(f['source_lift_error'] for f in frames.values())}
 rows.append(row)
assert rows[-1]['coupling_delta_frobenius']>0
receipt={'schema':'NOEMA_PHOTORECEPTION_EXPERIMENT_V1','scope':'isolated installed Model with bundled HTRI kernel; not full Coupler/optical runtime','seed':42,'dt':.01,'oscillators':1164,'controls':['dark','700nm subthreshold','450nm above threshold'],'pulse':first,'rows':rows,'frequency_restored':True,'trits_unknown_preserved':True,'native_host_verified':False,'full_coupler_verified':False,'affect_measured':False}
print(json.dumps(receipt,indent=2,allow_nan=False))
