from PySide2 import QtCore, QtWidgets

from opspro.UserNotes.user_note import UserNote


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


class UserNoteDialog(QtWidgets.QDialog):
    """
    QDialog for creating a new UserNote or editing an existing one.

    Usage
    -----
    Create mode::

        dlg = UserNoteDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()

    Edit mode::

        dlg = UserNoteDialog(note=note, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()
    """

    def __init__(self, note: UserNote = None, parent=None, is_new=False):
        super().__init__(parent)
        print(f'[UserNoteDialog] Initializing dialog for note id={getattr(note, "id", None)}, is_new={is_new}')
        self._is_new = is_new
        self._setup_ui()
        self._populate(note)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New User Note' if self._is_new else 'Edit User Note'
        self.setWindowTitle(title)
        self.setMinimumWidth(480)
        self.setMinimumHeight(320)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 60)
        grid.setColumnStretch(1, 1)

        def _lbl(text):
            l = QtWidgets.QLabel(text)
            l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            return l

        row = 0

        # ---- Name ----
        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('e.g. Design assumptions')
        grid.addWidget(_lbl('Name:'), row, 0)
        grid.addWidget(self._edit_name, row, 1)
        row += 1

        grid.addWidget(_hline(), row, 0, 1, 2)
        row += 1

        # ---- Text body ----
        grid.addWidget(QtWidgets.QLabel('<b>Note text</b>'), row, 0, 1, 2)
        row += 1

        self._edit_text = QtWidgets.QPlainTextEdit()
        self._edit_text.setPlaceholderText('Enter your note here…')
        self._edit_text.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        grid.addWidget(self._edit_text, row, 0, 1, 2)
        row += 1

        grid.setRowStretch(row - 1, 1)

        # ---- Button box ----
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal
        )
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(grid)
        main_layout.addSpacing(4)
        main_layout.addWidget(_hline())
        main_layout.addWidget(btn_box)

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, note: UserNote):
        if note is None:
            return
        self._edit_name.setText(str(note.name))
        self._edit_text.setPlainText(str(note.text))

    # ------------------------------------------------------------------
    # Validation & acceptance
    # ------------------------------------------------------------------

    def _on_accepted(self):
        name = self._edit_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, 'Invalid input', 'Name must not be empty.')
            return
        self._validated_data = {
            'name': name,
            'text': self._edit_text.toPlainText(),
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def data(self):
        """Return validated dict with keys ``name`` (str) and ``text`` (str)."""
        return getattr(self, '_validated_data', {})

    def apply_to(self, note: UserNote):
        """Write the validated data directly onto *note*."""
        d = self.data()
        if not d:
            return
        note.name = d['name']
        note.text = d['text']
