from opspro.Materials.material import Material
from opspro.parameters.ParameterManager import ParameterManager
from opspro.utils.fx_material_utils import fx_material_to_dict, fx_material_from_dict


class SandMaterial(Material):
    """
    Geotechnical sand material with multiple constitutive models.
    
    Supports:
    - Mohr-Coulomb plasticity
    - Drucker-Prager plasticity
    - Von-Mises elastoplasticity
    
    Common properties: E (Young's modulus), G (Shear modulus), K (Bulk modulus),
    nu (Poisson's ratio), gamma_unsat, gamma_sat, e_init, n_init
    """

    # Material type selector
    MATERIAL_TYPES = ['Mohr-Coulomb', 'Drucker-Prager', 'Von-Mises']
    
    # Calibration modes for Drucker-Prager
    CALIBRATION_MODES = ['Inner match', 'Outer match', 'Plane-Strain']

    def __init__(self, id=1, name='SandMaterial'):
        super().__init__(id, name)
        ureg = ParameterManager._unit_registry
        
        # ---- Elasticity properties ----
        self.E = ParameterManager.to_internal_like(50e6 * ureg.Pa)              # Young's modulus
        self.G = ParameterManager.to_internal_like(20e6 * ureg.Pa)              # Shear modulus
        self.K = ParameterManager.to_internal_like(40e6 * ureg.Pa)              # Bulk modulus
        self.nu = 0.3 * ureg.dimensionless                                      # Poisson's ratio
        self.gamma_unsat = ParameterManager.to_internal_like(16000.0 * ureg('kg/m^3'))  # Unsaturated unit weight
        self.gamma_sat = ParameterManager.to_internal_like(18000.0 * ureg('kg/m^3'))    # Saturated unit weight
        self.e_init = 0.8 * ureg.dimensionless                                  # Initial void ratio
        self.n_init = 0.444 * ureg.dimensionless                                # Initial porosity
        
        # ---- Material type selector ----
        self.material_type = 'Mohr-Coulomb'  # Default type
        
        # ---- Mohr-Coulomb / Drucker-Prager common parameters ----
        self.phi = 30.0 * ureg.degree                                           # Friction angle
        self.c = ParameterManager.to_internal_like(10e3 * ureg.Pa)              # Cohesion
        self.psi = 0.0 * ureg.degree                                            # Dilatancy angle
        
        # ---- Von-Mises specific parameters ----
        self.sigma_y = ParameterManager.to_internal_like(100e3 * ureg.Pa)       # Yield stress (Von-Mises)
        
        # ---- Drucker-Prager calibration ----
        self.calibration_mode = 'Inner match'  # Default calibration mode
        
        # ---- Nonlinear elasticity (optional) ----
        self.nonlinear_elasticity = False                                       # Enable nonlinear elasticity
        self.E_ref = ParameterManager.to_internal_like(50e6 * ureg.Pa)          # Reference elasticity
        self.P_ref = ParameterManager.to_internal_like(100e3 * ureg.Pa)         # Reference pressure
        self.n_exp = 0.5 * ureg.dimensionless                                   # Exponent for elasticity law
        
        # Visual material (FxMaterial or None)
        self.visual_material = None
        
        # Geotechnical material tester state. This stores only UI/tester data;
        # the actual material parameters remain regular SandMaterial fields.
        self.tester_state = {}

    @classmethod
    def dialog_class(cls):
        from opspro.Materials.sand_material.sand_material_dialog import SandMaterialDialog
        return SandMaterialDialog

    def className(self):
        return 'SandMaterial'

    def description(self):
        return f'Geotechnical sand material ({self.material_type} model)'

    def _to_dict(self):
        return {
            # base component fields
            'ID': int(self.id),
            'name': self.name,
            'changed': self.changed,
            # elasticity
            'E': self._qty_to_dict(self.E),
            'G': self._qty_to_dict(self.G),
            'K': self._qty_to_dict(self.K),
            'nu': self._qty_to_dict(self.nu),
            'gamma_unsat': self._qty_to_dict(self.gamma_unsat),
            'gamma_sat': self._qty_to_dict(self.gamma_sat),
            'e_init': self._qty_to_dict(self.e_init),
            'n_init': self._qty_to_dict(self.n_init),
            # material type and parameters
            'material_type': str(self.material_type),
            'phi': self._qty_to_dict(self.phi),
            'c': self._qty_to_dict(self.c),
            'psi': self._qty_to_dict(self.psi),
            # Von-Mises specific
            'sigma_y': self._qty_to_dict(self.sigma_y),
            # Drucker-Prager calibration
            'calibration_mode': str(self.calibration_mode),
            # nonlinear elasticity
            'nonlinear_elasticity': bool(self.nonlinear_elasticity),
            'E_ref': self._qty_to_dict(self.E_ref),
            'P_ref': self._qty_to_dict(self.P_ref),
            'n_exp': self._qty_to_dict(self.n_exp),
            # visual material
            'visual_material': fx_material_to_dict(self.visual_material) if self.visual_material is not None else None,
            # tester
            'tester_state': dict(self.tester_state) if isinstance(self.tester_state, dict) else {},
        }

    def _from_dict(self, data):
        # base component fields
        self.id = data.get('ID', self.id)
        self.name = data.get('name', self.name)
        self.changed = data.get('changed', self.changed)
        # elasticity
        self.E = self._qty_from_dict(data.get('E', None), self.E)
        self.G = self._qty_from_dict(data.get('G', None), self.G)
        self.K = self._qty_from_dict(data.get('K', None), self.K)
        self.nu = self._qty_from_dict(data.get('nu', None), self.nu)
        self.gamma_unsat = self._qty_from_dict(data.get('gamma_unsat', None), self.gamma_unsat)
        self.gamma_sat = self._qty_from_dict(data.get('gamma_sat', None), self.gamma_sat)
        self.e_init = self._qty_from_dict(data.get('e_init', None), self.e_init)
        self.n_init = self._qty_from_dict(data.get('n_init', None), self.n_init)
        # material type and parameters
        self.material_type = data.get('material_type', self.material_type)
        self.phi = self._qty_from_dict(data.get('phi', None), self.phi)
        self.c = self._qty_from_dict(data.get('c', None), self.c)
        self.psi = self._qty_from_dict(data.get('psi', None), self.psi)
        # Von-Mises specific
        self.sigma_y = self._qty_from_dict(data.get('sigma_y', None), self.sigma_y)
        # Drucker-Prager calibration
        self.calibration_mode = data.get('calibration_mode', self.calibration_mode)
        # nonlinear elasticity
        self.nonlinear_elasticity = bool(data.get('nonlinear_elasticity', self.nonlinear_elasticity))
        self.E_ref = self._qty_from_dict(data.get('E_ref', None), self.E_ref)
        self.P_ref = self._qty_from_dict(data.get('P_ref', None), self.P_ref)
        self.n_exp = self._qty_from_dict(data.get('n_exp', None), self.n_exp)
        # visual material
        _vm = data.get('visual_material', None)
        self.visual_material = fx_material_from_dict(_vm) if _vm is not None else None
        # tester
        state = data.get('tester_state', {})
        self.tester_state = dict(state) if isinstance(state, dict) else {}

    def write_tcl_for_tester(self, out_file, tag: int) -> int:
        """
        Write this SandMaterial as an OpenSees nDMaterial for the geotechnical
        tester and return the material tag used by the generated TCL.

        The tester calls this hook when preparing its temporary OpenSees script.
        The real SandMaterial TCL syntax is intentionally left for the material
        writer implementation.
        """
        raise NotImplementedError(
            'SandMaterial.write_tcl_for_tester is not implemented yet. '
            'Provide the SandMaterial OpenSees TCL writer before running the tester.'
        )

    def __repr__(self):
        return (
            f"SandMaterial(id={int(self.id)}, name={self.name}, "
            f"type={self.material_type}, "
            f"E={self.E:.4g~P}, G={self.G:.4g~P}, K={self.K:.4g~P}, "
            f"phi={self.phi:.4g~P}, c={self.c:.4g~P})"
        )
