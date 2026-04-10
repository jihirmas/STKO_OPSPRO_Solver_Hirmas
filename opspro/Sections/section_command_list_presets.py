import json

from PyMpc import (
    AsCommand,
    AsCommandExitingArgs,
)

"""
MCP_COMMAND_METADATA_START
{
    "name": "list_section_presets",
    "description": "Returns the named preset catalogue for a given beam cross-section shape. Each entry includes a ready-to-use section_parameters object for new_beam_section. Call list_section_shapes first to discover available shapes and whether they have a catalogue. Shapes with has_presets=false (e.g. 'Rectangular', 'Circular') return an empty presets array — for those, use preset_name='user' in new_beam_section and supply your own dimensions. Available shapes with catalogues: 'I Section' (IPE, HEA, HEB, HEM, W, S, HP, ...), 'I HP Section', 'I S Section', 'C Channel', 'C MC Channel', 'T Section', 'L Angle', 'L U Angle'.",
    "command": "ListSectionPresets",
    "inputSchema": {
        "type": "object",
        "properties": {
            "shape": {
                "type": "string",
                "description": "Section shape name (preset_module) as returned by list_section_shapes, e.g. 'I Section', 'C Channel', 'L Angle'."
            }
        },
        "required": ["shape"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "shape":  { "type": "string",  "description": "Echo of the requested shape" },
            "param_names":        { "type": "array", "items": { "type": "string" }, "description": "Input parameter keys for this shape" },
            "param_units":        { "type": "array", "items": { "type": "string" }, "description": "Default units for each input parameter" },
            "param_descriptions": { "type": "array", "items": { "type": "string" }, "description": "Human-readable description of each parameter" },
            "presets": {
                "type": "array",
                "description": "List of named presets. Empty for parametric-only shapes.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name":               { "type": "string", "description": "Preset designation to use as preset_name in new_beam_section" },
                        "section_parameters": { "type": "object", "description": "Ready-to-use parameters for new_beam_section (magnitude+unit format)" }
                    }
                }
            },
            "error": { "type": "string", "description": "Error message if status is false, empty string on success" }
        }
    }
}
MCP_COMMAND_METADATA_END
"""


def _preset_to_entry(preset, param_names: list, param_units: list) -> dict:
    """Convert a preset dataclass instance to a dict with section_parameters."""
    section_parameters = {}
    for pname, punit in zip(param_names, param_units):
        val = getattr(preset, pname, None)
        if val is None:
            continue
        if hasattr(val, 'magnitude'):
            # pint.Quantity — use its own units for accuracy
            section_parameters[pname] = {
                'magnitude': float(val.magnitude),
                'unit': str(val.units),
            }
        else:
            section_parameters[pname] = {
                'magnitude': float(val),
                'unit': punit,
            }
    return {
        'name': getattr(preset, 'name', str(preset)),
        'section_parameters': section_parameters,
    }


class SectionCommandListPresets(AsCommand):
    """
    Headless-only command: returns the named preset catalogue for a given
    section shape. Does not require or modify the CAE document.
    """

    COMMAND_NAME = 'ListSectionPresets'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._output = ''

    def create(self):
        return SectionCommandListPresets()

    def execute(self, initial_options: str = ''):
        try:
            opts = json.loads(initial_options) if initial_options else {}
        except Exception as e:
            self._finish(False, '', [], [], [], [], f'Invalid JSON input: {e}')
            return

        shape = opts.get('shape', '').strip()
        if not shape:
            self._finish(False, '', [], [], [], [], "'shape' is required.")
            return

        try:
            from opspro.Sections.presets import registry as section_registry
            mod = section_registry.get_preset_module(shape)
            if mod is None:
                known = section_registry.list_section_types()
                self._finish(False, shape, [], [], [], [],
                             f"Unknown shape '{shape}'. Available: {known}")
                return

            param_names  = getattr(mod, 'PARAM_NAMES', [])
            param_descs  = getattr(mod, 'PARAM_DESCRIPTIONS', [])
            param_units  = getattr(mod, 'PARAM_UNITS', ['mm'] * len(param_names))
            raw_presets  = getattr(mod, 'PRESETS', [])

            presets = [_preset_to_entry(p, param_names, param_units) for p in raw_presets]
            self._finish(True, shape, list(param_names), list(param_units),
                         list(param_descs), presets, '')
        except Exception as e:
            self._finish(False, shape, [], [], [], [], f'Failed to list presets: {e}')

    def terminate(self, abort: bool):
        self.emitCommandExiting(AsCommandExitingArgs(abort, None, self._output))

    def _finish(self, status: bool, shape: str, param_names: list,
                param_units: list, param_descriptions: list,
                presets: list, error: str):
        self._output = json.dumps({
            'status':             status,
            'shape':              shape,
            'param_names':        param_names,
            'param_units':        param_units,
            'param_descriptions': param_descriptions,
            'presets':            presets,
            'error':              error,
        })
        self.emitCommandExiting(AsCommandExitingArgs(not status, None, self._output))
