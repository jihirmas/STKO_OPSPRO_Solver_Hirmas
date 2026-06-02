import json

from PyMpc import App, AsCommand, AsCommandExitingArgs, AsUndoRedoCommand
from PySide2 import QtWidgets

from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator_dialog import (
    show_floating_editor,
)


class _GeotechnicalElementGeneratorEditUndo(AsUndoRedoCommand):
    def __init__(self, command_name: str, component_id: int, snapshot: str):
        super().__init__(command_name)
        self._command_name = command_name
        self._component_id = component_id
        self._snapshot = snapshot

    def execute(self):
        doc = App.caeDocument()
        if doc is None:
            return None
        try:
            comp = doc.pluginCaeComponents.groups()[
                CAEComponentGroupUIDs.GEOTECHNICAL_ELEMENT_GENERATORS
            ].collection[self._component_id]
        except Exception as e:
            print(f'[GeotechnicalElementGeneratorEditUndo] Could not retrieve component: {e}')
            return None
        current = comp.save()
        comp.restore(self._snapshot)
        comp.changed = True
        doc.commitChanges()
        doc.dirty = True
        return _GeotechnicalElementGeneratorEditUndo(self._command_name, self._component_id, current)


class GeotechnicalElementGeneratorCommandEdit(AsCommand):
    COMMAND_NAME = 'EditGeotechnicalElementGenerator'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._component = None
        self._before_snapshot = None
        self._error = ''
        self._output = ''
        self._headless = False

    def create(self):
        return GeotechnicalElementGeneratorCommandEdit()

    def execute(self, initial_options: str = ''):
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            self.terminate(abort=True)
            return

        try:
            opts = json.loads(initial_options) if initial_options else {}
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'Invalid input: {e}'
            self.terminate(abort=True)
            return

        try:
            self._component = doc.pluginCaeComponents.groups()[
                CAEComponentGroupUIDs.GEOTECHNICAL_ELEMENT_GENERATORS
            ].collection[component_id]
        except Exception as e:
            self._error = f'Geotechnical element generator with id={component_id} not found: {e}'
            self.terminate(abort=True)
            return

        has_changes = any(k in opts for k in ('name', 'dimension_mode', 'parameters'))
        self._headless = has_changes
        if not has_changes:
            show_floating_editor(self._component, QtWidgets.QApplication.activeWindow())
            self.terminate(abort=False, read_only=True)
            return

        self._before_snapshot = self._component.save()
        try:
            self._apply_options(opts)
            result = self._component.validate_configuration()
            if not result['valid']:
                raise ValueError('; '.join(result['errors']))
        except Exception as e:
            self._error = str(e)
            self._component.restore(self._before_snapshot)
            self.terminate(abort=True)
            return

        self._component.changed = True
        doc.commitChanges()
        doc.dirty = True
        self.terminate(abort=False)

    def terminate(self, abort: bool, read_only: bool = False):
        self._output = json.dumps({'status': not abort, 'error': self._error if abort else ''})
        if abort or read_only:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, self._output))
        else:
            undo_cmd = _GeotechnicalElementGeneratorEditUndo(
                self.COMMAND_NAME, int(self._component.id), self._before_snapshot
            )
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, self._output))

    def _apply_options(self, opts: dict):
        if 'name' in opts:
            self._component.name = str(opts['name'])
        if 'dimension_mode' in opts:
            self._component.dimension_mode = DimensionMode.normalize(opts['dimension_mode'])
        params = opts.get('parameters')
        if isinstance(params, dict):
            target_id = int(self._component.id)
            state = json.loads(self._component.save())
            state.update(params)
            if 'name' in opts:
                state['name'] = str(opts['name'])
            if 'dimension_mode' in opts:
                state['dimension_mode'] = DimensionMode.normalize(opts['dimension_mode'])
            self._component.restore(json.dumps(state))
            self._component.id = target_id

