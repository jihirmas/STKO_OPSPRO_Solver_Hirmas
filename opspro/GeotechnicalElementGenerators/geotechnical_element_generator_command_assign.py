import json

from PyMpc import App, AsCommand, AsCommandExitingArgs

from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.GeotechnicalElementGenerators.assignment_types import (
    is_face_target,
    is_node_target,
    is_solid_target,
)
from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator_assign_undo import (
    GeotechnicalElementGeneratorAssignUndo,
)
from opspro.GeotechnicalElementGenerators.spring_foundation.spring_foundation_generator import (
    SpringFoundationGenerator,
)
from opspro.GeotechnicalElementGenerators.embedded_foundation.embedded_foundation_generator import (
    EmbeddedFoundationGenerator,
)
from opspro.utils import AssignDiff, collect_targets, get_assignment_registry

"""
MCP_COMMAND_METADATA_START
{
  "name": "assign_geotechnical_element_generator",
  "description": "Assigns a geotechnical element generator to compatible CAE targets. Spring Foundation accepts one vertex/node. Embedded Foundation accepts one face in 2D mode or one solid in 3D mode.",
  "command": "AssignGeotechnicalElementGenerator",
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


class _Targets:
    def __init__(self, items):
        self.items = items


class GeotechnicalElementGeneratorCommandAssign(AsCommand):
    COMMAND_NAME = 'AssignGeotechnicalElementGenerator'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._undo_cmd = None
        self._error = ''

    def create(self):
        return GeotechnicalElementGeneratorCommandAssign()

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

        filtered, rejected = self._filter_targets(comp, targets.items)
        if rejected:
            self._error = rejected
            self.terminate(abort=True)
            return
        if not filtered:
            self._error = 'No compatible target found for this generator.'
            self.terminate(abort=True)
            return

        registry = get_assignment_registry()
        if registry is None:
            self._error = 'AssignmentRegistry not found.'
            self.terminate(abort=True)
            return

        try:
            diff = AssignDiff.makeAssignDiff(doc, registry, comp, _Targets(filtered))
        except Exception as e:
            self._error = f'Failed to build assignment diff: {e}'
            self.terminate(abort=True)
            return

        if not diff.items:
            self._error = 'Generator is already assigned to the selected target or no valid target was found.'
            self.terminate(abort=True)
            return

        diff.apply(invert=False)
        assignment = registry.assignment_for_component(comp)
        result = comp.validate_assignment(assignment, doc)
        if not result['valid']:
            AssignDiff.from_json(diff.to_json()).apply(invert=True)
            self._error = '; '.join(result['errors'])
            self.terminate(abort=True)
            return

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

    def _filter_targets(self, comp, items):
        filtered = []
        for item in items:
            if isinstance(comp, SpringFoundationGenerator):
                if not is_node_target(item):
                    return [], 'Spring Foundation requires exactly one node.'
            elif isinstance(comp, EmbeddedFoundationGenerator):
                if comp.dimension_mode == DimensionMode.THREE_D:
                    if not is_solid_target(item):
                        return [], 'Embedded Foundation 3D requires one compatible solid geometry.'
                else:
                    if not is_face_target(item):
                        return [], 'Embedded Foundation 2D requires one compatible 2D geometry.'
            filtered.append(item)
        return filtered, ''

