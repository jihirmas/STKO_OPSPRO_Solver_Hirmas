from .material import Material
from opspro.parameters.ParameterManager import ParameterManager
from opspro.utils.fx_material_utils import fx_material_to_dict, fx_material_from_dict


class ASDPlasticMaterial(Material):
    """
    Advanced elasto-plastic material based on OpenSees ASDPlasticMaterial3D.

    Supports combinations of:
    - Elasticity models: LinearIsotropic3D, DuncanChang
    - Yield Functions: VonMises, DruckerPrager, MohrCoulomb, TensionCutoff
    - Plastic Flow rules: Associated/Non-associated flow
    - Hardening Laws: Scalar and tensor hardening

    Reference:
        https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/ASDPlasticMaterial.html
    """

    def __init__(self, id=1, name='ASDPlasticMaterial'):
        super().__init__(id, name)
        ureg = ParameterManager._unit_registry

        # ===== ELASTICITY PARAMETERS =====
        self.elasticity_type = 'LinearIsotropic3D'
        self.E   = ParameterManager.to_internal_like(30e9   * ureg.Pa)           # Young's modulus
        self.nu  = 0.3 * ureg.dimensionless                                      # Poisson's ratio
        self.rho = ParameterManager.to_internal_like(2400.0 * ureg('kg/m^3'))   # Mass density

        # Duncan-Chang model parameters (used if elasticity_type = 'DuncanChang')
        self.ReferenceYoungsModulus = ParameterManager.to_internal_like(100e6 * ureg.Pa)
        self.ReferencePressure = ParameterManager.to_internal_like(100e3 * ureg.Pa)
        self.DuncanChang_MaxSigma3 = ParameterManager.to_internal_like(-0.01 * ureg.Pa)
        self.DuncanChang_n = 0.5 * ureg.dimensionless

        # ===== YIELD FUNCTION PARAMETERS =====
        self.yield_function = 'VonMises'

        # Von Mises
        self.VonMises_YieldStress = ParameterManager.to_internal_like(250e6 * ureg.Pa)

        # Drucker-Prager
        self.DP_xi_c = 0.0 * ureg.dimensionless
        self.DP_eta  = 0.0 * ureg.dimensionless

        # Mohr-Coulomb
        self.MC_c   = ParameterManager.to_internal_like(0e3 * ureg.Pa)
        self.MC_phi = 30.0 * ureg.degree
        self.MC_ds  = 0.001 * ureg.dimensionless

        # Tension Cutoff
        self.TC_min_stress = ParameterManager.to_internal_like(-0.1 * ureg.Pa)

        # ===== PLASTIC FLOW PARAMETERS =====
        self.plastic_flow = 'VonMises'

        # Drucker-Prager flow
        self.DP_etabar = 0.0 * ureg.dimensionless

        # Constant Dilatancy
        self.Dilatancy = 0.0 * ureg.dimensionless

        # Mohr-Coulomb flow
        self.MC_psi = 0.0 * ureg.degree

        # ===== HARDENING LAWS =====
        self.hardening_scalar = 'NullHardeningScalarFunction'
        self.hardening_tensor = 'NullHardeningTensorFunction'

        # Scalar Linear Hardening
        self.ScalarLinearHardeningParameter = 0.0 * ureg.dimensionless

        # Tensor Linear Hardening
        self.TensorLinearHardeningParameter = 0.0 * ureg.dimensionless

        # Armstrong-Frederick Hardening
        self.AF_ha = 0.0 * ureg.dimensionless
        self.AF_cr = 0.0 * ureg.dimensionless

        # ===== INTERNAL VARIABLES =====
        # BackStress (tensor, 6 components)
        self.BackStress_Value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # [σxx, σyy, σzz, σxy, σxz, σyz]

        # Scalar variables
        self.YieldStress_Value = ParameterManager.to_internal_like(250e6 * ureg.Pa)
        self.DP_cohesion_Value = ParameterManager.to_internal_like(0e3 * ureg.Pa)

        # ===== INTEGRATION OPTIONS =====
        self.f_absolute_tol = 1.0e-6 * ureg.dimensionless
        self.stress_absolute_tol = 1.0e-6 * ureg.Pa
        self.n_max_iterations = 100 * ureg.dimensionless
        self.rk45_dT_min = 1e-2 * ureg.dimensionless
        self.rk45_niter_max = 100 * ureg.dimensionless
        self.return_to_yield_surface = 'One_Step_Return'  # 'Disabled', 'One_Step_Return', 'Iterative_Return'
        self.integration_method = 'Runge_Kutta_45_Error_Control'  # Integration method
        self.tangent_type = 'Elastic'  # 'Elastic', 'Continuum', 'Secant', etc.

        # Preset provenance
        self.preset_standard    = ''
        self.preset_designation = ''

        # Visual material
        self.visual_material = None

    @classmethod
    def dialog_class(cls):
        from opspro.Materials.asd_plastic_material_dialog import ASDPlasticMaterialDialog
        return ASDPlasticMaterialDialog

    def className(self):
        return 'ASDPlasticMaterial'

    def description(self):
        return 'Advanced elasto-plastic material (ASDPlasticMaterial3D)'

    def _to_dict(self):
        return {
            # base component fields
            'ID':      int(self.id),
            'name':    self.name,
            'changed': self.changed,
            # elasticity
            'elasticity_type': self.elasticity_type,
            'E':   self._qty_to_dict(self.E),
            'nu':  self._qty_to_dict(self.nu),
            'rho': self._qty_to_dict(self.rho),
            'ReferenceYoungsModulus': self._qty_to_dict(self.ReferenceYoungsModulus),
            'ReferencePressure': self._qty_to_dict(self.ReferencePressure),
            'DuncanChang_MaxSigma3': self._qty_to_dict(self.DuncanChang_MaxSigma3),
            'DuncanChang_n': self._qty_to_dict(self.DuncanChang_n),
            # yield function
            'yield_function': self.yield_function,
            'VonMises_YieldStress': self._qty_to_dict(self.VonMises_YieldStress),
            'DP_xi_c': self._qty_to_dict(self.DP_xi_c),
            'DP_eta': self._qty_to_dict(self.DP_eta),
            'MC_c': self._qty_to_dict(self.MC_c),
            'MC_phi': self._qty_to_dict(self.MC_phi),
            'MC_ds': self._qty_to_dict(self.MC_ds),
            'TC_min_stress': self._qty_to_dict(self.TC_min_stress),
            # plastic flow
            'plastic_flow': self.plastic_flow,
            'DP_etabar': self._qty_to_dict(self.DP_etabar),
            'Dilatancy': self._qty_to_dict(self.Dilatancy),
            'MC_psi': self._qty_to_dict(self.MC_psi),
            # hardening
            'hardening_scalar': self.hardening_scalar,
            'hardening_tensor': self.hardening_tensor,
            'ScalarLinearHardeningParameter': self._qty_to_dict(self.ScalarLinearHardeningParameter),
            'TensorLinearHardeningParameter': self._qty_to_dict(self.TensorLinearHardeningParameter),
            'AF_ha': self._qty_to_dict(self.AF_ha),
            'AF_cr': self._qty_to_dict(self.AF_cr),
            # internal variables
            'BackStress_Value': self.BackStress_Value,
            'YieldStress_Value': self._qty_to_dict(self.YieldStress_Value),
            'DP_cohesion_Value': self._qty_to_dict(self.DP_cohesion_Value),
            # integration
            'f_absolute_tol': self._qty_to_dict(self.f_absolute_tol),
            'stress_absolute_tol': self._qty_to_dict(self.stress_absolute_tol),
            'n_max_iterations': self._qty_to_dict(self.n_max_iterations),
            'rk45_dT_min': self._qty_to_dict(self.rk45_dT_min),
            'rk45_niter_max': self._qty_to_dict(self.rk45_niter_max),
            'return_to_yield_surface': self.return_to_yield_surface,
            'integration_method': self.integration_method,
            'tangent_type': self.tangent_type,
            # preset
            'preset_standard': self.preset_standard,
            'preset_designation': self.preset_designation,
            # visual
            'visual_material': fx_material_to_dict(self.visual_material) if self.visual_material is not None else None,
        }

    def _from_dict(self, data):
        # base component fields
        self.id      = data.get('ID',      self.id)
        self.name    = data.get('name',    self.name)
        self.changed = data.get('changed', self.changed)
        # elasticity
        self.elasticity_type = data.get('elasticity_type', self.elasticity_type)
        self.E   = self._qty_from_dict(data.get('E',   None), self.E)
        self.nu  = self._qty_from_dict(data.get('nu',  None), self.nu)
        self.rho = self._qty_from_dict(data.get('rho', None), self.rho)
        self.ReferenceYoungsModulus = self._qty_from_dict(data.get('ReferenceYoungsModulus', None), self.ReferenceYoungsModulus)
        self.ReferencePressure = self._qty_from_dict(data.get('ReferencePressure', None), self.ReferencePressure)
        self.DuncanChang_MaxSigma3 = self._qty_from_dict(data.get('DuncanChang_MaxSigma3', None), self.DuncanChang_MaxSigma3)
        self.DuncanChang_n = self._qty_from_dict(data.get('DuncanChang_n', None), self.DuncanChang_n)
        # yield function
        self.yield_function = data.get('yield_function', self.yield_function)
        self.VonMises_YieldStress = self._qty_from_dict(data.get('VonMises_YieldStress', None), self.VonMises_YieldStress)
        self.DP_xi_c = self._qty_from_dict(data.get('DP_xi_c', None), self.DP_xi_c)
        self.DP_eta = self._qty_from_dict(data.get('DP_eta', None), self.DP_eta)
        self.MC_c = self._qty_from_dict(data.get('MC_c', None), self.MC_c)
        self.MC_phi = self._qty_from_dict(data.get('MC_phi', None), self.MC_phi)
        self.MC_ds = self._qty_from_dict(data.get('MC_ds', None), self.MC_ds)
        self.TC_min_stress = self._qty_from_dict(data.get('TC_min_stress', None), self.TC_min_stress)
        # plastic flow
        self.plastic_flow = data.get('plastic_flow', self.plastic_flow)
        self.DP_etabar = self._qty_from_dict(data.get('DP_etabar', None), self.DP_etabar)
        self.Dilatancy = self._qty_from_dict(data.get('Dilatancy', None), self.Dilatancy)
        self.MC_psi = self._qty_from_dict(data.get('MC_psi', None), self.MC_psi)
        # hardening
        self.hardening_scalar = data.get('hardening_scalar', self.hardening_scalar)
        self.hardening_tensor = data.get('hardening_tensor', self.hardening_tensor)
        self.ScalarLinearHardeningParameter = self._qty_from_dict(data.get('ScalarLinearHardeningParameter', None), self.ScalarLinearHardeningParameter)
        self.TensorLinearHardeningParameter = self._qty_from_dict(data.get('TensorLinearHardeningParameter', None), self.TensorLinearHardeningParameter)
        self.AF_ha = self._qty_from_dict(data.get('AF_ha', None), self.AF_ha)
        self.AF_cr = self._qty_from_dict(data.get('AF_cr', None), self.AF_cr)
        # internal variables
        self.BackStress_Value = data.get('BackStress_Value', self.BackStress_Value)
        self.YieldStress_Value = self._qty_from_dict(data.get('YieldStress_Value', None), self.YieldStress_Value)
        self.DP_cohesion_Value = self._qty_from_dict(data.get('DP_cohesion_Value', None), self.DP_cohesion_Value)
        # integration
        self.f_absolute_tol = self._qty_from_dict(data.get('f_absolute_tol', None), self.f_absolute_tol)
        self.stress_absolute_tol = self._qty_from_dict(data.get('stress_absolute_tol', None), self.stress_absolute_tol)
        self.n_max_iterations = self._qty_from_dict(data.get('n_max_iterations', None), self.n_max_iterations)
        self.rk45_dT_min = self._qty_from_dict(data.get('rk45_dT_min', None), self.rk45_dT_min)
        self.rk45_niter_max = self._qty_from_dict(data.get('rk45_niter_max', None), self.rk45_niter_max)
        self.return_to_yield_surface = data.get('return_to_yield_surface', self.return_to_yield_surface)
        self.integration_method = data.get('integration_method', self.integration_method)
        self.tangent_type = data.get('tangent_type', self.tangent_type)
        # preset
        self.preset_standard    = data.get('preset_standard',    '')
        self.preset_designation = data.get('preset_designation', '')
        # visual
        _vm = data.get('visual_material', None)
        self.visual_material = fx_material_from_dict(_vm) if _vm is not None else None

    def __repr__(self):
        return (
            f"ASDPlasticMaterial(id={int(self.id)}, name={self.name}, "
            f"elasticity={self.elasticity_type}, yield_fn={self.yield_function}, "
            f"plastic_flow={self.plastic_flow}, "
            f"E={self.E:.4g~P}, nu={self.nu:.4g~P}, rho={self.rho:.4g~P})"
        )