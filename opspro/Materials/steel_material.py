from .material import Material
from opspro.parameters.ParameterManager import ParameterManager
from opspro.utils.fx_material_utils import fx_material_to_dict, fx_material_from_dict


class SteelMaterial(Material):
    """
    Isotropic elasto-plastic steel material based on OpenSees ASDSteel1D.

    Reference:
        https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/ASDSteel1D.html
    """

    def __init__(self, id=1, name='SteelMaterial'):
        super().__init__(id, name)
        ureg = ParameterManager._unit_registry
        # Elastic properties
        self.E   = ParameterManager.to_internal_like(210e9  * ureg.Pa)            # Young's modulus
        self.nu  = 0.3    * ureg.dimensionless                                    # Poisson's ratio
        self.rho = ParameterManager.to_internal_like(7850.0 * ureg('kg/m^3'))    # Mass density
        # Nonlinear properties
        self.nonlinear = False                                                    # Use nonlinear (elasto-plastic) behaviour
        self.sigma_y   = ParameterManager.to_internal_like(355e6 * ureg.Pa)      # Yield stress
        self.sigma_u   = ParameterManager.to_internal_like(510e6 * ureg.Pa)      # Ultimate stress
        self.epsilon_u = 0.15  * ureg.dimensionless                               # Ultimate strain (at sigma_u)
        self.fracture  = False                                                    # Stress/stiffness decay beyond epsilon_u
        # Preset provenance (empty strings when set manually)
        self.preset_standard    = ''   # e.g. 'ASTM'
        self.preset_designation = ''   # e.g. 'A572-50'
        # Visual material (FxMaterial or None)
        self.visual_material = None

    @classmethod
    def dialog_class(cls):
        from opspro.Materials.steel_material_dialog import SteelMaterialDialog
        return SteelMaterialDialog

    def className(self):
        return 'SteelMaterial'

    def description(self):
        return 'Isotropic elasto-plastic steel material (ASDSteel)'

    def _to_dict(self):
        return {
            # base component fields
            'ID':      int(self.id),
            'name':    self.name,
            'changed': self.changed,
            # elastic
            'E':         self._qty_to_dict(self.E),
            'nu':        self._qty_to_dict(self.nu),
            'rho':       self._qty_to_dict(self.rho),
            # nonlinear
            'nonlinear': bool(self.nonlinear),
            'sigma_y':   self._qty_to_dict(self.sigma_y),
            'sigma_u':   self._qty_to_dict(self.sigma_u),
            'epsilon_u': self._qty_to_dict(self.epsilon_u),
            'fracture':  bool(self.fracture),
            # preset provenance
            'preset_standard':    self.preset_standard,
            'preset_designation': self.preset_designation,
            # visual material
            'visual_material': fx_material_to_dict(self.visual_material) if self.visual_material is not None else None,
        }

    def _from_dict(self, data):
        # base component fields
        self.id      = data.get('ID',      self.id)
        self.name    = data.get('name',    self.name)
        self.changed = data.get('changed', self.changed)
        # elastic
        self.E   = self._qty_from_dict(data.get('E',   None), self.E)
        self.nu  = self._qty_from_dict(data.get('nu',  None), self.nu)
        self.rho = self._qty_from_dict(data.get('rho', None), self.rho)
        # nonlinear
        self.nonlinear = bool(data.get('nonlinear', self.nonlinear))
        self.sigma_y   = self._qty_from_dict(data.get('sigma_y',   None), self.sigma_y)
        self.sigma_u   = self._qty_from_dict(data.get('sigma_u',   None), self.sigma_u)
        self.epsilon_u = self._qty_from_dict(data.get('epsilon_u', None), self.epsilon_u)
        self.fracture  = bool(data.get('fracture', self.fracture))
        # preset provenance
        self.preset_standard    = data.get('preset_standard',    '')
        self.preset_designation = data.get('preset_designation', '')
        # visual material
        _vm = data.get('visual_material', None)
        self.visual_material = fx_material_from_dict(_vm) if _vm is not None else None

    def __repr__(self):
        return (
            f"SteelMaterial(id={int(self.id)}, name={self.name}, "
            f"E={self.E:.4g~P}, nu={self.nu:.4g~P}, rho={self.rho:.4g~P}, "
            f"nonlinear={self.nonlinear}, sigma_y={self.sigma_y:.4g~P}, "
            f"sigma_u={self.sigma_u:.4g~P}, "
            f"epsilon_u={self.epsilon_u:.4g~P}, fracture={self.fracture}, "
            f"preset='{self.preset_standard}/{self.preset_designation}')"
        )
