from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "view_set_view_point",
    "description": "Snaps the 3D camera to one of the standard orthographic viewpoints or to a default 3D perspective view. Use this to orient the view before grabbing a screenshot.",
    "command": "ViewSetViewPoint",
    "inputSchema": {
        "type": "object",
        "properties": {
            "view_point": {
                "type": "string",
                "description": "Target viewpoint. One of: 'top', 'bottom', 'front', 'back', 'left', 'right', '3d'",
                "enum": ["top", "bottom", "front", "back", "left", "right", "3d"]
            }
        },
        "required": ["view_point"]
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

_VALID_VIEW_POINTS = {"top", "bottom", "front", "back", "left", "right", "3d"}


class ViewSetViewPoint(AsCommand):

    COMMAND_NAME = 'ViewSetViewPoint'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ok = False
        self._error = ''

    def create(self) -> AsCommand:
        return ViewSetViewPoint()

    def execute(self, initial_options: str = ''):
        try:
            opts = json.loads(initial_options)
            vp = str(opts.get('view_point', '')).lower()
            if vp not in _VALID_VIEW_POINTS:
                raise ValueError(
                    f"Invalid view_point '{vp}'. Must be one of: {sorted(_VALID_VIEW_POINTS)}"
                )
            App.cameraSetViewPoint(vp)
            self._ok = True
        except Exception as e:
            self._error = str(e)
        self.emitCommandExiting(AsCommandExitingArgs(
            not self._ok, None,
            json.dumps({'status': self._ok, 'error': self._error})
        ))
