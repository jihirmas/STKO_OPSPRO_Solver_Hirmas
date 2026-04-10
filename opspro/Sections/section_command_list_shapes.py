import json

from PyMpc import (
    AsCommand,
    AsCommandExitingArgs,
)

"""
MCP_COMMAND_METADATA_START
{
    "name": "list_section_shapes",
    "description": "Returns the list of all available beam cross-section shape types (preset modules) with their input parameter names, units and descriptions. Use this for discovery: call it once to learn what shapes exist and what parameters each shape accepts. For shapes that have a catalogue (has_presets=true, e.g. 'I Section', 'C Channel'), follow up with list_section_presets to get the named presets and their ready-to-use section_parameters. For parametric shapes (has_presets=false, e.g. 'Rectangular', 'Circular'), supply custom dimensions directly in new_beam_section with preset_name='user'. For the 'Custom' shape, supply section properties directly (area, Iyy, Izz, etc.).",
    "command": "ListSectionShapes",
    "inputSchema": {
        "type": "object",
        "properties": {}
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "shapes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "shape":             { "type": "string",  "description": "Shape name to use as preset_module in new_beam_section" },
                        "has_presets":       { "type": "boolean", "description": "true if a named preset catalogue exists for this shape" },
                        "param_names":       { "type": "array",   "items": { "type": "string" }, "description": "Input parameter keys for this shape" },
                        "param_units":       { "type": "array",   "items": { "type": "string" }, "description": "Default units for each input parameter" },
                        "param_descriptions":{ "type": "array",   "items": { "type": "string" }, "description": "Human-readable description of each parameter" }
                    }
                }
            },
            "error": { "type": "string", "description": "Error message if status is false, empty string on success" }
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class SectionCommandListShapes(AsCommand):
    """
    Headless-only command: returns all available section shape types with
    their parameter metadata. Does not require or modify the CAE document.
    """

    COMMAND_NAME = 'ListSectionShapes'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._output = ''

    def create(self):
        return SectionCommandListShapes()

    def execute(self, initial_options: str = ''):
        try:
            from opspro.Sections.presets import registry as section_registry
            shapes = []
            for shape_name in section_registry.list_section_types():
                mod = section_registry.get_preset_module(shape_name)
                param_names  = getattr(mod, 'PARAM_NAMES', [])
                param_descs  = getattr(mod, 'PARAM_DESCRIPTIONS', [])
                param_units  = getattr(mod, 'PARAM_UNITS', ['mm'] * len(param_names))
                presets      = getattr(mod, 'PRESETS', [])
                shapes.append({
                    'shape':              shape_name,
                    'has_presets':        len(presets) > 0,
                    'param_names':        list(param_names),
                    'param_units':        list(param_units),
                    'param_descriptions': list(param_descs),
                })
            self._finish(True, shapes, '')
        except Exception as e:
            self._finish(False, [], f'Failed to list section shapes: {e}')

    def terminate(self, abort: bool):
        self.emitCommandExiting(AsCommandExitingArgs(abort, None, self._output))

    def _finish(self, status: bool, shapes: list, error: str):
        self._output = json.dumps({'status': status, 'shapes': shapes, 'error': error})
        self.emitCommandExiting(AsCommandExitingArgs(not status, None, self._output))
