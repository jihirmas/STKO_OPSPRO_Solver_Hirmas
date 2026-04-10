from PySide2 import QtCore, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Hinges.beam_rotational_hinge import BeamRotationalHinge
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
    return QtWidgets.QLabel(f'<b>{text}</b>')


# C = centre is not meaningful for a rotational hinge (end-located spring)
_ANCHOR_OPTIONS = [
    (HingeAnchor.IJ, 'I and J  (both ends)'),
    (HingeAnchor.I,  'I  (near end)'),
    (HingeAnchor.J,  'J  (far end)'),
]

_DOF_LABELS = {
    'Ry': 'R<sub>y</sub>  (moment about the local-y axis)',
    'Rz': 'R<sub>z</sub>  (moment about the local-z axis)',
}

_OFFSET_NOTE = {
    HingeAnchor.IJ: 'Same offset applied from both I and J ends inward.',
    HingeAnchor.I:  'Distance from node-I in the direction I \u2192 J.',
    HingeAnchor.J:  'Distance from node-J in the direction J \u2192 I (inward).',
}


class BeamRotationalHingeDialog(QtWidgets.QDialog):
    """
    QDialog for creating or editing a BeamRotationalHinge component.

    Usage
    -----
    Create mode::

        dlg = BeamRotationalHingeDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            dlg.apply_to(component)

    Edit mode::

        dlg = BeamRotationalHingeDialog(component=existing, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            dlg.apply_to(existing)
    """

    def __init__(self, component: BeamRotationalHinge = None, parent=None, is_new=False):
        super().__init__(parent)
        self._component = component
        self._is_new = is_new
        self._setup_ui()
        self._populate(component)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New Beam Rotational Hinge' if self._is_new else 'Edit Beam Rotational Hinge'
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        ureg = ParameterManager._unit_registry

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 80)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        row = 0

        # ---- Name -------------------------------------------------------
        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('e.g. Plastic hinge I-end')
        grid.addWidget(_lbl('Name:'), row, 0)
        grid.addWidget(self._edit_name, row, 1, 1, 2)
        row += 1

        # ---- Location section -------------------------------------------
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(_header('Location'), row, 0, 1, 3)
        row += 1

        self._combo_anchor = QtWidgets.QComboBox()
        for val, label in _ANCHOR_OPTIONS:
            self._combo_anchor.addItem(label, userData=val)
        grid.addWidget(_lbl('Anchor:'), row, 0)
        grid.addWidget(self._combo_anchor, row, 1, 1, 2)
        row += 1

        self._edit_offset = ExpressionLineEdit(default_value=0.0 * ureg.m)
        self._desc_offset = QtWidgets.QLabel()
        self._desc_offset.setTextFormat(QtCore.Qt.RichText)
        grid.addWidget(_lbl('Offset:'), row, 0)
        grid.addWidget(self._edit_offset, row, 1)
        grid.addWidget(self._desc_offset, row, 2)
        row += 1

        # ---- Active DOFs section ----------------------------------------
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(_header('Active rotational DOFs'), row, 0, 1, 3)
        row += 1

        self._checks = {}
        for key in BeamRotationalHinge.DOF_KEYS:
            cb = QtWidgets.QCheckBox()
            lbl = QtWidgets.QLabel(_DOF_LABELS.get(key, key))
            row_w = QtWidgets.QWidget()
            h = QtWidgets.QHBoxLayout(row_w)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(4)
            h.addWidget(cb)
            h.addWidget(lbl)
            h.addStretch()
            grid.addWidget(row_w, row, 1, 1, 2)
            self._checks[key] = cb
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

        self._combo_anchor.currentIndexChanged.connect(self._on_anchor_changed)

    # ------------------------------------------------------------------
    # Anchor → offset note
    # ------------------------------------------------------------------

    def _on_anchor_changed(self, _index=None):
        anchor = self._combo_anchor.currentData()
        note = _OFFSET_NOTE.get(anchor, '')
        self._desc_offset.setText(
            f'<span style="color:gray;font-style:italic;">{note}</span>'
        )

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, component: BeamRotationalHinge):
        """Fill widgets from an existing BeamRotationalHinge (edit mode)."""
        if component is None:
            self._on_anchor_changed()
            return

        self._edit_name.setText(str(component.name))

        for i, (val, _) in enumerate(_ANCHOR_OPTIONS):
            if val == component.anchor:
                self._combo_anchor.setCurrentIndex(i)
                break

        self._edit_offset.set_quantity(component.offset)

        for key in BeamRotationalHinge.DOF_KEYS:
            self._checks[key].setChecked(bool(component.dofs.get(key, False)))

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
            errors.append('Offset must be a length quantity (e.g. 0.1[m]).')
        elif float(offset_val.to_base_units().magnitude) < 0.0:
            errors.append('Offset must be \u2265 0.')

        dofs = {k: self._checks[k].isChecked() for k in BeamRotationalHinge.DOF_KEYS}
        if not any(dofs.values()):
            errors.append('At least one rotational DOF (Ry or Rz) must be active.')

        if errors:
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._validated = {
            'name':   name,
            'anchor': self._combo_anchor.currentData(),
            'offset': offset_val,
            'dofs':   dofs,
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def apply_to(self, component: BeamRotationalHinge):
        """Write validated data back to a BeamRotationalHinge instance."""
        d = self._validated
        component.name   = d['name']
        component.anchor = d['anchor']
        component.offset = d['offset']
        component.dofs   = d['dofs']
