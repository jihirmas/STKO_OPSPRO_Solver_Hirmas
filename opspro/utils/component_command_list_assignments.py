"""
component_command_list_assignments.py
--------------------------------------
Abstract base command that lists all CAE entities (geometries and
interactions) to which a given plugin component is currently assigned.

Subclasses must supply:
  - COMMAND_NAME  (class attribute str)
  - component_group_id (property → str)  ← CAEComponentGroupUIDs constant

The command is headless-friendly: it reads initial_options JSON, queries
the AssignmentRegistry's inverse map, and exits immediately without any
undo entry.

Input JSON
----------
{ "component_id": <int> }

Output JSON
-----------
{
  "status": true | false,
  "error":  "",
  "assignments": {
    "geometries": [
      {
        "id": <int>,
        "subshapes": {
          "vertex": [<int>, ...],
          "edge":   [<int>, ...],
          "face":   [<int>, ...],
          "solid":  [<int>, ...]
        }
      }
    ],
    "interactions": [<int>, ...]
  }
}
"""

from __future__ import annotations

import json
from abc import abstractmethod

from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
)

from opspro.utils.assignment_registry import get_assignment_registry


class ComponentCommandListAssignments(AsCommand):
    """
    Read-only command: returns all CAE entities assigned to a component.

    Subclasses must define:
        COMMAND_NAME (str)           — name registered with the command system
        component_group_id (str)     — CAEComponentGroupUIDs constant for the component group
    """

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._output: str = ''

    # ------------------------------------------------------------------
    # Abstract interface for subclasses
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def component_group_id(self) -> str:
        """Return the CAEComponentGroupUIDs string for this component type."""

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        try:
            opts = json.loads(initial_options) if initial_options else {}
            component_id = int(opts.get('component_id', -1))
            if component_id < 0:
                self._finish(False, 'component_id is required and must be a non-negative integer')
                return

            doc = App.caeDocument()
            if doc is None:
                self._finish(False, 'No active CAE document')
                return

            # Resolve the component object
            all_groups = doc.pluginCaeComponents.groups()
            group = all_groups.get(self.component_group_id)
            if group is None:
                self._finish(False, f'Component group "{self.component_group_id}" not found')
                return
            component = group.collection.get(component_id)
            if component is None:
                self._finish(False, f'Component with ID {component_id} not found in group "{self.component_group_id}"')
                return

            # Query the inverse map
            registry = get_assignment_registry()
            if registry is None:
                self._finish(False, 'AssignmentRegistry not found in the active document')
                return

            asn = registry.assignment_for_component(component)
            if asn is None:
                # Component exists but is not assigned anywhere — return empty lists
                result = {'geometries': [], 'interactions': []}
            else:
                geometries = []
                for geom, cga_item in asn.geometries.items():
                    subshapes = {
                        'vertex': sorted(cga_item.vertices),
                        'edge':   sorted(cga_item.edges),
                        'face':   sorted(cga_item.faces),
                        'solid':  sorted(cga_item.solids),
                    }
                    geometries.append({'id': int(geom.id), 'subshapes': subshapes})
                # Sort by geometry ID for deterministic output
                geometries.sort(key=lambda x: x['id'])

                interactions = sorted(int(i.id) for i in asn.interactions)
                result = {'geometries': geometries, 'interactions': interactions}

            self._finish(True, '', result)

        except Exception as e:
            self._finish(False, str(e))

    def terminate(self, abort: bool):
        self.emitCommandExiting(AsCommandExitingArgs(True, None, self._output))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _finish(self, ok: bool, error: str, assignments: dict = None):
        payload = {'status': ok, 'error': error}
        if assignments is not None:
            payload['assignments'] = assignments
        elif ok:
            payload['assignments'] = {'geometries': [], 'interactions': []}
        self._output = json.dumps(payload)
        self.terminate(abort=False)
