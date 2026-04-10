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
    "name": "delete_material",
    "description": "Deletes a material from the active document by its ID. Requires an active CAE document; returns status=false if no document is open or if the component_id is not found.",
    "command": "DeleteMaterial",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the material to delete"
            }
        },
        "required": ["component_id"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "error": { "type": "string", "description": "Error message if status is false, empty string on success" }
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class MaterialCommandDelete(AsCommand):
    """
    Command for deleting a Material from the document.

    initial_options (JSON)
    ----------------------
    {
      "component_id": <int>   // ID of the material to delete
    }

    The group is always CAEComponentGroupUIDs.MATERIALS.
    Undo/redo is handled by MpcCaeDocumentGeneralUndo wrapping the return args
    from doc.removePluginCaeComponent(), which restores the component on undo
    and removes it again on redo.
    """

    COMMAND_NAME = 'DeleteMaterial'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ret_args = None
        self._error = ''

    def create(self) -> AsCommand:
        return MaterialCommandDelete()

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            print(f'[{self.COMMAND_NAME}] Error: no active CAE document.')
            self.terminate(abort=True)
            return

        try:
            opts = json.loads(initial_options)
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'Invalid input: {e}'
            print(f'[{self.COMMAND_NAME}] Error: failed to parse initial_options ({e}).')
            self.terminate(abort=True)
            return

        try:
            groups = doc.pluginCaeComponents.groups()
            mat = groups[CAEComponentGroupUIDs.MATERIALS].collection[component_id]
        except Exception as e:
            self._error = f'Material with id={component_id} not found: {e}'
            print(f'[{self.COMMAND_NAME}] Error: could not retrieve material id={component_id} ({e}).')
            self.terminate(abort=True)
            return

        self._ret_args = doc.removePluginCaeComponent(mat)
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
