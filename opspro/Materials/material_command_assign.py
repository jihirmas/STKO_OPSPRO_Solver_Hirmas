"""
material_command_assign.py
--------------------------
Command for assigning a Material to CAE targets,
with full diff-based undo/redo support.

Command
-------
MaterialCommandAssign (COMMAND_NAME = 'AssignMaterial')
    Assigns the current material to the selected CAE targets, enforcing
    the one-material-per-target constraint: if another material is already
    assigned to a target, it is silently evicted and recorded in the diff
    so that undo can restore it.

Undo/redo relies on MaterialAssignUndo (swap-based) from
opspro.utils.assignment_diff, mirroring the pattern of _MaterialEditUndo.
"""

from __future__ import annotations

import json

from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)

from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.utils import get_assignment_registry
from opspro.utils import collect_targets
from opspro.utils import AssignDiff

"""
MCP_COMMAND_METADATA_START
{
    "name": "assign_material",
    "description": "Assigns a material to one or more CAE targets (geometry sub-shapes or interactions). Enforces the one-material-per-target constraint: any previously assigned material is evicted and recorded for undo. Requires an active CAE document. In headless/API mode, 'targets' must be supplied explicitly since no GUI selection is available.",
    "command": "AssignMaterial",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the material to assign"
            },
            "targets": {
                "type": "array",
                "description": "List of CAE targets to assign the material to. Required in headless/API mode.",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": { "type": "integer", "description": "ID of the geometry or interaction" },
                        "type": { "type": "string", "enum": ["Geometry", "Interaction"], "description": "Target entity type" },
                        "subshape_id": { "type": "integer", "description": "Subshape index for Geometry targets (-1 for whole geometry); ignored for Interaction" },
                        "subshape_type": { "type": "string", "enum": ["Vertex", "Edge", "Face", "Solid"], "description": "Subshape type for Geometry targets; omit for whole geometry or Interaction" }
                    },
                    "required": ["id", "type"]
                }
            }
        },
        "required": ["component_id", "targets"]
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

# ---------------------------------------------------------------------------
# MaterialCommandAssign
# ---------------------------------------------------------------------------

class MaterialCommandAssign(AsCommand):
    """
    Assigns the current Material to the selected CAE targets.

    Enforces the one-material-per-target constraint: any material already
    assigned to a target sub-shape is evicted and recorded in the diff so
    that undo can restore it.

    initial_options (JSON)
    ----------------------
    {
      "component_id": <int>,
      "targets": [
            "id": <int>,
            "type": "Geometry" | "Interaction" | ... others are not supported and will be ignored,
            "subshape_id": <int>, required for Geometry subshapes (-1 for whole geometry), ignored for Interaction
            "subshape_type": "Vertex" | "Edge" | "Face" | "Solid" (None for whole geometry), required for Geometry, ignored for Interaction
        ]   // optional — see _decode_inline_targets()
    }

    Undo/redo
    ---------
    _MaterialAssignUndo stores the per-target diff (prev/new component refs).
    Undo restores prev_comp for every target; redo re-applies new_comp.
    Both are handled by the same swap-based execute() mechanism.
    """

    COMMAND_NAME = 'AssignMaterial'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._undo_cmd = None
        self._error = ''

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        from opspro.Materials import MaterialAssignUndo # here to avoid circular import

        # get document
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            print(f'[{self.COMMAND_NAME}] Error: no active CAE document.')
            self.terminate(abort=True)
            return

        # parse initial options (must be valid JSON with component_id)
        try:
            opts = json.loads(initial_options)
        except Exception as e:
            self._error = f'Invalid JSON input: {e}'
            print(f'[{self.COMMAND_NAME}] Error: bad initial_options ({e}).')
            self.terminate(abort=True)
            return

        # resolve material component
        try:
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'component_id missing or invalid: {e}'
            print(f'[{self.COMMAND_NAME}] Error: component_id missing or invalid in initial_options ({e}).')
            self.terminate(abort=True)
            return
        try:
            mat = (
                doc.pluginCaeComponents
                   .groups()[CAEComponentGroupUIDs.MATERIALS]
                   .collection[component_id]
            )
        except Exception as e:
            self._error = f'Material with id={component_id} not found: {e}'
            print(f'[{self.COMMAND_NAME}] Error: material id={component_id} not found ({e}).')
            self.terminate(abort=True)
            return

        # resolve cae targets (from initial options or current selection)
        targets = collect_targets(doc, opts)
        if targets is None:
            self._error = 'Failed to acquire CAE targets.'
            print(f'[{self.COMMAND_NAME}] Error acquiring targets; aborting.')
            self.terminate(abort=True)
            return

        # resolve registry
        registry = get_assignment_registry()
        if registry is None:
            self._error = 'AssignmentRegistry not found.'
            print(f'[{self.COMMAND_NAME}] Error: AssignmentRegistry not found.')
            self.terminate(abort=True)
            return

        # build diff
        try:
            diff = AssignDiff.makeAssignDiff(doc, registry, mat, targets)
        except Exception as e:
            self._error = f'Failed to build assignment diff: {e}'
            print(f'[{self.COMMAND_NAME}] Error building assignment diff: {e}')
            self.terminate(abort=True)
            return

        if not diff.items:
            self._error = 'No valid targets found in the assignment diff.'
            print(f'[{self.COMMAND_NAME}] No diff targets found; aborting.')
            self.terminate(abort=True)
            return

        # apply forward diff and set up undo
        diff.apply(invert=False)

        # invert=True → undo will restore prev_comp for each target
        self._undo_cmd = MaterialAssignUndo(
            self.COMMAND_NAME, diff.to_json(), invert=True
        )
        self.terminate(abort=False)

    def terminate(self, abort: bool):
        output = json.dumps({'status': not abort, 'error': self._error if abort else ''})
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            self.emitCommandExiting(AsCommandExitingArgs(False, self._undo_cmd, output))

    def create(self) -> 'MaterialCommandAssign':
        return MaterialCommandAssign()
