from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "view_grab_screenshot",
    "description": "Captures the current 3D viewport and saves it to a file. The output format is inferred from the file extension. Supported extensions: .png, .jpg, .bmp, .ppm. Use this command to let the agent visually inspect the model, verify rendering results, or produce images for reports.",
    "command": "ViewGrabScreenShot",
    "inputSchema": {
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "Absolute file path where the screenshot will be saved, including the file name and extension (e.g. C:/tmp/view.png)."
            }
        },
        "required": ["filepath"]
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


class ViewGrabScreenShot(AsCommand):

    COMMAND_NAME = 'ViewGrabScreenShot'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ok = False
        self._error = ''

    def create(self) -> AsCommand:
        return ViewGrabScreenShot()

    def execute(self, initial_options: str = ''):
        try:
            opts = json.loads(initial_options)
            filepath = str(opts['filepath'])
            App.cameraGrabScreenShot(filepath)
            self._ok = True
        except Exception as e:
            self._error = str(e)
        self.emitCommandExiting(AsCommandExitingArgs(
            not self._ok, None,
            json.dumps({'status': self._ok, 'error': self._error})
        ))
