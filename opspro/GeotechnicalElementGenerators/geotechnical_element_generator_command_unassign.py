import json

from PyMpc import App, AsCommand, AsCommandExitingArgs

from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator_assign_undo import (
    GeotechnicalElementGeneratorAssignUndo,
)
from opspro.utils import AssignDiff, collect_targets, get_assignment_registry

"""
MCP_COMMAND_METADATA_START
{
  "name": "unassign_geotechnical_element_generator",
  "description": "Unassigns a geotechnical element generator from CAE targets.",
  "command": "UnassignGeotechnicalElementGenerator",
  "inputSchema": {
    "type": "object",
    "properties": {
      "component_id": {"type": "integer"},
      "targets": {"type": "array"}
    },
    "required": ["component_id", "targets"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "status": {"type": "boolean"},
      "error": {"type": "string"}
    }
  }
}
MCP_COMMAND_METADATA_END
"""


class GeotechnicalElementGeneratorCommandUnassign(AsCommand):
    COMMAND_NAME = 'UnassignGeotechnicalElementGenerator'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._undo_cmd = None
        self._error = ''

    def create(self):
        return GeotechnicalElementGeneratorCommandUnassign()

    def execute(self, initial_options: str = ''):
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
            comp = doc.pluginCaeComponents.groups()[
                CAEComponentGroupUIDs.GEOTECHNICAL_ELEMENT_GENERATORS
            ].collection[component_id]
        except Exception as e:
            self._error = f'Geotechnical element generator with id={component_id} not found: {e}'
            self.terminate(abort=True)
            return

        targets = collect_targets(doc, opts)
        if targets is None:
            self._error = 'Failed to acquire CAE targets.'
            self.terminate(abort=True)
            return

        registry = get_assignment_registry()
        if registry is None:
            self._error = 'AssignmentRegistry not found.'
            self.terminate(abort=True)
            return

        try:
            diff = AssignDiff.makeUnassignDiff(doc, registry, comp, targets)
        except Exception as e:
            self._error = f'Failed to build unassignment diff: {e}'
            self.terminate(abort=True)
            return

        if not diff.items:
            self._error = 'Generator is not assigned to any of the selected targets.'
            self.terminate(abort=True)
            return

        diff.apply(invert=False)
        self._undo_cmd = GeotechnicalElementGeneratorAssignUndo(
            self.COMMAND_NAME, diff.to_json(), invert=True
        )
        self.terminate(abort=False)

    def terminate(self, abort: bool):
        output = json.dumps({'status': not abort, 'error': self._error if abort else ''})
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            self.emitCommandExiting(AsCommandExitingArgs(False, self._undo_cmd, output))

