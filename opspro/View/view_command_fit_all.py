from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "view_fit_all",
    "description": "Fits the 3D view to show the entire model bounding box. Equivalent to pressing the 'Fit All' button. Use this to reset the view after navigating away or after loading a model.",
    "command": "ViewFitAll",
    "inputSchema": {
        "type": "object",
        "properties": {}
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


class ViewFitAll(AsCommand):

    COMMAND_NAME = 'ViewFitAll'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ok = False
        self._error = ''

    def create(self) -> AsCommand:
        return ViewFitAll()

    def execute(self, initial_options: str = ''):
        try:
            App.cameraFitAll()
            self._ok = True
        except Exception as e:
            self._error = str(e)
        self.emitCommandExiting(AsCommandExitingArgs(
            not self._ok, None,
            json.dumps({'status': self._ok, 'error': self._error})
        ))
