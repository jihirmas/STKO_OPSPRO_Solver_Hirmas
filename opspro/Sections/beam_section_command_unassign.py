"""
beam_section_command_unassign.py
--------------------------------
Command for unassigning a BeamSection from CAE targets,
with full diff-based undo/redo support.

Command
-------
BeamSectionCommandUnassign (COMMAND_NAME = 'UnassignBeamSection')
    Unassigns the current section from the selected CAE targets.
    Only targets where *this* section is actually assigned are affected;
    others are silently ignored.
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
    "name": "unassign_beam_section",
    "description": "Unassigns a beam section from one or more CAE targets. Only targets where this specific section is currently assigned are affected; others are silently skipped. Requires an active CAE document. In headless/API mode, 'targets' must be supplied explicitly since no GUI selection is available.",
    "command": "UnassignBeamSection",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the beam section to unassign"
            },
            "targets": {
                "type": "array",
                "description": "List of CAE targets to unassign the section from. Required in headless/API mode.",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": { "type": "integer", "description": "ID of the geometry" },
                        "type": { "type": "string", "enum": ["Geometry"], "description": "Target entity type" },
                        "subshape_id": { "type": "integer", "description": "Subshape index (-1 for whole geometry)" },
                        "subshape_type": { "type": "string", "enum": ["Edge"], "description": "Subshape type for beam sections" }
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


class BeamSectionCommandUnassign(AsCommand):
    """
    Unassigns the current BeamSection from the selected CAE targets.

    Only targets where *this* section is actually assigned are processed;
    targets assigned to another section (or unassigned) are silently skipped.

    initial_options (JSON)
    ----------------------
    {
      "component_id": <int>,
      "targets": [...]   // optional — see collect_targets()
    }
    """

    COMMAND_NAME = 'UnassignBeamSection'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._undo_cmd = None
        self._error = ''

    def execute(self, initial_options: str = ''):
        from opspro.Sections import SectionAssignUndo  # avoid circular import

        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            print(f'[{self.COMMAND_NAME}] Error: no active CAE document.')
            self.terminate(abort=True)
            return

        try:
            opts = json.loads(initial_options)
        except Exception as e:
            self._error = f'Invalid JSON input: {e}'
            print(f'[{self.COMMAND_NAME}] Error: bad initial_options ({e}).')
            self.terminate(abort=True)
            return

        try:
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'component_id missing or invalid: {e}'
            print(f'[{self.COMMAND_NAME}] Error: component_id missing or invalid ({e}).')
            self.terminate(abort=True)
            return

        try:
            section = (
                doc.pluginCaeComponents
                   .groups()[CAEComponentGroupUIDs.SECTIONS]
                   .collection[component_id]
            )
        except Exception as e:
            self._error = f'BeamSection with id={component_id} not found: {e}'
            print(f'[{self.COMMAND_NAME}] Error: section id={component_id} not found ({e}).')
            self.terminate(abort=True)
            return

        targets = collect_targets(doc, opts)
        if targets is None:
            self._error = 'Failed to acquire CAE targets.'
            print(f'[{self.COMMAND_NAME}] Error acquiring targets; aborting.')
            self.terminate(abort=True)
            return

        registry = get_assignment_registry()
        if registry is None:
            self._error = 'AssignmentRegistry not found.'
            print(f'[{self.COMMAND_NAME}] Error: AssignmentRegistry not found.')
            self.terminate(abort=True)
            return

        try:
            diff = AssignDiff.makeUnassignDiff(doc, registry, section, targets)
        except Exception as e:
            self._error = f'Failed to build unassignment diff: {e}'
            print(f'[{self.COMMAND_NAME}] Error building unassignment diff: {e}')
            self.terminate(abort=True)
            return

        if not diff.items:
            self._error = 'Section is not assigned to any of the selected targets.'
            print(f'[{self.COMMAND_NAME}] Section not assigned to any selected target; aborting.')
            self.terminate(abort=True)
            return

        diff.apply(invert=False)
        self._undo_cmd = SectionAssignUndo(
            self.COMMAND_NAME, diff.to_json(), invert=True
        )
        self.terminate(abort=False)

    def terminate(self, abort: bool):
        output = json.dumps({'status': not abort, 'error': self._error if abort else ''})
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            self.emitCommandExiting(AsCommandExitingArgs(False, self._undo_cmd, output))

    def create(self) -> 'BeamSectionCommandUnassign':
        return BeamSectionCommandUnassign()
