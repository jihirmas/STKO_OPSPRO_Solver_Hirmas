from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    MpcCaeDocumentGeneralUndo,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "delete_user_note",
    "description": "Deletes a user note from the active document by its ID. Requires an active CAE document.",
    "command": "DeleteUserNote",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the note to delete"
            }
        },
        "required": ["component_id"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": {"type": "boolean", "description": "true on success, false on failure"},
            "error":  {"type": "string",  "description": "Error message if status is false, empty string on success"}
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class UserNoteCommandDelete(AsCommand):
    """Command for deleting a UserNote from the document."""

    COMMAND_NAME = 'DeleteUserNote'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ret_args = None
        self._error    = ''

    def create(self):
        return UserNoteCommandDelete()

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            self.terminate(abort=True)
            return

        try:
            opts         = json.loads(initial_options)
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'Invalid input: {e}'
            self.terminate(abort=True)
            return

        try:
            groups = doc.pluginCaeComponents.groups()
            note   = groups[CAEComponentGroupUIDs.USER_NOTES].collection[component_id]
        except Exception as e:
            self._error = f'Note with id={component_id} not found: {e}'
            self.terminate(abort=True)
            return

        self._ret_args = doc.removePluginCaeComponent(note)
        doc.commitChanges()
        doc.dirty = True
        self.terminate(abort=False)

    def terminate(self, abort: bool):
        output = json.dumps({'status': not abort, 'error': self._error if abort else ''})
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            undo_cmd = MpcCaeDocumentGeneralUndo(self.COMMAND_NAME, self._ret_args)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))
