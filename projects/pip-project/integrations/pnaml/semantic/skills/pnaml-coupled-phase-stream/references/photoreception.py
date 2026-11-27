"""Explicit Einstein photoelectric candidate for the existing owner; not an affect generator."""
import math

# Exact SI definitions converted to eV nm (h*c/e).
HC_EV_NM=6.62607015e-34*299792458.0/1.602176634e-19*1e9

def finite(value,name,lo=None,hi=None):
    if type(value) not in (int,float) or not math.isfinite(value): raise ValueError(f'{name}: finite real required')
    if lo is not None and value<lo or hi is not None and value>hi: raise ValueError(f'{name}: outside declared range')
    return float(value)

def photo_target(scene,pulse):
    """A declared local receptor on the RDSSG chart, not a physical material measurement.
    The original RDSSG four-nearest landmark interpolation distributes a candidate
    energy-to-phase increment. The natural source step remains intact.
    """
    xy=pulse['position_xy']
    if len(xy)!=2: raise ValueError('two chart coordinates required')
    x,y=[finite(v,'position_xy',0,1) for v in xy]
    mid=pulse['material_id']
    if type(mid)!=int or mid not in [m['id'] for m in scene['materials']]: raise ValueError('unknown RDSSG material id')
    wavelength=finite(pulse['wavelength_nm'],'wavelength_nm',1e-9)
    n=pulse['photon_count']
    if type(n)!=int or not 0<=n<=10**12: raise ValueError('photon_count outside numerical model range')
    work=finite(pulse['work_function_ev'],'work_function_ev',0)
    absorb=finite(pulse['absorption_fraction'],'absorption_fraction',0,1)
    yield_=finite(pulse['quantum_yield'],'quantum_yield',0,1)
    gain=finite(pulse['phase_gain_rad_per_ev'],'phase_gain_rad_per_ev',0)
    energy=HC_EV_NM/wavelength
    excess=max(energy-work,0.)
    expected_absorbed=n*absorb
    emitted=expected_absorbed*yield_ if energy>work else 0.
    kinetic=emitted*excess
    if not all(map(math.isfinite,(energy,expected_absorbed,kinetic,kinetic*gain))): raise ValueError('nonfinite energy')
    # Same 6x6 centers and four-nearest Gaussian kernel as optical_solver.
    d=[((x-(.08+.84*(i%6+.5)/6))**2+(y-(.08+.84*(i//6+.5)/6))**2,i) for i in range(36)]
    near=sorted(d)[:4]; weights=[math.exp(-a/.17**2) for a,i in near]; norm=sum(weights)
    spatial=[0.]*36
    for (_,i),w in zip(near,weights): spatial[i]=w/norm
    delta=[gain*kinetic*w for w in spatial]
    # Inverse-step feedback has a principal branch: do not silently alias a large impulse.
    if max(delta)>=math.pi: raise ValueError('phase increment exceeds principal-branch model; split explicit pulse')
    receipt={'schema':'NOEMA_PHOTORECEPTION_V1','status':'PHOTOELECTRIC_RESPONSE' if kinetic>0 else 'NO_PHOTOELECTRIC_RESPONSE',
      'source_ref':pulse['source_ref'],'position_xy':[x,y],'material_id':mid,'material_binding':'CALLER_DECLARED_RECEPTOR',
      'wavelength_nm':wavelength,'photon_count':n,'photon_energy_ev':energy,'work_function_ev':work,
      'absorption_fraction':absorb,'quantum_yield':yield_,'phase_gain_rad_per_ev':gain,'expected_absorbed_photons':expected_absorbed,
      'expected_emitted_electrons':emitted,'absorbed_energy_ev':expected_absorbed*energy,'kinetic_energy_proxy_ev':kinetic,
      'nonkinetic_absorbed_energy_ev':expected_absorbed*energy-kinetic,'spatial_weights36':spatial,'requested_phase_increment36':delta,
      'calibration':'EXPLICIT_MODEL_PARAMETERS_NOT_MEASURED','affect':None,'native_host_verified':False,'dynamic_hashing':False}
    if not isinstance(receipt['source_ref'],str) or not receipt['source_ref']: raise ValueError('source_ref required')
    return {'source_ref':receipt['source_ref'],'phase_increment36':delta,'photoreception':receipt}
