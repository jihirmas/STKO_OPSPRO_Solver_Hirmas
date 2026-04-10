from PyMpc import MpcPluginCaeComponent
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.Sections.presets.section_properties import SectionProperties
from opspro.Sections.presets import registry as section_registry
from opspro.parameters.ParameterManager import ParameterManager
from opspro.utils.fx_material_utils import fx_material_to_dict, fx_material_from_dict
import pint
import json


class BeamSection(MpcPluginCaeComponent):
    """
    Generic class for all beam section components (steel, RC, etc).
    Stores geometric parameters and provides section property calculation.
    """
    def __init__(self, id=1, name='BeamSection'):
        super().__init__(id, name)
        self.preset_module: str = None  # e.g. 'I Section', 'C Channel', ...
        self.preset_name: str = None    # e.g. 'C 3x6', 'user', ...
        self.parameters: dict = {}      # dict of pint.Quantity (h, b, tw, tf, ...)
        self.visual_material = None

    def componentGroupID(self):
        return CAEComponentGroupUIDs.SECTIONS

    def className(self):
        return 'BeamSection'

    def description(self):
        return 'Beam cross-section with geometric properties'

    @classmethod
    def dialog_class(cls):
        from opspro.Sections.beam_section_dialog import BeamSectionDialog
        return BeamSectionDialog

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def save(self):
        """Serialize plugin state to a JSON string."""
        try:
            return json.dumps(self._to_dict())
        except Exception as e:
            print(f"Error serializing BeamSection {self.name}: {e}")
            import traceback
            print(traceback.format_exc())
            return ''

    def restore(self, state):
        """Restore plugin state from a JSON string produced by `save()`."""
        if not state:
            return
        try:
            data = json.loads(state)
        except Exception as e:
            print(f"Error parsing state for BeamSection {self.name}: {e}")
            return
        try:
            self._from_dict(data)
        except Exception as e:
            print(f"Error restoring BeamSection {self.name} from state: {e}")

    def _to_dict(self):
        return {
            'ID': int(self.id),
            'name': self.name,
            'changed': self.changed,
            'preset_module': self.preset_module,
            'preset_name': self.preset_name,
            'parameters': {k: self._qty_to_dict(v) for k, v in self.parameters.items()},
            'visual_material': fx_material_to_dict(self.visual_material) if self.visual_material is not None else None,
        }

    def _from_dict(self, data):
        self.id = data.get('ID', self.id)
        self.name = data.get('name', self.name)
        self.changed = data.get('changed', self.changed)
        self.preset_module = data.get('preset_module', self.preset_module)
        self.preset_name = data.get('preset_name', self.preset_name)
        saved_params = data.get('parameters', {})
        self.parameters = {k: self._qty_from_dict(v) for k, v in saved_params.items()}
        _vm = data.get('visual_material')
        self.visual_material = fx_material_from_dict(_vm) if _vm is not None else None

    @staticmethod
    def _qty_to_dict(qty) -> dict:
        if isinstance(qty, pint.Quantity):
            return {'magnitude': float(qty.magnitude), 'unit': str(qty.units)}
        return {'magnitude': float(qty), 'unit': 'dimensionless'}

    @staticmethod
    def _qty_from_dict(data):
        ureg = ParameterManager._unit_registry
        if isinstance(data, dict):
            return ureg.Quantity(data['magnitude'], data['unit'])
        elif isinstance(data, (int, float)):
            return float(data) * ureg.dimensionless
        return 0.0 * ureg.dimensionless

    # ------------------------------------------------------------------
    # Preset selection
    # ------------------------------------------------------------------

    def set_preset(self, preset_module: str, preset_name: str):
        """Set the section type and preset, updating parameters accordingly.

        - If preset_name is a named preset (e.g. 'IPE 200'): parameters are
          copied from the preset (read-only in the editor).
        - If preset_name is 'user': parameters are initialized from CUSTOM
          defaults (editable in the editor).
        - If only preset_module changes but preset_name is 'user': parameters
          are re-initialized from the new module's CUSTOM defaults.
        """
        self.preset_module = preset_module
        self.preset_name = preset_name
        if preset_name == 'user':
            custom = section_registry.get_custom(preset_module)
            if custom is not None:
                d = custom.__dict__.copy()
                d.pop('name', None)
                self.parameters = d
            else:
                self.parameters = {}
        else:
            preset = section_registry.get_preset(preset_module, preset_name)
            if preset is not None:
                d = preset.__dict__.copy()
                d.pop('name', None)
                self.parameters = d
            else:
                self.parameters = {}

    # ------------------------------------------------------------------
    # Calculation
    # ------------------------------------------------------------------

    def calculate_properties(self) -> SectionProperties:
        """
        Calculate section properties using the current preset_module, preset_name, and parameters.
        If preset_name is not 'user', uses the preset values; otherwise uses self.parameters.
        """
        if not self.preset_module:
            raise ValueError("preset_module must be set (e.g. 'C', 'C_MC')")
        if not self.preset_name:
            raise ValueError("preset_name must be set (e.g. 'C 3x6', 'user')")

        calc_fn = section_registry.get_calculate_function(self.preset_module)
        if calc_fn is None:
            raise ValueError(f"No preset module found for section type '{self.preset_module}'")

        if self.preset_name != 'user':
            preset = section_registry.get_preset(self.preset_module, self.preset_name)
            if preset is None:
                raise ValueError(f"Preset '{self.preset_name}' not found for section type '{self.preset_module}'")
            param_dict = preset.__dict__.copy()
        else:
            param_dict = self.parameters.copy()
        return calc_fn(param_dict)

    def __repr__(self):
        return (
            f"BeamSection(id={int(self.id)}, name={self.name}, "
            f"preset_module={self.preset_module}, preset={self.preset_name})"
        )
