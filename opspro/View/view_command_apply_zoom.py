from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "view_apply_zoom",
    "description": "Adjusts the camera zoom by moving the eye position along the view axis toward or away from the target. Positive values move the eye away from the target (zoom out); negative values move it toward the target (zoom in).",
    "command": "ViewApplyZoom",
    "inputSchema": {
        "type": "object",
        "properties": {
            "distance_increment": {
                "type": "number",
                "description": "Amount to add to the current eye-to-target distance. Positive = zoom out, negative = zoom in. The unit matches the model's coordinate system units."
            }
        },
        "required": ["distance_increment"]
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


class ViewApplyZoom(AsCommand):

    COMMAND_NAME = 'ViewApplyZoom'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ok = False
        self._error = ''

    def create(self) -> AsCommand:
        return ViewApplyZoom()

    def execute(self, initial_options: str = ''):
        try:
            opts = json.loads(initial_options)
            increment = float(opts['distance_increment'])
            App.cameraApplyZoom(increment)
            self._ok = True
        except Exception as e:
            self._error = str(e)
        self.emitCommandExiting(AsCommandExitingArgs(
            not self._ok, None,
            json.dumps({'status': self._ok, 'error': self._error})
        ))
