from PyMpc import MpcPluginCaeComponent
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
import json


class UserNote(MpcPluginCaeComponent):
    """
    A free-text annotation that the user can attach to a document.
    It lives in the USER_NOTES component group and is never assigned
    to any geometry or interaction.
    """

    def __init__(self, id=1, name='UserNote'):
        super().__init__(id, name)
        self.text = ''   # free-form note body

    def componentGroupID(self):
        return CAEComponentGroupUIDs.USER_NOTES

    @classmethod
    def dialog_class(cls):
        from opspro.UserNotes.user_note_dialog import UserNoteDialog
        return UserNoteDialog

    def className(self):
        return 'UserNote'

    def description(self):
        return 'Free-text annotation stored in the document'

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def save(self):
        try:
            return json.dumps({'ID': int(self.id), 'name': self.name,
                               'changed': self.changed, 'text': self.text})
        except Exception as e:
            print(f'[UserNote] Error serializing id={self.id}: {e}')
            return ''

    def restore(self, state):
        if not state:
            return
        try:
            data = json.loads(state)
        except Exception as e:
            print(f'[UserNote] Error parsing state: {e}')
            return
        self.id      = data.get('ID',      self.id)
        self.name    = data.get('name',    self.name)
        self.changed = data.get('changed', self.changed)
        self.text    = data.get('text',    self.text)

    def __repr__(self):
        preview = (self.text[:40] + '…') if len(self.text) > 40 else self.text
        return f"UserNote(id={int(self.id)}, name={self.name!r}, text={preview!r})"
