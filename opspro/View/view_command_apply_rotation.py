from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "view_apply_rotation",
    "description": "Rotates the 3D camera around the current target point by a given angle about an arbitrary world-space axis. The target point stays fixed; only the eye orientation changes. Useful for inspecting a model from a custom direction without snapping to a preset viewpoint.",
    "command": "ViewApplyRotation",
    "inputSchema": {
        "type": "object",
        "properties": {
            "axis": {
                "type": "array",
                "items": { "type": "number" },
                "minItems": 3,
                "maxItems": 3,
                "description": "World-space rotation axis [x, y, z]. Does not need to be unit-length."
            },
            "angle_deg": {
                "type": "number",
                "description": "Rotation angle in degrees. Positive is counter-clockwise when looking from the axis tip toward the origin."
            }
        },
        "required": ["axis", "angle_deg"]
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


class ViewApplyRotation(AsCommand):

    COMMAND_NAME = 'ViewApplyRotation'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ok = False
        self._error = ''

    def create(self) -> AsCommand:
        return ViewApplyRotation()

    def execute(self, initial_options: str = ''):
        try:
            opts = json.loads(initial_options)
            axis = list(opts['axis'])
            if len(axis) != 3:
                raise ValueError("'axis' must have exactly 3 components.")
            angle_deg = float(opts['angle_deg'])
            App.cameraApplyRotation(float(axis[0]), float(axis[1]), float(axis[2]), angle_deg)
            self._ok = True
        except Exception as e:
            self._error = str(e)
        self.emitCommandExiting(AsCommandExitingArgs(
            not self._ok, None,
            json.dumps({'status': self._ok, 'error': self._error})
        ))
