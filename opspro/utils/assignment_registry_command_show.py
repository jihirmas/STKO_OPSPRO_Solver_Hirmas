from PyMpc import (
    AsCommand,
    AsCommandExitingArgs,
)
from opspro.utils.assignment_registry import get_assignment_registry
from opspro.utils.assignment_registry_dialog import AssignmentRegistryDialog
from PySide2 import QtWidgets

class AssignmentRegistryCommandShow(AsCommand):
    """
    Read-only command that opens the AssignmentRegistryDialog.

    No undo/redo entry is created because the command does not modify
    any document state.
    """

    COMMAND_NAME = 'ShowAssignmentRegistry'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg: AssignmentRegistryDialog = None

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        registry = get_assignment_registry()
        if registry is None:
            print(f'[{self.COMMAND_NAME}] Error: AssignmentRegistry not found in the active document.')
            self.terminate(abort=True)
            return

        self._dlg = AssignmentRegistryDialog(registry, parent=QtWidgets.QApplication.activeWindow())
        self._dlg.setModal(True)
        self._dlg.finished.connect(self._on_finished)
        self._dlg.show()

    def terminate(self, abort: bool):
        self._cleanup_dialog()
        # No state change → never push an undo entry regardless of abort flag
        self.emitCommandExiting(AsCommandExitingArgs(True, None, ''))

    def create(self) -> 'AssignmentRegistryCommandShow':
        return AssignmentRegistryCommandShow()

    # ------------------------------------------------------------------
    # Dialog callback
    # ------------------------------------------------------------------

    def _on_finished(self, result: int):
        self.terminate(abort=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _cleanup_dialog(self):
        if self._dlg is not None:
            self._dlg.deleteLater()
            self._dlg = None
