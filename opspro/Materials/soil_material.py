from .material import Material
from opspro.parameters.ParameterManager import ParameterManager
from opspro.utils.fx_material_utils import fx_material_to_dict, fx_material_from_dict


class SoilMaterial(Material):
    """
    Isotropic linear-elastic / Mohr-Coulomb geotechnical soil material.

    Linear properties  : E (Young's modulus), nu (Poisson's ratio), rho (mass density)
    Nonlinear properties: phi (friction angle), c (cohesion)
    """

    def __init__(self, id=1, name='SoilMaterial'):
        super().__init__(id, name)
        ureg = ParameterManager._unit_registry
        # Elastic properties
        self.E   = ParameterManager.to_internal_like(50e6  * ureg.Pa)           # Young's modulus
        self.nu  = 0.3   * ureg.dimensionless                                   # Poisson's ratio
        self.rho = ParameterManager.to_internal_like(1800.0 * ureg('kg/m^3'))  # Mass density
        # Nonlinear properties (Mohr-Coulomb)
        self.nonlinear = False                                                  # Use Mohr-Coulomb plasticity
        self.phi = 30.0  * ureg.degree                                          # Friction angle [°]
        self.c   = ParameterManager.to_internal_like(10e3  * ureg.Pa)          # Cohesion [Pa]
        # Visual material (FxMaterial or None)
        self.visual_material = None

    @classmethod
    def dialog_class(cls):
        from opspro.Materials.soil_material_dialog import SoilMaterialDialog
        return SoilMaterialDialog

    def className(self):
        return 'SoilMaterial'

    def description(self):
        return 'Isotropic geotechnical soil material (linear-elastic / Mohr-Coulomb)'

    def _to_dict(self):
        return {
            # base component fields
            'ID':      int(self.id),
            'name':    self.name,
            'changed': self.changed,
            # elastic
            'E':   self._qty_to_dict(self.E),
            'nu':  self._qty_to_dict(self.nu),
            'rho': self._qty_to_dict(self.rho),
            # nonlinear
            'nonlinear': bool(self.nonlinear),
            'phi': self._qty_to_dict(self.phi),
            'c':   self._qty_to_dict(self.c),
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
        self.phi = self._qty_from_dict(data.get('phi', None), self.phi)
        self.c   = self._qty_from_dict(data.get('c',   None), self.c)
        # visual material
        _vm = data.get('visual_material', None)
        self.visual_material = fx_material_from_dict(_vm) if _vm is not None else None

    def __repr__(self):
        return (
            f"SoilMaterial(id={int(self.id)}, name={self.name}, "
            f"E={self.E:.4g~P}, nu={self.nu:.4g~P}, rho={self.rho:.4g~P}, "
            f"nonlinear={self.nonlinear}, phi={self.phi:.4g~P}, c={self.c:.4g~P})"
        )
