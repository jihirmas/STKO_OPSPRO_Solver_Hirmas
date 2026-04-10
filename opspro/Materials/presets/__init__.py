from opspro.Materials.presets.steel_presets import PRESETS as STEEL_PRESETS, SteelPreset
from opspro.Materials.presets.steel_preset_dialog import SteelPresetDialog
from opspro.Materials.presets.concrete_presets import PRESETS as CONCRETE_PRESETS, ConcretePreset, mc2010_fracture_energy
from opspro.Materials.presets.concrete_preset_dialog import ConcretePresetDialog

# Legacy alias — keeps existing code that imports PRESETS from this package working
PRESETS = STEEL_PRESETS

__all__ = [
    'PRESETS', 'STEEL_PRESETS', 'SteelPreset', 'SteelPresetDialog',
    'CONCRETE_PRESETS', 'ConcretePreset', 'mc2010_fracture_energy', 'ConcretePresetDialog',
]
