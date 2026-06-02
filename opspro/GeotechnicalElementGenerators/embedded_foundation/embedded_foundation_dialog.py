from PyMpc import App
from PySide2 import QtCore, QtWidgets

from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator_dialog import (
    configure_floating_dialog,
    horizontal_line,
)
from opspro.GeotechnicalElementGenerators.preview import EmbeddedFoundationPreview
from opspro.GeotechnicalElementGenerators.embedded_foundation.embedded_foundation_form import (
    EmbeddedFoundationForm,
)


class EmbeddedFoundationDialog(QtWidgets.QDialog):
    def __init__(self, component=None, parent=None, is_new=False):
        super().__init__(parent)
        self._component = component
        self._is_new = is_new
        configure_floating_dialog(self)
        self._setup_ui()
        self.set_component(component)

    def _setup_ui(self):
        self.setWindowTitle('Embedded Foundation')
        self.setMinimumSize(760, 480)

        self._combo_dimension = QtWidgets.QComboBox()
        self._combo_dimension.addItems(DimensionMode.ALL)
        dim_layout = QtWidgets.QHBoxLayout()
        dim_layout.addWidget(QtWidgets.QLabel('Dimension:'))
        dim_layout.addWidget(self._combo_dimension)
        dim_layout.addStretch()

        self._form = EmbeddedFoundationForm()
        self._preview = EmbeddedFoundationPreview()
        self._summary = QtWidgets.QLabel()
        self._summary.setTextFormat(QtCore.Qt.RichText)
        self._summary.setWordWrap(True)

        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel('<b>PROPERTIES</b>'))
        left.addWidget(self._form, 1)

        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel('<b>PREVIEW</b>'))
        right.addWidget(self._preview, 1)
        right.addWidget(self._summary)

        content = QtWidgets.QHBoxLayout()
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
        errors = self._form.validation_errors()
        if errors:
            self._set_status(False, errors, [])
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._component.dimension_mode = DimensionMode.normalize(self._combo_dimension.currentText())
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
        self._preview.set_dimension_mode(mode)
        if self._component is not None:
            summary = self._component.describe_generated_entities()
            self._preview.set_summary(summary)
            self._summary.setText(
                '<b>Generated internally</b><br>'
                'Mechanical expansion: pending<br>'
                'Materials, constraints and interface strategy are not finalized.'
            )
        errors = self._form.validation_errors()
        warnings = ['Mechanical expansion is not implemented yet.']
        self._set_status(len(errors) == 0, errors, warnings)

    def _set_status(self, valid, errors, warnings):
        if valid:
            text = warnings[0] if warnings else 'Valid configuration'
            self._status.setStyleSheet('color: #7a5a00;')
        else:
            text = errors[0] if errors else 'Invalid configuration'
            self._status.setStyleSheet('color: #a12b2b;')
        self._status.setText(text)

