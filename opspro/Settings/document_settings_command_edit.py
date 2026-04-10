from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    AsUndoRedoCommand
)
from opspro.Settings.document_settings import DocumentSettings
from opspro.Settings.document_settings_dialog import DocumentSettingsDialog
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from PySide2 import QtWidgets


class _DocumentSettingsEditUndo(AsUndoRedoCommand):
    """
    Swap-based undo/redo for a DocumentSettings edit.

    Each call to execute() captures the current settings state, restores the
    stored snapshot, then returns a new _DocumentSettingsEditUndo holding the
    just-captured state so that the next call undoes/redoes correctly.
    """

    def __init__(self, command_name: str, component_id: int, snapshot: str):
        super().__init__(command_name)
        self._command_name = command_name
        self._component_id = component_id
        self._snapshot = snapshot   # settings state to restore on next undo/redo

    def execute(self):
        doc = App.caeDocument()
        if doc is None:
            return None
        try:
            groups = doc.pluginCaeComponents.groups()
            settings: DocumentSettings = groups[CAEComponentGroupUIDs.SETTINGS].collection[self._component_id]
        except Exception as e:
            print(f'[DocumentSettingsEditUndo] Could not retrieve settings id={self._component_id}: {e}')
            return None

        current_snapshot = settings.save()   # capture state before overwriting
        settings.restore(self._snapshot)     # apply stored snapshot (also calls settings.apply())
        settings.changed = True
        doc.commitChanges()
        doc.dirty = True

        # Return inverse command so redo/undo always works
        return _DocumentSettingsEditUndo(self._command_name, self._component_id, current_snapshot)


class DocumentSettingsCommandEdit(AsCommand):
    """
    Command that opens a DocumentSettingsDialog pre-populated with the current
    DocumentSettings and, on acceptance, applies the edited values with full
    undo/redo support.

    DocumentSettings is a document-level singleton (always id=1) stored in the
    SETTINGS component group. No options parsing is needed.
    """

    COMMAND_NAME = 'EditDocumentSettings'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg: DocumentSettingsDialog = None
        self._settings: DocumentSettings = None
        self._before_snapshot: str = None

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        doc = App.caeDocument()
        if doc is None:
            print(f'[{self.COMMAND_NAME}] Error: no active CAE document.')
            self.terminate(abort=True)
            return

        # Retrieve the DocumentSettings singleton from the document
        try:
            groups = doc.pluginCaeComponents.groups()
            settings_collection = groups[CAEComponentGroupUIDs.SETTINGS].collection
            # DocumentSettings is always registered with id=1
            self._settings = next(iter(settings_collection.values()))
        except Exception as e:
            print(f'[{self.COMMAND_NAME}] Error: could not retrieve DocumentSettings ({e}).')
            self.terminate(abort=True)
            return

        self._dlg = DocumentSettingsDialog(settings=self._settings, parent=QtWidgets.QApplication.activeWindow())
        self._dlg.setModal(True)

        self._dlg.accepted.connect(self._on_accept)
        self._dlg.rejected.connect(self._on_reject)

        self._dlg.show()

    def terminate(self, abort: bool):
        self._cleanup_dialog()
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, ''))
        else:
            undo_cmd = _DocumentSettingsEditUndo(
                self.COMMAND_NAME, int(self._settings.id), self._before_snapshot)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, ''))

    def create(self) -> AsCommand:
        return DocumentSettingsCommandEdit()

    # ------------------------------------------------------------------
    # Dialog callbacks
    # ------------------------------------------------------------------

    def _on_accept(self):
        doc = App.caeDocument()
        if doc is None:
            print(f'[{self.COMMAND_NAME}] Error: document became unavailable.')
            self.terminate(abort=True)
            return

        data = self._dlg.data()
        if not data:
            self.terminate(abort=True)
            return

        # Snapshot state before editing (used by the undo command)
        self._before_snapshot = self._settings.save()

        # Apply edited values and propagate the new unit system
        self._dlg.apply_to(self._settings)
        self._settings.changed = True
        doc.commitChanges()
        doc.dirty = True

        self.terminate(abort=False)

    def _on_reject(self):
        self.terminate(abort=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _cleanup_dialog(self):
        if self._dlg is not None:
            self._dlg.deleteLater()
            self._dlg = None
