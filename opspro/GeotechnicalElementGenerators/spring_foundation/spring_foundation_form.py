from PySide2 import QtCore, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator_dialog import (
    header,
    horizontal_line,
    label,
    muted_label,
)


class SpringFoundationForm(QtWidgets.QWidget):
    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = {}
        self._setup_ui()

    def _setup_ui(self):
        ureg = ParameterManager._unit_registry
        grid = QtWidgets.QGridLayout(self)
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 70)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 1)
        row = 0

        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('Spring Foundation')
        grid.addWidget(header('General'), row, 0, 1, 3)
        row += 1
        grid.addWidget(label('Name:'), row, 0)
        grid.addWidget(self._edit_name, row, 1, 1, 2)
        row += 1

        grid.addWidget(horizontal_line(), row, 0, 1, 3)
        row += 1
        grid.addWidget(header('Foundation geometry'), row, 0, 1, 3)
        row += 1
        self._edit_B = ExpressionLineEdit(default_value=2.5 * ureg.meter)
        self._edit_H = ExpressionLineEdit(default_value=0.6 * ureg.meter)
        row = self._add_expr_row(grid, row, 'B:', self._edit_B, 'Preview width')
        row = self._add_expr_row(grid, row, 'H:', self._edit_H, 'Preview height')

        grid.addWidget(horizontal_line(), row, 0, 1, 3)
        row += 1
        grid.addWidget(header('Equivalent stiffness'), row, 0, 1, 3)
        row += 1
        default_k = 10.0 * ureg.kilonewton / ureg.meter
        default_kr = 30.0 * ureg.kilonewton * ureg.meter
        self._edits = {
            'Kx': ExpressionLineEdit(default_value=default_k),
            'Ky': ExpressionLineEdit(default_value=default_k),
            'Kz': ExpressionLineEdit(default_value=default_k),
            'Krx': ExpressionLineEdit(default_value=default_kr),
            'Kry': ExpressionLineEdit(default_value=default_kr),
            'Krz': ExpressionLineEdit(default_value=default_kr),
        }
        for key in ('Kx', 'Ky', 'Kz', 'Krx', 'Kry', 'Krz'):
            row = self._add_expr_row(grid, row, f'{key}:', self._edits[key], self._description_for(key), key)

        grid.addWidget(horizontal_line(), row, 0, 1, 3)
        row += 1
        self._advanced = QtWidgets.QGroupBox('Advanced options')
        self._advanced.setCheckable(True)
        self._advanced.setChecked(False)
        adv_layout = QtWidgets.QGridLayout(self._advanced)
        self._combo_orientation = QtWidgets.QComboBox()
        self._combo_orientation.addItem('Assigned entity local axes', 'assigned_entity')
        self._combo_orientation.addItem('Global axes', 'global_axes')
        self._check_global = QtWidgets.QCheckBox('Use global axes')
        adv_layout.addWidget(label('Orientation:'), 0, 0)
        adv_layout.addWidget(self._combo_orientation, 0, 1)
        adv_layout.addWidget(self._check_global, 1, 1)
        grid.addWidget(self._advanced, row, 0, 1, 3)
        row += 1
        grid.setRowStretch(row, 1)

        self._edit_name.textChanged.connect(self.changed)
        self._combo_orientation.currentIndexChanged.connect(self.changed)
        self._check_global.toggled.connect(self.changed)
        for edit in (self._edit_B, self._edit_H) + tuple(self._edits.values()):
            edit.textChanged.connect(self.changed)

    def _add_expr_row(self, grid, row, text, edit, description, key=None):
        row_label = label(text)
        row_desc = muted_label(description)
        grid.addWidget(row_label, row, 0)
        grid.addWidget(edit, row, 1)
        grid.addWidget(row_desc, row, 2)
        if key is not None:
            self._rows[key] = (row_label, edit, row_desc)
        return row + 1

    def _description_for(self, key):
        return {
            'Kx': 'Translation along local x',
            'Ky': 'Translation along local y',
            'Kz': 'Translation along local z',
            'Krx': 'Rotation about local x',
            'Kry': 'Rotation about local y',
            'Krz': 'Rotation about local z',
        }.get(key, '')

    def set_dimension_mode(self, mode: str):
        mode = DimensionMode.normalize(mode)
        visible = ('Kx', 'Ky', 'Krz') if mode == DimensionMode.TWO_D else ('Kx', 'Ky', 'Kz', 'Krx', 'Kry', 'Krz')
        for key, widgets in self._rows.items():
            show = key in visible
            for widget in widgets:
                widget.setVisible(show)

    def set_component(self, component):
        self._edit_name.setText(str(component.name))
        self._edit_B.set_quantity(component.B)
        self._edit_H.set_quantity(component.H)
        for key, edit in self._edits.items():
            edit.set_quantity(getattr(component, key))
        idx = self._combo_orientation.findData(component.orientation_mode)
        if idx >= 0:
            self._combo_orientation.setCurrentIndex(idx)
        self._check_global.setChecked(bool(component.use_global_axes))
        self.set_dimension_mode(component.dimension_mode)

    def read_values(self):
        return {
            'name': self._edit_name.text().strip(),
            'B': self._edit_B.value,
            'H': self._edit_H.value,
            'Kx': self._edits['Kx'].value,
            'Ky': self._edits['Ky'].value,
            'Kz': self._edits['Kz'].value,
            'Krx': self._edits['Krx'].value,
            'Kry': self._edits['Kry'].value,
            'Krz': self._edits['Krz'].value,
            'orientation_mode': self._combo_orientation.currentData(),
            'use_global_axes': self._check_global.isChecked(),
        }

    def apply_values(self, component):
        data = self.read_values()
        component.name = data['name']
        component.B = data['B']
        component.H = data['H']
        for key in ('Kx', 'Ky', 'Kz', 'Krx', 'Kry', 'Krz'):
            setattr(component, key, data[key])
        component.orientation_mode = data['orientation_mode']
        component.use_global_axes = data['use_global_axes']

    def validation_errors(self, mode: str):
        errors = []
        if not self._edit_name.text().strip():
            errors.append('Name must not be empty.')
        self._validate_expression(self._edit_B, 'B', errors)
        self._validate_expression(self._edit_H, 'H', errors)
        keys = ('Kx', 'Ky', 'Krz') if mode == DimensionMode.TWO_D else ('Kx', 'Ky', 'Kz', 'Krx', 'Kry', 'Krz')
        for key in keys:
            self._validate_expression(self._edits[key], key, errors)
        return errors

    def _validate_expression(self, edit, label_text, errors):
        if edit.error:
            errors.append(f'{label_text}: {edit.error}')
            return
        try:
            if float(edit.value.to_base_units().magnitude) <= 0.0:
                errors.append(f'{label_text} must be greater than zero.')
        except Exception as e:
            errors.append(f'{label_text}: invalid quantity ({e}).')

