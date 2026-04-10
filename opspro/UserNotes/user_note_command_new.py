from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    MpcCaeDocumentGeneralUndo,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.UserNotes.user_note import UserNote
from PySide2 import QtWidgets
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_user_note",
    "description": "Creates a new free-text user note in the active document. The note is stored in the User Notes component group and is not assigned to any geometry. All parameters are optional. Requires an active CAE document.",
    "command": "NewUserNote",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Optional display name for the note. Default: 'UserNote'"
            },
            "text": {
                "type": "string",
                "description": "Optional body text of the note. Default: empty string"
            }
        }
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status":       {"type": "boolean", "description": "true on success, false on failure"},
            "component_id": {"type": "integer", "description": "ID of the newly created note, or -1 on failure"},
            "error":        {"type": "string",  "description": "Error message if status is false, empty string on success"}
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class UserNoteCommandNew(AsCommand):
    """Command that creates a new UserNote."""

    COMMAND_NAME = 'NewUserNote'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg      = None
        self._ret_args = None
        self._new_id   = -1
        self._error    = ''
        self._headless = False

    def create(self):
        return UserNoteCommandNew()

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        self._headless = bool(initial_options)
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            self.terminate(abort=True)
            return

        if initial_options:
            try:
                opts = json.loads(initial_options)
            except Exception as e:
                self._error = f'Invalid JSON input: {e}'
                self.terminate(abort=True)
                return

            next_id = self._next_id(doc)
            note = UserNote(id=next_id)
            if 'name' in opts:
                note.name = str(opts['name'])
            note.text = str(opts.get('text', ''))

            self._new_id   = next_id
            self._ret_args = doc.addPluginCaeComponent(note)
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # GUI mode
        next_id = self._next_id(doc)
        proto   = UserNote(id=next_id)
        dlg_cls = UserNote.dialog_class()
        self._dlg = dlg_cls(note=proto, parent=QtWidgets.QApplication.activeWindow(), is_new=True)
        self._dlg.setModal(True)
        self._dlg.accepted.connect(self._on_accept)
        self._dlg.rejected.connect(self._on_reject)
        self._dlg.show()

    def terminate(self, abort: bool):
        self._cleanup_dialog()
        output = ''
        if self._headless:
            output = json.dumps({
                'status':       not abort,
                'component_id': self._new_id if not abort else -1,
                'error':        self._error if abort else '',
            })
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            undo_cmd = MpcCaeDocumentGeneralUndo(self.COMMAND_NAME, self._ret_args)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))

    # ------------------------------------------------------------------
    # Dialog callbacks
    # ------------------------------------------------------------------

    def _on_accept(self):
        doc = App.caeDocument()
        if doc is None:
            self.terminate(abort=True)
            return
        d = self._dlg.data()
        next_id = self._next_id(doc)
        note = UserNote(id=next_id, name=d['name'])
        note.text = d['text']
        self._new_id   = next_id
        self._ret_args = doc.addPluginCaeComponent(note)
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

    @staticmethod
    def _next_id(doc) -> int:
        try:
            groups = doc.pluginCaeComponents.groups()
            collection = groups[CAEComponentGroupUIDs.USER_NOTES].collection
            return max((int(n.id) for n in collection.values()), default=0) + 1
        except Exception:
            return 1
