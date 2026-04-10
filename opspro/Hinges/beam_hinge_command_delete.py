"""
beam_hinge_command_delete.py
----------------------------
Command for deleting any BeamHinge subtype.
"""

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
    "name": "delete_beam_hinge",
    "description": "Deletes a beam hinge component (BeamEndRelease, BeamRotationalHinge, or BeamShearHinge) from the active document. Any element assignments referencing this hinge are also removed. Requires an active CAE document.",
    "command": "DeleteBeamHinge",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the hinge component to delete"
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


class BeamHingeCommandDelete(AsCommand):
    """Command for deleting any BeamHinge subtype."""

    COMMAND_NAME = 'DeleteBeamHinge'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ret_args = None
        self._headless = False
        self._error = ''

    def create(self):
        return BeamHingeCommandDelete()

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        self._headless = bool(initial_options)
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            self.terminate(abort=True)
            return

        try:
            opts = json.loads(initial_options)
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'Invalid input: {e}'
            self.terminate(abort=True)
            return

        try:
            groups = doc.pluginCaeComponents.groups()
            comp = groups[CAEComponentGroupUIDs.BEAM_HINGES].collection[component_id]
        except Exception as e:
            self._error = f'Hinge component with id={component_id} not found: {e}'
            self.terminate(abort=True)
            return

        snapshot = comp.save()
        comp_type = type(comp)
        comp_id   = int(comp.id)

        self._ret_args = doc.removePluginCaeComponent(comp)
        doc.commitChanges()
        doc.dirty = True

        self.terminate(abort=False)

    def terminate(self, abort: bool):
        output = ''
        if self._headless:
            output = json.dumps({'status': not abort, 'error': self._error if abort else ''})
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            undo_cmd = MpcCaeDocumentGeneralUndo(self.COMMAND_NAME, self._ret_args)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))
