from PyMpc import App
from PySide2 import QtCore, QtWidgets

from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator_dialog import (
    configure_floating_dialog,
    horizontal_line,
)
from opspro.GeotechnicalElementGenerators.preview import SpringFoundationPreview
from opspro.GeotechnicalElementGenerators.spring_foundation.spring_foundation_form import (
    SpringFoundationForm,
)


class SpringFoundationDialog(QtWidgets.QDialog):
    def __init__(self, component=None, parent=None, is_new=False):
        super().__init__(parent)
        self._component = component
        self._is_new = is_new
        configure_floating_dialog(self)
        self._setup_ui()
        self.set_component(component)

    def _setup_ui(self):
        self.setWindowTitle('Spring Foundation')
        self.setMinimumSize(760, 480)

        self._combo_dimension = QtWidgets.QComboBox()
        self._combo_dimension.addItems(DimensionMode.ALL)
        dim_layout = QtWidgets.QHBoxLayout()
        dim_layout.addWidget(QtWidgets.QLabel('Dimension:'))
        dim_layout.addWidget(self._combo_dimension)
        dim_layout.addStretch()

        self._form = SpringFoundationForm()
        self._preview = SpringFoundationPreview()
        self._summary = QtWidgets.QLabel()
        self._summary.setTextFormat(QtCore.Qt.RichText)
        self._summary.setWordWrap(True)

        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel('<b>PREVIEW</b>'))
        right.addWidget(self._preview, 1)
        right.addWidget(self._summary)

        content = QtWidgets.QHBoxLayout()
        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel('<b>PROPERTIES</b>'))
        left.addWidget(self._form, 1)
        content.addLayout(left, 1)
        content.addLayout(right, 1)

        self._status = QtWidgets.QLabel()
        self._status.setWordWrap(True)
        self._btn_apply = QtWidgets.QPushButton('Apply')
        self._btn_close = QtWidgets.QPushButton('Close')
        footer = QtWidgets.QHBoxLayout()
        footer.addWidget(QtWidgets.QLabel('Status:'))
        footer.addWidget(self._status, 1)
        footer.addWidget(self._btn_apply)
        footer.addWidget(self._btn_close)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(dim_layout)
        layout.addWidget(horizontal_line())
        layout.addLayout(content, 1)
        layout.addWidget(horizontal_line())
        layout.addLayout(footer)

        self._combo_dimension.currentTextChanged.connect(self._on_dimension_changed)
        self._form.changed.connect(self._on_form_changed)
        self._btn_apply.clicked.connect(self._on_apply)
        self._btn_close.clicked.connect(self.close)

    def set_component(self, component):
        self._component = component
        if component is None:
            return
        idx = self._combo_dimension.findText(component.dimension_mode)
        if idx >= 0:
            self._combo_dimension.setCurrentIndex(idx)
        self._form.set_component(component)
        self._update_preview_and_status()

    def _on_dimension_changed(self, text):
        mode = DimensionMode.normalize(text)
        self._form.set_dimension_mode(mode)
        self._preview.set_dimension_mode(mode)
        self._update_preview_and_status()

    def _on_form_changed(self):
        self._update_preview_and_status()

    def _on_apply(self):
        if self._component is None:
            return
        mode = DimensionMode.normalize(self._combo_dimension.currentText())
        errors = self._form.validation_errors(mode)
        if errors:
            self._set_status(False, errors, [])
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._component.dimension_mode = mode
        self._form.apply_values(self._component)
        result = self._component.validate_configuration()
        self._set_status(result['valid'], result['errors'], result['warnings'])
        if not result['valid']:
            QtWidgets.QMessageBox.warning(self, 'Invalid configuration', '\n'.join(result['errors']))
            return

        self._component.changed = True
        doc = App.caeDocument()
        if doc is not None:
            doc.commitChanges()
            doc.dirty = True
        self._update_preview_and_status()

    def _update_preview_and_status(self):
        mode = DimensionMode.normalize(self._combo_dimension.currentText())
        if self._component is not None:
            summary = self._component.describe_generated_entities()
            if self._component.dimension_mode != mode:
                mats = 3 if mode == DimensionMode.TWO_D else 6
                summary = {
                    'auxiliary_nodes': 1,
                    'uniaxial_materials': mats,
                    'elements': [{'type': 'zeroLength', 'count': 1}],
                }
            self._preview.set_dimension_mode(mode)
            self._preview.set_summary(summary)
            self._summary.setText(self._summary_html(summary))
        errors = self._form.validation_errors(mode)
        self._set_status(len(errors) == 0, errors, [])

    def _summary_html(self, summary):
        elements = summary.get('elements', [])
        element_text = ', '.join(f"{e.get('count', 0)} {e.get('type', '')}" for e in elements)
        return (
            '<b>Generated internally</b><br>'
            f"Auxiliary nodes: {summary.get('auxiliary_nodes', 0)}<br>"
            f"Uniaxial materials: {summary.get('uniaxial_materials', 0)}<br>"
            f'Elements: {element_text}'
        )

    def _set_status(self, valid, errors, warnings):
        if valid:
            text = 'Valid configuration'
            if warnings:
                text += ' - ' + warnings[0]
            self._status.setStyleSheet('color: #1f6f3f;')
        else:
            text = errors[0] if errors else 'Invalid configuration'
            self._status.setStyleSheet('color: #a12b2b;')
        self._status.setText(text)

