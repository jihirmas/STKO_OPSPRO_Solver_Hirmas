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
    "name": "clone_material",
    "description": "Clones an existing material in the active document, creating a new independent copy with a new ID. Requires an active CAE document; returns status=false if no document is open or if the source component_id is not found.",
    "command": "CloneMaterial",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the material to clone"
            },
            "component_name": {
                "type": "string",
                "description": "Optional name for the cloned material. Defaults to '<source name>-Clone'"
            }
        },
        "required": ["component_id"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "component_id": { "type": "integer", "description": "ID of the newly created clone (or -1 on failure)" },
            "error": { "type": "string", "description": "Error message if status is false, empty string on success" }
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class MaterialCommandClone(AsCommand):
    """
    Command for cloning an existing Material.

    Copies the full state of the source material into a brand-new component
    (new ID, optionally a new name), then adds it to the document.

    initial_options (JSON)
    ----------------------
    {
      "component_id":   <int>,     // required — ID of the material to clone
      "component_name": <string>   // optional — name for the clone;
                                   //   defaults to "<source name>-Clone"
    }

    Undo/redo is handled by MpcCaeDocumentGeneralUndo wrapping the return args
    from doc.addPluginCaeComponent(), mirroring MaterialCommandNew.
    """

    COMMAND_NAME = 'CloneMaterial'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ret_args = None
        self._new_id = -1
        self._error = ''

    def create(self) -> AsCommand:
        return MaterialCommandClone()

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
            src_mat = groups[CAEComponentGroupUIDs.MATERIALS].collection[component_id]
        except Exception as e:
            self._error = f'Material with id={component_id} not found: {e}'
            print(f'[{self.COMMAND_NAME}] Error: could not retrieve material id={component_id} ({e}).')
            self.terminate(abort=True)
            return

        # Determine the name for the clone
        component_name = opts.get('component_name', '').strip()
        if not component_name:
            component_name = f'{src_mat.name}-Clone'

        # Snapshot the source, then build a same-type clone with a new ID
        snapshot = src_mat.save()
        new_id = self._next_material_id(doc)
        clone = type(src_mat)(id=new_id, name=component_name)
        clone.restore(snapshot)
        # Override id/name; restore() copies them from the snapshot
        clone.id   = new_id
        clone.name = component_name
        clone.changed = True

        self._new_id = new_id
        self._ret_args = doc.addPluginCaeComponent(clone)
        doc.commitChanges()
        doc.dirty = True

        self.terminate(abort=False)

    def terminate(self, abort: bool):
        output = json.dumps({
            'status': not abort,
            'component_id': self._new_id,
            'error': self._error if abort else ''
        })
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            undo_cmd = MpcCaeDocumentGeneralUndo(self.COMMAND_NAME, self._ret_args)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _next_material_id(doc) -> int:
        """Return max(existing material IDs) + 1, or 1 if the group is empty."""
        try:
            groups = doc.pluginCaeComponents.groups()
            group_id = CAEComponentGroupUIDs.MATERIALS
            if group_id not in groups:
                return 1
            coll = groups[group_id].collection
            return coll.getlastkey(0) + 1
        except Exception as e:
            print(f'[MaterialCommandClone] Warning: could not compute next ID ({e}); defaulting to 1.')
            return 1
