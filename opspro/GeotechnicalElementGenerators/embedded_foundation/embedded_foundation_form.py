from PyMpc import App
from PySide2 import QtCore, QtWidgets

from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator_dialog import (
    header,
    horizontal_line,
    label,
    muted_label,
)


class EmbeddedFoundationForm(QtWidgets.QWidget):
    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._geometry_rows = {}
        self._setup_ui()

    def _setup_ui(self):
        ureg = ParameterManager._unit_registry
        grid = QtWidgets.QGridLayout(self)
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 108)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        row = 0

        grid.addWidget(header('General'), row, 0, 1, 3)
        row += 1
        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('Embedded Foundation')
        grid.addWidget(label('Name:'), row, 0)
        grid.addWidget(self._edit_name, row, 1, 1, 2)
        row += 1

        grid.addWidget(horizontal_line(), row, 0, 1, 3)
        row += 1
        grid.addWidget(header('Foundation material'), row, 0, 1, 3)
        row += 1
        self._combo_material = QtWidgets.QComboBox()
        grid.addWidget(label('Material:'), row, 0)
        grid.addWidget(self._combo_material, row, 1, 1, 2)
        row += 1

        grid.addWidget(horizontal_line(), row, 0, 1, 3)
        row += 1
        grid.addWidget(header('Interaction model'), row, 0, 1, 3)
        row += 1
        self._combo_interaction = QtWidgets.QComboBox()
        self._combo_interaction.addItem('Pending', 'pending')
        grid.addWidget(label('Model:'), row, 0)
        grid.addWidget(self._combo_interaction, row, 1, 1, 2)
        row += 1

        self._edit_mesh_tolerance = ExpressionLineEdit(default_value=0.001 * ureg.meter)
        self._edit_interface_tolerance = ExpressionLineEdit(default_value=0.001 * ureg.meter)
        row = self._add_expr_row(grid, row, 'Mesh tol.:', self._edit_mesh_tolerance, 'Geometry matching tolerance')
        row = self._add_expr_row(grid, row, 'Interface tol.:', self._edit_interface_tolerance, 'Interface matching tolerance')

        grid.addWidget(horizontal_line(), row, 0, 1, 3)
        row += 1
        grid.addWidget(header('Detected geometry'), row, 0, 1, 3)
        row += 1
        for key, text in (
            ('width', 'Width:'),
            ('depth', 'Depth:'),
            ('mesh_nodes', 'Mesh nodes:'),
            ('length', 'Length:'),
            ('volume', 'Volume:'),
            ('boundary_faces', 'Boundary faces:'),
        ):
            edit = QtWidgets.QLineEdit()
            edit.setReadOnly(True)
            edit.setText('not detected')
            row_label = label(text)
            grid.addWidget(row_label, row, 0)
            grid.addWidget(edit, row, 1, 1, 2)
            self._geometry_rows[key] = (row_label, edit)
            row += 1

        self._advanced = QtWidgets.QGroupBox('Advanced options')
        self._advanced.setCheckable(True)
        self._advanced.setChecked(False)
        adv_layout = QtWidgets.QVBoxLayout(self._advanced)
        adv_layout.addWidget(muted_label('Mechanical expansion is pending final specification.'))
        grid.addWidget(self._advanced, row, 0, 1, 3)
        row += 1
        grid.setRowStretch(row, 1)

        self._edit_name.textChanged.connect(self.changed)
        self._combo_material.currentIndexChanged.connect(self.changed)
        self._combo_interaction.currentIndexChanged.connect(self.changed)
        self._edit_mesh_tolerance.textChanged.connect(self.changed)
        self._edit_interface_tolerance.textChanged.connect(self.changed)

    def _add_expr_row(self, grid, row, text, edit, description):
        grid.addWidget(label(text), row, 0)
        grid.addWidget(edit, row, 1)
        grid.addWidget(muted_label(description), row, 2)
        return row + 1

    def set_dimension_mode(self, mode: str):
        mode = DimensionMode.normalize(mode)
        show_3d = mode == DimensionMode.THREE_D
        for key in ('length', 'volume', 'boundary_faces'):
            for widget in self._geometry_rows[key]:
                widget.setVisible(show_3d)

    def set_component(self, component):
        self._refresh_materials(component.foundation_material_id if component is not None else None)
        if component is None:
            return
        self._edit_name.setText(str(component.name))
        idx = self._combo_material.findData(component.foundation_material_id)
        if idx >= 0:
            self._combo_material.setCurrentIndex(idx)
        idx = self._combo_interaction.findData(component.interaction_model)
        if idx >= 0:
            self._combo_interaction.setCurrentIndex(idx)
        self._edit_mesh_tolerance.set_quantity(component.mesh_tolerance)
        self._edit_interface_tolerance.set_quantity(component.interface_tolerance)
        self._set_geometry_summary(getattr(component, 'geometry_summary', {}) or {})
        self.set_dimension_mode(component.dimension_mode)

    def read_values(self):
        return {
            'name': self._edit_name.text().strip(),
            'foundation_material_id': self._combo_material.currentData(),
            'interaction_model': self._combo_interaction.currentData(),
            'mesh_tolerance': self._edit_mesh_tolerance.value,
            'interface_tolerance': self._edit_interface_tolerance.value,
        }

    def apply_values(self, component):
        data = self.read_values()
        component.name = data['name']
        component.foundation_material_id = data['foundation_material_id']
        component.interaction_model = data['interaction_model']
        component.mesh_tolerance = data['mesh_tolerance']
        component.interface_tolerance = data['interface_tolerance']

    def validation_errors(self):
        errors = []
        if not self._edit_name.text().strip():
            errors.append('Name must not be empty.')
        if self._combo_material.currentData() is None:
            errors.append('Foundation material is required.')
        self._validate_expression(self._edit_mesh_tolerance, 'Mesh tolerance', errors)
        self._validate_expression(self._edit_interface_tolerance, 'Interface tolerance', errors)
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

    def _refresh_materials(self, selected_id):
        self._combo_material.blockSignals(True)
        self._combo_material.clear()
        self._combo_material.addItem('Select material', None)
        try:
            doc = App.caeDocument()
            groups = doc.pluginCaeComponents.groups()
            coll = groups[CAEComponentGroupUIDs.MATERIALS].collection
            for key in coll.keys():
                comp = coll[key]
                self._combo_material.addItem(f'{comp.name}  (id={int(comp.id)})', int(comp.id))
        except Exception:
            pass
        idx = self._combo_material.findData(selected_id)
        if idx >= 0:
            self._combo_material.setCurrentIndex(idx)
        self._combo_material.blockSignals(False)

    def _set_geometry_summary(self, summary):
        for key, widgets in self._geometry_rows.items():
            value = summary.get(key, 'not detected')
            widgets[1].setText(str(value))

