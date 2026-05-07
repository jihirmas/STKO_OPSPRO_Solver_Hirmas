import math

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

        The tester uses a 3D continuum element, so this method writes standard
        OpenSees 3D nDMaterial commands from the current SandMaterial fields.
        """
        material_type = str(self.material_type)
        tag = int(tag)

        out_file.write('\n# SandMaterial tester material: {}\n'.format(material_type))
        if material_type == 'Von-Mises':
            self._write_j2_plasticity_tcl(out_file, tag)
        elif material_type in ('Mohr-Coulomb', 'Drucker-Prager'):
            self._write_drucker_prager_tcl(out_file, tag, material_type)
        else:
            raise ValueError('Unsupported SandMaterial type: {}'.format(material_type))
        out_file.write('\n')
        return tag

    def _write_j2_plasticity_tcl(self, out_file, tag: int):
        K = self._stress_magnitude(self.K)
        G = self._stress_magnitude(self.G)
        sig0 = self._stress_magnitude(self.sigma_y)
        if sig0 <= 0.0:
            sig0 = math.sqrt(3.0) * self._stress_magnitude(self.c)
        sig0 = max(sig0, 1.0e-12)

        sig_inf = sig0
        delta = 0.0
        H = 0.0
        out_file.write(
            'nDMaterial J2Plasticity {tag} {K} {G} {sig0} {sig_inf} {delta} {H}\n'.format(
                tag=tag,
                K=self._tcl_float(K),
                G=self._tcl_float(G),
                sig0=self._tcl_float(sig0),
                sig_inf=self._tcl_float(sig_inf),
                delta=self._tcl_float(delta),
                H=self._tcl_float(H),
            )
        )

    def _write_drucker_prager_tcl(self, out_file, tag: int, material_type: str):
        K = self._stress_magnitude(self.K)
        G = self._stress_magnitude(self.G)
        phi = self._angle_radians(self.phi)
        c = self._stress_magnitude(self.c)
        psi = self._angle_radians(self.psi)
        density = self._density_magnitude(self.gamma_unsat)

        if material_type == 'Mohr-Coulomb':
            out_file.write(
                '# Mohr-Coulomb parameters are mapped to DruckerPrager for this 3D tester.\n'
            )

        sigma_y, rho = self._drucker_prager_strength(phi, c)
        rho_bar = min(rho, max(0.0, self._drucker_prager_flow_parameter(psi)))

        # The current SandMaterial GUI exposes perfect-plastic strength only.
        # Keep OpenSees hardening/tension-softening terms neutral.
        Kinf = 0.0
        Ko = 0.0
        delta1 = 0.0
        delta2 = 0.0
        H = 0.0
        theta = 0.0

        out_file.write(
            (
                'nDMaterial DruckerPrager {tag} {K} {G} {sigma_y} {rho} {rho_bar} '
                '{Kinf} {Ko} {delta1} {delta2} {H} {theta} {density}\n'
            ).format(
                tag=tag,
                K=self._tcl_float(K),
                G=self._tcl_float(G),
                sigma_y=self._tcl_float(sigma_y),
                rho=self._tcl_float(rho),
                rho_bar=self._tcl_float(rho_bar),
                Kinf=self._tcl_float(Kinf),
                Ko=self._tcl_float(Ko),
                delta1=self._tcl_float(delta1),
                delta2=self._tcl_float(delta2),
                H=self._tcl_float(H),
                theta=self._tcl_float(theta),
                density=self._tcl_float(density),
            )
        )

    def _drucker_prager_strength(self, phi: float, c: float):
        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)
        denom = self._drucker_prager_denominator(sin_phi)
        rho = 2.0 * math.sqrt(2.0) * sin_phi / (math.sqrt(3.0) * denom)
        sigma_y = 6.0 * c * cos_phi / (math.sqrt(2.0) * denom)
        return max(sigma_y, 1.0e-12), max(rho, 0.0)

    def _drucker_prager_flow_parameter(self, psi: float):
        sin_psi = math.sin(psi)
        denom = self._drucker_prager_denominator(sin_psi)
        return 2.0 * math.sqrt(2.0) * sin_psi / (math.sqrt(3.0) * denom)

    def _drucker_prager_denominator(self, sin_angle: float):
        mode = str(getattr(self, 'calibration_mode', 'Inner match'))
        if mode == 'Inner match':
            denom = 3.0 + sin_angle
        else:
            denom = 3.0 - sin_angle
        return max(denom, 1.0e-12)

    @staticmethod
    def _stress_magnitude(qty) -> float:
        try:
            return float(qty.to_base_units().magnitude)
        except Exception:
            return float(getattr(qty, 'magnitude', qty))

    @staticmethod
    def _density_magnitude(qty) -> float:
        try:
            return float(qty.to('kg/m^3').magnitude)
        except Exception:
            try:
                return float(qty.to_base_units().magnitude)
            except Exception:
                return float(getattr(qty, 'magnitude', qty))

    @staticmethod
    def _angle_radians(qty) -> float:
        try:
            return float(qty.to('radian').magnitude)
        except Exception:
            return float(getattr(qty, 'magnitude', qty))

    @staticmethod
    def _tcl_float(value) -> str:
        return '{:.16g}'.format(float(value))

    def __repr__(self):
        return (
            f"SandMaterial(id={int(self.id)}, name={self.name}, "
            f"type={self.material_type}, "
            f"E={self.E:.4g~P}, G={self.G:.4g~P}, K={self.K:.4g~P}, "
            f"phi={self.phi:.4g~P}, c={self.c:.4g~P})"
        )
