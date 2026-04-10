from .material import Material
from opspro.parameters.ParameterManager import ParameterManager
from opspro.Materials.presets.concrete_presets import mc2010_fracture_energy
from opspro.utils.fx_material_utils import fx_material_to_dict, fx_material_from_dict


class ConcreteMaterial(Material):
    """
    Isotropic concrete material with optional nonlinear fracture-based behaviour.

    Nonlinear model is based on a smeared-crack / damage approach where the
    softening laws are governed by the tensile and compressive fracture energies
    (Gt, Gc) per unit area following Bazant's crack-band theory.

    References:
        https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/ASDConcrete3D.html
        https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/ASDConcrete1D.html
    """

    def __init__(self, id=1, name='ConcreteMaterial'):
        super().__init__(id, name)
        ureg = ParameterManager._unit_registry
        # Elastic properties
        self.E   = ParameterManager.to_internal_like(30e9   * ureg.Pa)           # Young's modulus
        self.nu  = 0.2    * ureg.dimensionless                                   # Poisson's ratio
        self.rho = ParameterManager.to_internal_like(2400.0 * ureg('kg/m^3'))   # Mass density
        # Nonlinear properties
        self.nonlinear            = False                                         # Use nonlinear (fracture) behaviour
        self.auto_fracture_energy = True                                          # Auto-compute Gt, Gc from fcp via MC2010
        self.fcp = ParameterManager.to_internal_like(30e6   * ureg.Pa)           # Peak compressive strength
        self.ft  = ParameterManager.to_internal_like(2.9e6  * ureg.Pa)           # Peak tensile strength
        # Gt/Gc: computed from fcp via Model Code 2010
        _Gt, _Gc = mc2010_fracture_energy(float(self.fcp.to('MPa').magnitude))
        self.Gt = ParameterManager.to_internal_like(_Gt * ureg('J/m^2'))         # Tensile fracture energy
        self.Gc = ParameterManager.to_internal_like(_Gc * ureg('J/m^2'))         # Compressive fracture energy
        # Preset provenance (empty strings when set manually)
        self.preset_standard    = ''   # e.g. 'EN 1992'
        self.preset_designation = ''   # e.g. 'C30/37'
        # Visual material (FxMaterial or None)
        self.visual_material = None

    @classmethod
    def dialog_class(cls):
        from opspro.Materials.concrete_material_dialog import ConcreteMaterialDialog
        return ConcreteMaterialDialog

    def className(self):
        return 'ConcreteMaterial'

    def description(self):
        return 'Isotropic concrete material with fracture-based softening (ASDConcrete)'

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
            'nonlinear':            bool(self.nonlinear),
            'auto_fracture_energy': bool(self.auto_fracture_energy),
            'fcp': self._qty_to_dict(self.fcp),
            'ft':  self._qty_to_dict(self.ft),
            'Gt':  self._qty_to_dict(self.Gt),
            'Gc':  self._qty_to_dict(self.Gc),
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
        self.nonlinear            = bool(data.get('nonlinear',            self.nonlinear))
        self.auto_fracture_energy = bool(data.get('auto_fracture_energy', self.auto_fracture_energy))
        self.fcp = self._qty_from_dict(data.get('fcp', None), self.fcp)
        self.ft  = self._qty_from_dict(data.get('ft',  None), self.ft)
        self.Gt  = self._qty_from_dict(data.get('Gt',  None), self.Gt)
        self.Gc  = self._qty_from_dict(data.get('Gc',  None), self.Gc)
        if self.auto_fracture_energy:
            ureg = ParameterManager._unit_registry
            _Gt, _Gc = mc2010_fracture_energy(float(self.fcp.to('MPa').magnitude))
            self.Gt = _Gt * ureg('J/m^2')
            self.Gc = _Gc * ureg('J/m^2')
        # preset provenance
        self.preset_standard    = data.get('preset_standard',    '')
        self.preset_designation = data.get('preset_designation', '')
        # visual material
        _vm = data.get('visual_material', None)
        self.visual_material = fx_material_from_dict(_vm) if _vm is not None else None

    def __repr__(self):
        return (
            f"ConcreteMaterial(id={int(self.id)}, name={self.name}, "
            f"E={self.E:.4g~P}, nu={self.nu:.4g~P}, rho={self.rho:.4g~P}, "
            f"nonlinear={self.nonlinear}, auto_fracture_energy={self.auto_fracture_energy}, "
            f"fcp={self.fcp:.4g~P}, "
            f"ft={self.ft:.4g~P}, Gt={self.Gt:.4g~P}, Gc={self.Gc:.4g~P}, "
            f"preset='{self.preset_standard}/{self.preset_designation}')"
        )
