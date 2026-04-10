"""
beam_hinge_command_clone.py
---------------------------
Command for cloning any BeamHinge subtype (BeamEndRelease,
BeamRotationalHinge, BeamShearHinge).
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
    "name": "clone_beam_hinge",
    "description": "Clones an existing beam hinge component (BeamEndRelease, BeamRotationalHinge, or BeamShearHinge) in the active document, creating a new independent copy with a new ID. Requires an active CAE document.",
    "command": "CloneBeamHinge",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the hinge component to clone"
            },
            "component_name": {
                "type": "string",
                "description": "Optional name for the clone. Defaults to '<source name>-Clone'."
            }
        },
        "required": ["component_id"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status":       {"type": "boolean", "description": "true on success, false on failure"},
            "component_id": {"type": "integer", "description": "ID of the newly created clone (-1 on failure)"},
            "error":        {"type": "string",  "description": "Error message if status is false, empty string on success"}
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class BeamHingeCommandClone(AsCommand):
    """Command for cloning any BeamHinge subtype."""

    COMMAND_NAME = 'CloneBeamHinge'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ret_args = None
        self._new_id   = -1
        self._error    = ''

    def create(self):
        return BeamHingeCommandClone()

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
            src = groups[CAEComponentGroupUIDs.BEAM_HINGES].collection[component_id]
        except Exception as e:
            self._error = f'Hinge component with id={component_id} not found: {e}'
            print(f'[{self.COMMAND_NAME}] Error: could not retrieve id={component_id} ({e}).')
            self.terminate(abort=True)
            return

        component_name = opts.get('component_name', '').strip()
        if not component_name:
            component_name = f'{src.name}-Clone'

        snapshot = src.save()
        new_id = self._next_hinge_id(doc)
        clone = type(src)(id=new_id, name=component_name)
        clone.restore(snapshot)
        # restore() copies id/name from the snapshot — override them
        clone.id   = new_id
        clone.name = component_name
        clone.changed = True

        self._new_id   = new_id
        self._ret_args = doc.addPluginCaeComponent(clone)
        doc.commitChanges()
        doc.dirty = True

        self.terminate(abort=False)

    def terminate(self, abort: bool):
        output = json.dumps({
            'status':       not abort,
            'component_id': self._new_id,
            'error':        self._error if abort else '',
        })
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            undo_cmd = MpcCaeDocumentGeneralUndo(self.COMMAND_NAME, self._ret_args)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))

    @staticmethod
    def _next_hinge_id(doc) -> int:
        """Return max(existing BEAM_HINGES component IDs) + 1, or 1 if empty."""
        try:
            groups    = doc.pluginCaeComponents.groups()
            group_id  = CAEComponentGroupUIDs.BEAM_HINGES
            if group_id not in groups:
                return 1
            coll = groups[group_id].collection
            return coll.getlastkey(0) + 1
        except Exception as e:
            print(f'[BeamHingeCommandClone] Warning: could not compute next ID ({e}); defaulting to 1.')
            return 1
