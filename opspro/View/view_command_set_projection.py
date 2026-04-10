from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "view_set_projection",
    "description": "Switches the 3D view between Perspective and Orthographic projection.",
    "command": "ViewSetProjection",
    "inputSchema": {
        "type": "object",
        "properties": {
            "projection": {
                "type": "string",
                "description": "Projection type to set. One of: 'Perspective', 'Orthographic'",
                "enum": ["Perspective", "Orthographic"]
            }
        },
        "required": ["projection"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "error":  { "type": "string",  "description": "Error message if status is false, empty string on success" }
        }
    }
}
MCP_COMMAND_METADATA_END
"""

_VALID_PROJECTIONS = {"Perspective", "Orthographic"}


class ViewSetProjection(AsCommand):

    COMMAND_NAME = 'ViewSetProjection'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ok = False
        self._error = ''

    def create(self) -> AsCommand:
        return ViewSetProjection()

    def execute(self, initial_options: str = ''):
        try:
            opts = json.loads(initial_options)
            proj = str(opts.get('projection', ''))
            if proj not in _VALID_PROJECTIONS:
                raise ValueError(
                    f"Invalid projection '{proj}'. Must be one of: {sorted(_VALID_PROJECTIONS)}"
                )
            App.cameraSetProjection(proj)
            self._ok = True
        except Exception as e:
            self._error = str(e)
        self.emitCommandExiting(AsCommandExitingArgs(
            not self._ok, None,
            json.dumps({'status': self._ok, 'error': self._error})
        ))
