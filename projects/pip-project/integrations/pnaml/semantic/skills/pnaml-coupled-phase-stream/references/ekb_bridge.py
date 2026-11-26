"""D <-> QHTRI <-> epsilon: explicit reciprocal software-model candidate.
Source D/epsilon holonomy is retained; the feedback law below is a new model,
not a measured cosmological or neutrino interaction. No implicit gains.
"""
import numpy as np
import math
TAU=2*math.pi
class EKB:
    def __init__(self, config):
        # Source Metatime/Neutrinotime normalization. Physical parameters are
        # explicit and immutable; the coupled phase variables are model states.
        if 'cosmology' in config or 'neutrino' in config:
            if 'D_lambda' in config or 'epsilon_nu' in config:
                raise ValueError('choose derived physical inputs or explicit normalized inputs')
            c=config['cosmology']; v=config['neutrino']
            if 'Omega_lambda' in c:
                D=1.5*float(c['Omega_lambda'])
                cosmology_basis='FLAT_LCDM'
            else:
                D=float(c['Lambda_m_inv2'])*float(c['R_H_m'])**2/2
                if float(c['R_H_m'])<=0: raise ValueError('positive Hubble radius required')
                cosmology_basis='LAMBDA_RH'
            L=float(v['L_km']); E=float(v['E_GeV']); dm=float(v['delta_m2_eV2'])
            if L<0 or E<=0: raise ValueError('nonnegative baseline and positive energy required')
            e=(1.267/math.pi)*dm*L/E
            self.basis={'cosmology':c,'neutrino':v,'cosmology_basis':cosmology_basis,'epsilon_basis':'VACUUM_MASS_SQUARED_PHASE_SOURCE_NORMALIZATION'}
        else:
            D=float(config['D_lambda']); e=float(config['epsilon_nu'])
            self.basis={'cosmology_basis':'EXPLICIT_NORMALIZED_D_LAMBDA','epsilon_basis':'EXPLICIT_NORMALIZED_EPSILON_NU'}
        kd,ke=(float(config[k]) for k in ('K_D','K_epsilon'))
        n=config['winding']
        if not all(map(math.isfinite,(D,e,kd,ke))) or type(n)!=int: raise ValueError('finite parameters and integer winding required')
        self.D,self.e,self.kd,self.ke,self.n=D,e,kd,ke,n
        self.d=np.full(36,TAU*D);self.eps=np.full(36,TAU*e);self.feedback=np.zeros(36)
    def step(self, p, psi, dt, trits):
        # Euler phasors, using actual model ket phase; zero amplitude has no phase.
        q=np.angle(psi); valid=np.abs(psi)>0
        td=np.where(valid,self.kd*np.sin(self.d-q),0.)
        te=np.where(valid,self.ke*np.sin(self.eps-q),0.)
        tq=td+te;dd=-dt*td;de=-dt*te;dq=dt*tq
        self.d+=dd;self.eps+=de;self.feedback+=dq
        # Unitary phase kick; reciprocal unweighted angular increments sum to zero.
        psi=psi*np.exp(1j*dq)
        # Bombelli conjugate alternatives for explicitly declared HOLD only.
        hold=[{'group':j,'branches':[[0.,-1.],[0.,1.]]} for j,t in enumerate(trits or []) if t==0]
        expected=TAU*(self.D+self.e+self.n)
        return p+self.feedback,psi,dq,dict(schema='PNAML_EKB_DE_MODEL_V1',status='EXPLICIT_SOFTWARE_MODEL_CANDIDATE',D_lambda=self.D,epsilon_nu=self.e,physical_parameter_basis=self.basis,winding=self.n,source_expected_connection_integral=expected,measured_connection_integral=None,D_phase36_lift=self.d.tolist(),epsilon_phase36_lift=self.eps.tolist(),Q_feedback36_lift=self.feedback.tolist(),Q_kick36=dq.tolist(),reciprocity_error=float(np.max(np.abs(dd+de+dq))),bombelli_hold=hold,source_parameters_unchanged=True)
