from PyMpc import App, AsUndoRedoCommand

from opspro.utils import AssignDiff


class GeotechnicalElementGeneratorAssignUndo(AsUndoRedoCommand):
    def __init__(self, command_name: str, diff_json: str, *, invert: bool):
        super().__init__(command_name)
        self._command_name = command_name
        self._diff_json = diff_json
        self._invert = invert

    def execute(self):
        App.processEvents()
        try:
            diff = AssignDiff.from_json(self._diff_json)
            diff.apply(invert=self._invert)
        except Exception as e:
            direction = 'undo' if self._invert else 'redo'
            print(f'[GeotechnicalElementGeneratorAssignUndo] Error during {direction}: {e}')
            return None
        return GeotechnicalElementGeneratorAssignUndo(
            self._command_name, self._diff_json, invert=not self._invert
        )

