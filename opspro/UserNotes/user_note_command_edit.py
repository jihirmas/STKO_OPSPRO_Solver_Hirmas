from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    AsUndoRedoCommand,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.UserNotes.user_note import UserNote
from PySide2 import QtWidgets
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "edit_user_note",
    "description": "Edits an existing user note in the active document, identified by its component_id. Supply name and/or text to update; omitted fields keep their current values. Requires an active CAE document.",
    "command": "EditUserNote",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the note to edit"
            },
            "name": {
                "type": "string",
                "description": "Optional: new display name for the note"
            },
            "text": {
                "type": "string",
                "description": "Optional: new body text for the note"
            }
        },
        "required": ["component_id"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": {"type": "boolean", "description": "true on success, false on failure"},
            "error":  {"type": "string",  "description": "Error message if status is false, empty string on success"}
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class _UserNoteEditUndo(AsUndoRedoCommand):
    """Swap-based undo/redo for a UserNote edit."""

    def __init__(self, command_name: str, component_id: int, snapshot: str):
        super().__init__(command_name)
        self._command_name = command_name
        self._component_id = component_id
        self._snapshot     = snapshot

    def execute(self):
        doc = App.caeDocument()
        if doc is None:
            return None
        try:
            groups = doc.pluginCaeComponents.groups()
            note: UserNote = groups[CAEComponentGroupUIDs.USER_NOTES].collection[self._component_id]
        except Exception as e:
            print(f'[UserNoteEditUndo] Could not retrieve note id={self._component_id}: {e}')
            return None

        current_snapshot = note.save()
        note.restore(self._snapshot)
        note.changed = True
        doc.commitChanges()
        doc.dirty = True
        return _UserNoteEditUndo(self._command_name, self._component_id, current_snapshot)


class UserNoteCommandEdit(AsCommand):
    """Command for editing an existing UserNote (GUI or headless)."""

    COMMAND_NAME = 'EditUserNote'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg             = None
        self._note: UserNote  = None
        self._before_snapshot = None
        self._headless        = False
        self._error           = ''

    def create(self):
        return UserNoteCommandEdit()

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            self.terminate(abort=True)
            return

        try:
            opts         = json.loads(initial_options)
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'Invalid input: {e}'
            self.terminate(abort=True)
            return

        try:
            groups     = doc.pluginCaeComponents.groups()
            self._note = groups[CAEComponentGroupUIDs.USER_NOTES].collection[component_id]
        except Exception as e:
            self._error = f'Note with id={component_id} not found: {e}'
            self.terminate(abort=True)
            return

        # Headless path: name and/or text supplied alongside component_id
        if 'name' in opts or 'text' in opts:
            self._headless = True
            self._before_snapshot = self._note.save()
            if 'name' in opts:
                self._note.name = str(opts['name'])
            if 'text' in opts:
                self._note.text = str(opts['text'])
            self._note.changed = True
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # GUI mode: only component_id provided → open dialog pre-populated
        dlg_cls   = UserNote.dialog_class()
        self._dlg = dlg_cls(note=self._note, parent=QtWidgets.QApplication.activeWindow())
        self._dlg.setModal(True)
        self._dlg.accepted.connect(self._on_accept)
        self._dlg.rejected.connect(self._on_reject)
        self._dlg.show()

    def terminate(self, abort: bool):
        self._cleanup_dialog()
        output = ''
        if self._headless:
            output = json.dumps({'status': not abort, 'error': self._error if abort else ''})
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            undo_cmd = _UserNoteEditUndo(self.COMMAND_NAME, int(self._note.id), self._before_snapshot)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))

    # ------------------------------------------------------------------
    # Dialog callbacks
    # ------------------------------------------------------------------

    def _on_accept(self):
        doc = App.caeDocument()
        if doc is None:
            self.terminate(abort=True)
            return
        self._before_snapshot = self._note.save()
        self._dlg.apply_to(self._note)
        self._note.changed = True
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
