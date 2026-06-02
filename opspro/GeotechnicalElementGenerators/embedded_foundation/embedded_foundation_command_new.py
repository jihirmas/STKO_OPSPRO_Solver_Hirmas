import json

from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    MpcCaeDocumentGeneralUndo,
)
from PySide2 import QtWidgets

from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator_dialog import (
    show_floating_editor,
)
from opspro.GeotechnicalElementGenerators.embedded_foundation.embedded_foundation_generator import (
    EmbeddedFoundationGenerator,
)

"""
MCP_COMMAND_METADATA_START
{
  "name": "new_embedded_foundation_generator",
  "description": "Creates an Embedded Foundation element generator. Supports 2D and 3D modes. The editor stores mechanical and interaction parameters while the mechanical expansion remains explicitly pending.",
  "command": "NewEmbeddedFoundationGenerator",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string"
      },
      "dimension_mode": {
        "type": "string",
        "enum": ["2D", "3D"]
      },
      "parameters": {
        "type": "object"
      }
    }
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "status": {
        "type": "boolean"
      },
      "component_id": {
        "type": "integer"
      },
      "error": {
        "type": "string"
      }
    }
  }
}
MCP_COMMAND_METADATA_END
"""


class EmbeddedFoundationCommandNew(AsCommand):
    COMMAND_NAME = 'NewEmbeddedFoundationGenerator'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._ret_args = None
        self._new_id = -1
        self._error = ''
        self._output = ''

    def create(self):
        return EmbeddedFoundationCommandNew()

    def execute(self, initial_options: str = ''):
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            self.terminate(abort=True)
            return

        opts = {}
        if initial_options:
            try:
                opts = json.loads(initial_options)
            except Exception as e:
                self._error = f'Invalid JSON input: {e}'
                self.terminate(abort=True)
                return

        next_id = self._next_id(doc)
        comp = EmbeddedFoundationGenerator(id=next_id)
        try:
            self._apply_options(comp, opts)
        except Exception as e:
            self._error = str(e)
            self.terminate(abort=True)
            return

        if initial_options:
            result = comp.validate_configuration()
            if not result['valid']:
                self._error = '; '.join(result['errors'])
                self.terminate(abort=True)
                return

        self._new_id = next_id
        self._ret_args = doc.addPluginCaeComponent(comp)
        doc.commitChanges()
        doc.dirty = True

        if not initial_options:
            show_floating_editor(comp, QtWidgets.QApplication.activeWindow())

        self.terminate(abort=False)

    def terminate(self, abort: bool):
        self._output = json.dumps({
            'status': not abort,
            'component_id': self._new_id,
            'error': self._error if abort else '',
        })
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, self._output))
        else:
            undo_cmd = MpcCaeDocumentGeneralUndo(self.COMMAND_NAME, self._ret_args)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, self._output))

    def _apply_options(self, comp: EmbeddedFoundationGenerator, opts: dict):
        if not opts:
            return
        if 'name' in opts:
            comp.name = str(opts['name'])
        if 'dimension_mode' in opts:
            comp.dimension_mode = DimensionMode.normalize(opts['dimension_mode'])
        params = opts.get('parameters')
        if isinstance(params, dict):
            target_id = int(comp.id)
            state = json.loads(comp.save())
            state.update(params)
            if 'name' in opts:
                state['name'] = str(opts['name'])
            if 'dimension_mode' in opts:
                state['dimension_mode'] = DimensionMode.normalize(opts['dimension_mode'])
            comp.restore(json.dumps(state))
            comp.id = target_id

    @staticmethod
    def _next_id(doc) -> int:
        try:
            groups = doc.pluginCaeComponents.groups()
            group_id = CAEComponentGroupUIDs.GEOTECHNICAL_ELEMENT_GENERATORS
            if group_id not in groups:
                return 1
            return groups[group_id].collection.getlastkey(0) + 1
        except Exception as e:
            print(f'[EmbeddedFoundationCommandNew] Warning: could not compute next ID ({e}); defaulting to 1.')
            return 1

