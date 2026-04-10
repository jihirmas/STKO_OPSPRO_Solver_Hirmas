"""
material_command_unassign.py
----------------------------
Command for unassigning a Material from CAE targets,
with full diff-based undo/redo support.

Command
-------
MaterialCommandUnassign (COMMAND_NAME = 'UnassignMaterial')
    Unassigns the current material from the selected CAE targets.
    Only targets where *this* material is actually assigned are affected;
    others are silently ignored.

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
    "name": "unassign_material",
    "description": "Unassigns a material from one or more CAE targets. Only targets where this specific material is currently assigned are affected; others are silently skipped. Requires an active CAE document. In headless/API mode, 'targets' must be supplied explicitly since no GUI selection is available.",
    "command": "UnassignMaterial",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the material to unassign"
            },
            "targets": {
                "type": "array",
                "description": "List of CAE targets to unassign the material from. Required in headless/API mode.",
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
# MaterialCommandUnassign
# ---------------------------------------------------------------------------

class MaterialCommandUnassign(AsCommand):
    """
    Unassigns the current Material from the selected CAE targets.

    Only targets where *this* material is actually assigned are processed;
    targets assigned to another material (or unassigned) are silently skipped.

    initial_options (JSON)
    ----------------------
    {
      "component_id": <int>,
      "targets": [...]   // optional — see decode_inline_targets()
    }

    Undo/redo
    ---------
    MaterialAssignUndo stores the per-target diff (prev/new component refs).
    Undo re-assigns the material; redo unassigns it again.
    Both are handled by the same swap-based execute() mechanism.
    """

    COMMAND_NAME = 'UnassignMaterial'

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

        # build diff — only targets where this material is currently assigned
        try:
            diff = AssignDiff.makeUnassignDiff(doc, registry, mat, targets)
        except Exception as e:
            self._error = f'Failed to build unassignment diff: {e}'
            print(f'[{self.COMMAND_NAME}] Error building unassignment diff: {e}')
            self.terminate(abort=True)
            return

        if not diff.items:
            self._error = 'Material is not assigned to any of the selected targets.'
            print(f'[{self.COMMAND_NAME}] Material not assigned to any selected target; aborting.')
            self.terminate(abort=True)
            return

        diff.apply(invert=False)
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

    def create(self) -> 'MaterialCommandUnassign':
        return MaterialCommandUnassign()
