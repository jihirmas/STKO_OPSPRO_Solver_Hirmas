import dataclasses
import json

from PyMpc import (
    AsCommand,
    AsCommandExitingArgs,
)

"""
MCP_COMMAND_METADATA_START
{
    "name": "list_material_presets",
    "description": "Returns the full database of available material presets for a given material type. Call this BEFORE creating a material from a named standard/grade (e.g. 'EN 1992 C30/37', 'ASTM A572-50', 'CSA G40.21 350W', 'CSA A23.3 f\\'c 30 MPa'): read the matching entry\\'s material_parameters, then pass those values directly to new_steel_material or new_concrete_material. Each preset includes a ready-to-use material_parameters object with all physical quantities. Use the 'standard' filter to reduce output when you already know the target standard (case-sensitive exact match). Available standard keys — steel (124 grades): 'ASTM', 'API', 'AISI', 'ASME', 'EN', 'JIS', 'GB', 'AS/NZS', 'IS', 'CSA', 'UNI'. Available standard keys — concrete (49 grades): 'EN 1992', 'ACI 318', 'GB 50010', 'CSA A23.3'.",
    "command": "ListMaterialPresets",
    "inputSchema": {
        "type": "object",
        "properties": {
            "material_type": {
                "type": "string",
                "enum": ["steel", "concrete", "soil"],
                "description": "Type of material presets to list. Note: soil has no standardised presets and returns an empty result."
            },
            "standard": {
                "type": "string",
                "description": "Optional: filter results to a single standard using the exact case-sensitive key. Steel keys: 'ASTM', 'API', 'AISI', 'ASME', 'EN', 'JIS', 'GB', 'AS/NZS', 'IS', 'CSA', 'UNI'. Concrete keys: 'EN 1992', 'ACI 318', 'GB 50010', 'CSA A23.3'. If omitted, all standards are returned."
            }
        },
        "required": ["material_type"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "presets": {
                "type": "object",
                "description": "Dictionary keyed by standard name. Each value is an array of preset entries.",
                "additionalProperties": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "designation":         { "type": "string" },
                            "name":                { "type": "string" },
                            "notes":               { "type": "string" },
                            "material_parameters": { "type": "object", "description": "Ready-to-use object for new_steel_material or new_concrete_material" }
                        }
                    }
                }
            },
            "error": { "type": "string", "description": "Error message if status is false, empty string on success" }
        }
    }
}
MCP_COMMAND_METADATA_END
"""


def _qty(magnitude, unit):
    return {'magnitude': magnitude, 'unit': unit}


def _steel_preset_to_entry(p) -> dict:
    d = dataclasses.asdict(p)
    return {
        'designation': d['designation'],
        'name':        d['name'],
        'notes':       d.get('notes', ''),
        'material_parameters': {
            'E':                  _qty(d['E']       / 1e9,  'GPa'),
            'nu':                 _qty(d['nu'],             'dimensionless'),
            'rho':                _qty(d['rho'],            'kg/m^3'),
            'sigma_y':            _qty(d['sigma_y'] / 1e6,  'MPa'),
            'sigma_u':            _qty(d['sigma_u'] / 1e6,  'MPa'),
            'epsilon_u':          _qty(d['epsilon_u'],      'dimensionless'),
            'preset_standard':    d['standard'],
            'preset_designation': d['designation'],
        },
    }


def _concrete_preset_to_entry(p) -> dict:
    d = dataclasses.asdict(p)
    return {
        'designation': d['designation'],
        'name':        d['name'],
        'notes':       d.get('notes', ''),
        'material_parameters': {
            'E':                  _qty(d['E']   / 1e9,  'GPa'),
            'nu':                 _qty(d['nu'],         'dimensionless'),
            'rho':                _qty(d['rho'],        'kg/m^3'),
            'fcp':                _qty(d['fcp'] / 1e6,  'MPa'),
            'ft':                 _qty(d['ft']  / 1e6,  'MPa'),
            'Gt':                 _qty(d['Gt'],         'J/m^2'),
            'Gc':                 _qty(d['Gc'],         'J/m^2'),
            'auto_fracture_energy': False,
            'preset_standard':    d['standard'],
            'preset_designation': d['designation'],
        },
    }


class MaterialCommandListPresets(AsCommand):
    """
    Headless-only command: returns the preset database for steel or concrete
    as a JSON output. Does not require or modify the CAE document.
    """

    COMMAND_NAME = 'ListMaterialPresets'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._output = ''

    def create(self):
        return MaterialCommandListPresets()

    def execute(self, initial_options: str = ''):
        try:
            opts = json.loads(initial_options) if initial_options else {}
        except Exception as e:
            self._finish(False, {}, f'Invalid JSON input: {e}')
            return

        material_type = opts.get('material_type', '').strip().lower()
        if material_type not in ('steel', 'concrete', 'soil'):
            self._finish(False, {}, "material_type must be 'steel', 'concrete', or 'soil'.")
            return

        std_filter = opts.get('standard', '').strip()

        try:
            if material_type == 'steel':
                from opspro.Materials.presets.steel_presets import PRESETS
                result = {}
                for std, entries in PRESETS.items():
                    if std_filter and std != std_filter:
                        continue
                    result[std] = [_steel_preset_to_entry(p) for p in entries]
            elif material_type == 'concrete':
                from opspro.Materials.presets.concrete_presets import PRESETS
                result = {}
                for std, entries in PRESETS.items():
                    if std_filter and std != std_filter:
                        continue
                    result[std] = [_concrete_preset_to_entry(p) for p in entries]
            else:  # soil — no standardised presets
                result = {}
        except Exception as e:
            self._finish(False, {}, f'Failed to load presets: {e}')
            return

        if std_filter and not result:
            self._finish(False, {}, f"Standard '{std_filter}' not found for material_type='{material_type}'.")
            return

        self._finish(True, result, '')

    def terminate(self, abort: bool):
        self.emitCommandExiting(AsCommandExitingArgs(abort, None, self._output))

    # ------------------------------------------------------------------

    def _finish(self, status: bool, presets: dict, error: str):
        self._output = json.dumps({'status': status, 'presets': presets, 'error': error})
        self.emitCommandExiting(AsCommandExitingArgs(not status, None, self._output))
