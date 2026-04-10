from PySide2 import QtCore, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Hinges.beam_end_release import BeamEndRelease
from opspro.Hinges.beam_hinge import HingeAnchor


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


def _lbl(text):
    l = QtWidgets.QLabel(text)
    l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    return l


def _header(text):
    l = QtWidgets.QLabel(f'<b>{text}</b>')
    return l


# Anchor options available for end-releases (C = centre is not meaningful here)
_ANCHOR_OPTIONS = [
    (HingeAnchor.IJ, 'I and J  (both ends)'),
    (HingeAnchor.I,  'I  (near end)'),
    (HingeAnchor.J,  'J  (far end)'),
]

# DOF display labels (HTML, rendered by QLabel auto-detection)
# All DOFs are expressed in the element local reference frame.
_DOF_LABELS = {
    'Ux': 'U<sub>x</sub>',
    'Uy': 'U<sub>y</sub>',
    'Uz': 'U<sub>z</sub>',
    'Rx': 'R<sub>x</sub>',
    'Ry': 'R<sub>y</sub>',
    'Rz': 'R<sub>z</sub>',
}

_DOF_DESCRIPTIONS = {
    'Ux': 'release the translation along the local-x axis',
    'Uy': 'release the translation along the local-y axis',
    'Uz': 'release the translation along the local-z axis',
    'Rx': 'release the rotation about the local-x axis',
    'Ry': 'release the rotation about the local-y axis',
    'Rz': 'release the rotation about the local-z axis',
}


class BeamEndReleaseDialog(QtWidgets.QDialog):
    """
    QDialog for creating or editing a BeamEndRelease component.

    Usage
    -----
    Create mode::

        dlg = BeamEndReleaseDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            dlg.apply_to(component)

    Edit mode::

        dlg = BeamEndReleaseDialog(component=existing, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            dlg.apply_to(existing)
    """

    def __init__(self, component: BeamEndRelease = None, parent=None, is_new=False):
        super().__init__(parent)
        self._component = component
        self._is_new = is_new
        self._setup_ui()
        self._populate(component)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New Beam End Release' if self._is_new else 'Edit Beam End Release'
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        ureg = ParameterManager._unit_registry

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 80)
        grid.setColumnMinimumWidth(1, 60)
        grid.setColumnMinimumWidth(2, 60)
        grid.setColumnStretch(3, 1)
        row = 0

        # ---- Name -------------------------------------------------------
        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('e.g. Pin I-end')
        grid.addWidget(_lbl('Name:'), row, 0)
        grid.addWidget(self._edit_name, row, 1, 1, 3)
        row += 1

        # ---- Location section -------------------------------------------
        grid.addWidget(_hline(), row, 0, 1, 4)
        row += 1
        grid.addWidget(_header('Location'), row, 0, 1, 4)
        row += 1

        self._combo_anchor = QtWidgets.QComboBox()
        for val, label in _ANCHOR_OPTIONS:
            self._combo_anchor.addItem(label, userData=val)
        grid.addWidget(_lbl('Anchor:'), row, 0)
        grid.addWidget(self._combo_anchor, row, 1, 1, 3)
        row += 1

        self._lbl_offset = _lbl('Offset:')
        self._edit_offset = ExpressionLineEdit(default_value=0.0 * ureg.m)
        self._desc_offset = QtWidgets.QLabel(
            '<span style="color:gray;font-style:italic;">'
            'Distance from anchor along beam axis (\u2265 0)</span>'
        )
        self._desc_offset.setTextFormat(QtCore.Qt.RichText)
        grid.addWidget(self._lbl_offset, row, 0)
        grid.addWidget(self._edit_offset, row, 1)
        grid.addWidget(self._desc_offset, row, 2, 1, 2)
        row += 1

        # ---- Released DOFs section --------------------------------------
        grid.addWidget(_hline(), row, 0, 1, 4)
        row += 1
        grid.addWidget(_header('Released DOFs'), row, 0, 1, 4)
        row += 1

        # Column headers: blank label | I end | J end | description
        grid.addWidget(QtWidgets.QLabel(''), row, 0)
        self._hdr_I = QtWidgets.QLabel('<b>I end</b>')
        self._hdr_I.setAlignment(QtCore.Qt.AlignHCenter)
        self._hdr_J = QtWidgets.QLabel('<b>J end</b>')
        self._hdr_J.setAlignment(QtCore.Qt.AlignHCenter)
        grid.addWidget(self._hdr_I, row, 1)
        grid.addWidget(self._hdr_J, row, 2)
        grid.addWidget(QtWidgets.QLabel(''), row, 3)
        row += 1

        # One row per DOF
        self._checks_I = {}
        self._checks_J = {}
        for key in BeamEndRelease.DOF_KEYS:
            lbl_w = _lbl(_DOF_LABELS.get(key, key) + ':')
            cb_I = QtWidgets.QCheckBox()
            cb_I.setStyleSheet('margin-left: auto; margin-right: auto;')
            cb_J = QtWidgets.QCheckBox()
            cb_J.setStyleSheet('margin-left: auto; margin-right: auto;')

            # centre the checkboxes in their cells
            w_I = QtWidgets.QWidget()
            h_I = QtWidgets.QHBoxLayout(w_I)
            h_I.setContentsMargins(0, 0, 0, 0)
            h_I.addStretch()
            h_I.addWidget(cb_I)
            h_I.addStretch()

            w_J = QtWidgets.QWidget()
            h_J = QtWidgets.QHBoxLayout(w_J)
            h_J.setContentsMargins(0, 0, 0, 0)
            h_J.addStretch()
            h_J.addWidget(cb_J)
            h_J.addStretch()

            desc_lbl = QtWidgets.QLabel(_DOF_DESCRIPTIONS.get(key, ''))
            desc_lbl.setStyleSheet('color: gray; font-style: italic;')

            grid.addWidget(lbl_w, row, 0)
            grid.addWidget(w_I, row, 1)
            grid.addWidget(w_J, row, 2)
            grid.addWidget(desc_lbl, row, 3)
            self._checks_I[key] = cb_I
            self._checks_J[key] = cb_J
            row += 1

        # ---- vertical spacer -------------------------------------------
        grid.setRowStretch(row, 1)

        # ---- Button box ------------------------------------------------
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal
        )
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        # ---- Main layout -----------------------------------------------
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(grid)
        main_layout.addSpacing(4)
        main_layout.addWidget(_hline())
        main_layout.addWidget(btn_box)

        # Wire anchor combo → update column visibility
        self._combo_anchor.currentIndexChanged.connect(self._on_anchor_changed)

    # ------------------------------------------------------------------
    # Anchor → column enable/disable
    # ------------------------------------------------------------------

    def _on_anchor_changed(self, _index=None):
        anchor = self._combo_anchor.currentData()
        show_I = anchor in (HingeAnchor.I,  HingeAnchor.IJ)
        show_J = anchor in (HingeAnchor.J,  HingeAnchor.IJ)

        self._hdr_I.setEnabled(show_I)
        self._hdr_J.setEnabled(show_J)
        for key in BeamEndRelease.DOF_KEYS:
            self._checks_I[key].setEnabled(show_I)
            self._checks_J[key].setEnabled(show_J)

        # Offset: always editable (symmetric for IJ, from respective end)
        # Disable offset only when both ends have the same distance = 0
        # (no restriction; let the user decide)

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, component: BeamEndRelease):
        """Fill widgets from an existing BeamEndRelease (edit mode)."""
        if component is None:
            self._on_anchor_changed()
            return

        self._edit_name.setText(str(component.name))

        # Anchor
        for i, (val, _) in enumerate(_ANCHOR_OPTIONS):
            if val == component.anchor:
                self._combo_anchor.setCurrentIndex(i)
                break

        # Offset
        self._edit_offset.set_quantity(component.offset)

        # DOF checkboxes
        for key in BeamEndRelease.DOF_KEYS:
            self._checks_I[key].setChecked(bool(component.dofs_I.get(key, False)))
            self._checks_J[key].setChecked(bool(component.dofs_J.get(key, False)))

        self._on_anchor_changed()

    # ------------------------------------------------------------------
    # Validation & acceptance
    # ------------------------------------------------------------------

    def _on_accepted(self):
        errors = []

        name = self._edit_name.text().strip()
        if not name:
            errors.append('Name must not be empty.')

        offset_val = self._edit_offset.value
        offset_err = self._edit_offset.error
        if offset_err:
            errors.append(f'Offset: {offset_err}')
        elif offset_val.dimensionality != self._edit_offset.expected_dimensionality:
            errors.append('Offset must be a length quantity (e.g. 0.3[m]).')
        elif float(offset_val.to_base_units().magnitude) < 0.0:
            errors.append('Offset must be \u2265 0.')

        anchor = self._combo_anchor.currentData()
        show_I = anchor in (HingeAnchor.I,  HingeAnchor.IJ)
        show_J = anchor in (HingeAnchor.J,  HingeAnchor.IJ)

        dofs_I = {k: (self._checks_I[k].isChecked() if show_I else False)
                  for k in BeamEndRelease.DOF_KEYS}
        dofs_J = {k: (self._checks_J[k].isChecked() if show_J else False)
                  for k in BeamEndRelease.DOF_KEYS}

        if not any(dofs_I.values()) and not any(dofs_J.values()):
            errors.append('At least one DOF must be released.')

        if errors:
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._validated = {
            'name':   name,
            'anchor': anchor,
            'offset': offset_val,
            'dofs_I': dofs_I,
            'dofs_J': dofs_J,
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def apply_to(self, component: BeamEndRelease):
        """Write validated data back to a BeamEndRelease instance."""
        d = self._validated
        component.name   = d['name']
        component.anchor = d['anchor']
        component.offset = d['offset']
        component.dofs_I = d['dofs_I']
        component.dofs_J = d['dofs_J']
