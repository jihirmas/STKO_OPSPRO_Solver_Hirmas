from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "view_get_camera_state",
    "description": "Returns the current state of the 3D view camera: eye position, target point, up vector, field-of-view, distance, near/far planes, and projection type. Useful to understand the current viewpoint before issuing rotation or zoom commands.",
    "command": "ViewGetCameraState",
    "inputSchema": {
        "type": "object",
        "properties": {}
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "error":  { "type": "string",  "description": "Error message if status is false, empty string on success" },
            "eye":        { "type": "array",  "items": { "type": "number" }, "description": "Eye (camera) position [x, y, z] in world space" },
            "target":     { "type": "array",  "items": { "type": "number" }, "description": "Look-at target point [x, y, z] in world space" },
            "up":         { "type": "array",  "items": { "type": "number" }, "description": "Camera up vector [x, y, z]" },
            "fovy":       { "type": "number", "description": "Field of view (vertical) in degrees (perspective only)" },
            "distance":   { "type": "number", "description": "Distance from eye to target" },
            "near_plane": { "type": "number", "description": "Near clipping plane distance" },
            "far_plane":  { "type": "number", "description": "Far clipping plane distance" },
            "projection": { "type": "string", "description": "Projection type: 'Perspective' or 'Orthographic'" }
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class ViewGetCameraState(AsCommand):

    COMMAND_NAME = 'ViewGetCameraState'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ok = False
        self._error = ''
        self._state = {}

    def create(self) -> AsCommand:
        return ViewGetCameraState()

    def execute(self, initial_options: str = ''):
        try:
            s = App.cameraGetState()
            if not s:
                self._error = 'No active 3D view found.'
            else:
                self._ok = True
                self._state = dict(s)
        except Exception as e:
            self._error = str(e)
        self.emitCommandExiting(AsCommandExitingArgs(
            not self._ok, None,
            json.dumps({'status': self._ok, 'error': self._error, **self._state})
        ))
