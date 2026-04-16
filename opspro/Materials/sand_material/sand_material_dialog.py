from PySide2 import QtCore, QtGui, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Materials.sand_material.sand_material import SandMaterial


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


class SandMaterialDialog(QtWidgets.QDialog):
    """
    QDialog for creating a new SandMaterial or editing an existing one.

    The dialog dynamically shows/hides parameters based on the material type selector
    (Mohr-Coulomb, Drucker-Prager, Von-Mises).

    Usage
    -----
    Create mode::

        dlg = SandMaterialDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()

    Edit mode (pre-populate with an existing SandMaterial)::

        dlg = SandMaterialDialog(material=mat, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()
    """

    def __init__(self, material: SandMaterial = None, parent=None, is_new=False):
        super().__init__(parent)

        self._material = material
        self._is_new = is_new
        self._visual_material = None
        self._setup_ui()
        self._populate(material)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New Sand Material' if self._is_new else 'Edit Sand Material'
        self.setWindowTitle(title)
        self.setMinimumWidth(600)

        ureg = ParameterManager._unit_registry
        # Default values
        _default_E = 50e6 * ureg.Pa
        _default_G = 20e6 * ureg.Pa
        _default_K = 40e6 * ureg.Pa
        _default_nu = 0.3 * ureg.dimensionless
        _default_gamma_unsat = 16000.0 * ureg('kg/m^3')
        _default_gamma_sat = 18000.0 * ureg('kg/m^3')
        _default_e_init = 0.8 * ureg.dimensionless
        _default_n_init = 0.444 * ureg.dimensionless
        _default_phi = 30.0 * ureg.degree
        _default_c = 10e3 * ureg.Pa
        _default_psi = 0.0 * ureg.degree
        _default_sigma_y = 100e3 * ureg.Pa
        _default_E_ref = 50e6 * ureg.Pa
        _default_P_ref = 100e3 * ureg.Pa
        _default_n_exp = 0.5 * ureg.dimensionless

        # 3-column grid: label | input | description
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 120)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 1)

        def _lbl(text):
            lbl = QtWidgets.QLabel(text)
            lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            return lbl

        def _desc(text):
            lbl = QtWidgets.QLabel(text)
            lbl.setStyleSheet("color: gray; font-size: 10px;")
            return lbl

        row = 0

        # ---- Name ----
        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('e.g. Dense Sand')
        self._btn_shader = QtWidgets.QPushButton('Shader\u2026')
        self._btn_shader.setToolTip('Edit visual shader\u2026')
        try:
            from PyMpc import FxMaterialEditor
        except Exception:
            self._btn_shader.setEnabled(False)
        self._btn_shader.clicked.connect(self._on_edit_shader)
        name_layout = QtWidgets.QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.addWidget(self._edit_name)
        name_layout.addWidget(self._btn_shader)
        grid.addWidget(_lbl('Name:'), row, 0)
        grid.addLayout(name_layout, row, 1, 1, 2)
        row += 1

        # ---- Elasticity section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Elasticity properties</b>'), row, 0, 1, 3)
        row += 1

        self._edit_E = ExpressionLineEdit(default_value=_default_E)
        grid.addWidget(_lbl('E:'), row, 0)
        grid.addWidget(self._edit_E, row, 1)
        grid.addWidget(_desc("Young's modulus"), row, 2)
        row += 1

        self._edit_G = ExpressionLineEdit(default_value=_default_G)
        grid.addWidget(_lbl('G:'), row, 0)
        grid.addWidget(self._edit_G, row, 1)
        grid.addWidget(_desc('Shear modulus'), row, 2)
        row += 1

        self._edit_K = ExpressionLineEdit(default_value=_default_K)
        grid.addWidget(_lbl('K:'), row, 0)
        grid.addWidget(self._edit_K, row, 1)
        grid.addWidget(_desc('Bulk modulus'), row, 2)
        row += 1

        self._edit_nu = ExpressionLineEdit(default_value=_default_nu)
        grid.addWidget(_lbl('\u03bd:'), row, 0)  # ν
        grid.addWidget(self._edit_nu, row, 1)
        grid.addWidget(_desc("Poisson's ratio"), row, 2)
        row += 1

        # ---- Unit weight and void parameters ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Unit weight & void ratio</b>'), row, 0, 1, 3)
        row += 1

        self._edit_gamma_unsat = ExpressionLineEdit(default_value=_default_gamma_unsat)
        grid.addWidget(_lbl('\u03b3_unsat:'), row, 0)  # γ_unsat
        grid.addWidget(self._edit_gamma_unsat, row, 1)
        grid.addWidget(_desc('Unsaturated unit weight'), row, 2)
        row += 1

        self._edit_gamma_sat = ExpressionLineEdit(default_value=_default_gamma_sat)
        grid.addWidget(_lbl('\u03b3_sat:'), row, 0)  # γ_sat
        grid.addWidget(self._edit_gamma_sat, row, 1)
        grid.addWidget(_desc('Saturated unit weight'), row, 2)
        row += 1

        self._edit_e_init = ExpressionLineEdit(default_value=_default_e_init)
        grid.addWidget(_lbl('e_init:'), row, 0)
        grid.addWidget(self._edit_e_init, row, 1)
        grid.addWidget(_desc('Initial void ratio'), row, 2)
        row += 1

        self._edit_n_init = ExpressionLineEdit(default_value=_default_n_init)
        grid.addWidget(_lbl('n_init:'), row, 0)
        grid.addWidget(self._edit_n_init, row, 1)
        grid.addWidget(_desc('Initial porosity'), row, 2)
        row += 1

        # ---- Material Type selector ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Constitutive model</b>'), row, 0, 1, 3)
        row += 1

        self._combo_type = QtWidgets.QComboBox()
        self._combo_type.addItems(SandMaterial.MATERIAL_TYPES)
        self._combo_type.currentTextChanged.connect(self._on_material_type_changed)
        grid.addWidget(_lbl('Type:'), row, 0)
        grid.addWidget(self._combo_type, row, 1, 1, 2)
        row += 1

        # ---- Drucker-Prager calibration mode (initially hidden) ----
        self._lbl_calibration = _lbl('Calibration:')
        self._combo_calibration = QtWidgets.QComboBox()
        self._combo_calibration.addItems(SandMaterial.CALIBRATION_MODES)
        self._desc_calibration = _desc('Calibration mode for Drucker-Prager')
        grid.addWidget(self._lbl_calibration, row, 0)
        grid.addWidget(self._combo_calibration, row, 1, 1, 2)
        self._row_calibration = row
        row += 1

        # ---- Strength parameters (shown for Mohr-Coulomb, Drucker-Prager, hidden for Von-Mises) ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        self._lbl_strength_section = QtWidgets.QLabel('<b>Strength parameters</b>')
        grid.addWidget(self._lbl_strength_section, row, 0, 1, 3)
        row += 1

        self._lbl_phi = _lbl('\u03c6:')  # φ
        self._edit_phi = ExpressionLineEdit(default_value=_default_phi)
        self._desc_phi = _desc('Friction angle')
        grid.addWidget(self._lbl_phi, row, 0)
        grid.addWidget(self._edit_phi, row, 1)
        grid.addWidget(self._desc_phi, row, 2)
        self._row_phi = row
        row += 1

        self._lbl_c = _lbl('c:')
        self._edit_c = ExpressionLineEdit(default_value=_default_c)
        self._desc_c = _desc('Cohesion')
        grid.addWidget(self._lbl_c, row, 0)
        grid.addWidget(self._edit_c, row, 1)
        grid.addWidget(self._desc_c, row, 2)
        self._row_c = row
        row += 1

        self._lbl_psi = _lbl('\u03a8:')  # Ψ
        self._edit_psi = ExpressionLineEdit(default_value=_default_psi)
        self._desc_psi = _desc('Dilatancy angle')
        grid.addWidget(self._lbl_psi, row, 0)
        grid.addWidget(self._edit_psi, row, 1)
        grid.addWidget(self._desc_psi, row, 2)
        self._row_psi = row
        row += 1

        # ---- Von-Mises specific: Yield stress (initially hidden) ----
        self._lbl_sigma_y = _lbl('\u03c3_y:')  # σ_y
        self._edit_sigma_y = ExpressionLineEdit(default_value=_default_sigma_y)
        self._desc_sigma_y = _desc('Yield stress (Von-Mises)')
        grid.addWidget(self._lbl_sigma_y, row, 0)
        grid.addWidget(self._edit_sigma_y, row, 1)
        grid.addWidget(self._desc_sigma_y, row, 2)
        self._row_sigma_y = row
        row += 1

        # ---- Nonlinear elasticity section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Nonlinear elasticity (optional)</b>'), row, 0, 1, 3)
        row += 1

        self._check_nonlinear = QtWidgets.QCheckBox()
        grid.addWidget(_lbl('Enable:'), row, 0)
        grid.addWidget(self._check_nonlinear, row, 1)
        grid.addWidget(_desc('Enable pressure-dependent elasticity'), row, 2)
        row += 1

        self._lbl_E_ref = _lbl('E_ref:')
        self._edit_E_ref = ExpressionLineEdit(default_value=_default_E_ref)
        self._desc_E_ref = _desc('Reference elasticity')
        grid.addWidget(self._lbl_E_ref, row, 0)
        grid.addWidget(self._edit_E_ref, row, 1)
        grid.addWidget(self._desc_E_ref, row, 2)
        self._row_E_ref = row
        row += 1

        self._lbl_P_ref = _lbl('P_ref:')
        self._edit_P_ref = ExpressionLineEdit(default_value=_default_P_ref)
        self._desc_P_ref = _desc('Reference pressure')
        grid.addWidget(self._lbl_P_ref, row, 0)
        grid.addWidget(self._edit_P_ref, row, 1)
        grid.addWidget(self._desc_P_ref, row, 2)
        self._row_P_ref = row
        row += 1

        self._lbl_n_exp = _lbl('n:')
        self._edit_n_exp = ExpressionLineEdit(default_value=_default_n_exp)
        self._desc_n_exp = _desc('Elasticity exponent')
        grid.addWidget(self._lbl_n_exp, row, 0)
        grid.addWidget(self._edit_n_exp, row, 1)
        grid.addWidget(self._desc_n_exp, row, 2)
        self._row_n_exp = row
        row += 1

        self._check_nonlinear.toggled.connect(self._on_nonlinear_toggled)

        # ---- vertical spacer ----
        grid.setRowStretch(row, 1)

        # ---- Button box ----
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accepted)
        button_box.rejected.connect(self.reject)

        main_layout = QtWidgets.QVBoxLayout()
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QtWidgets.QWidget()
        widget.setLayout(grid)
        scroll.setWidget(widget)
        main_layout.addWidget(scroll)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        # Initialize visibility
        self._on_material_type_changed(self._combo_type.currentText())
        self._on_nonlinear_toggled(False)

    # ------------------------------------------------------------------
    # Dynamic UI updates
    # ------------------------------------------------------------------

    def _on_material_type_changed(self, material_type: str):
        """Show/hide parameters based on material type."""
        if material_type == 'Mohr-Coulomb':
            self._lbl_calibration.hide()
            self._combo_calibration.hide()
            self._desc_calibration.hide()
            self._lbl_phi.show()
            self._edit_phi.show()
            self._desc_phi.show()
            self._lbl_c.show()
            self._edit_c.show()
            self._desc_c.show()
            self._lbl_psi.show()
            self._edit_psi.show()
            self._desc_psi.show()
            self._lbl_sigma_y.hide()
            self._edit_sigma_y.hide()
            self._desc_sigma_y.hide()

        elif material_type == 'Drucker-Prager':
            self._lbl_calibration.show()
            self._combo_calibration.show()
            self._desc_calibration.show()
            self._lbl_phi.show()
            self._edit_phi.show()
            self._desc_phi.show()
            self._lbl_c.show()
            self._edit_c.show()
            self._desc_c.show()
            self._lbl_psi.show()
            self._edit_psi.show()
            self._desc_psi.show()
            self._lbl_sigma_y.hide()
            self._edit_sigma_y.hide()
            self._desc_sigma_y.hide()

        elif material_type == 'Von-Mises':
            self._lbl_calibration.hide()
            self._combo_calibration.hide()
            self._desc_calibration.hide()
            self._lbl_phi.hide()
            self._edit_phi.hide()
            self._desc_phi.hide()
            self._lbl_c.hide()
            self._edit_c.hide()
            self._desc_c.hide()
            self._lbl_psi.hide()
            self._edit_psi.hide()
            self._desc_psi.hide()
            self._lbl_sigma_y.show()
            self._edit_sigma_y.show()
            self._desc_sigma_y.show()

    def _on_nonlinear_toggled(self, enabled: bool):
        """Show/hide nonlinear elasticity parameters."""
        self._lbl_E_ref.setEnabled(enabled)
        self._edit_E_ref.setEnabled(enabled)
        self._desc_E_ref.setEnabled(enabled)
        self._lbl_P_ref.setEnabled(enabled)
        self._edit_P_ref.setEnabled(enabled)
        self._desc_P_ref.setEnabled(enabled)
        self._lbl_n_exp.setEnabled(enabled)
        self._edit_n_exp.setEnabled(enabled)
        self._desc_n_exp.setEnabled(enabled)

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, material: SandMaterial):
        if material is None:
            return

        self._edit_name.setText(material.name)
        self._edit_E.setValue(material.E)
        self._edit_G.setValue(material.G)
        self._edit_K.setValue(material.K)
        self._edit_nu.setValue(material.nu)
        self._edit_gamma_unsat.setValue(material.gamma_unsat)
        self._edit_gamma_sat.setValue(material.gamma_sat)
        self._edit_e_init.setValue(material.e_init)
        self._edit_n_init.setValue(material.n_init)
        self._combo_type.setCurrentText(material.material_type)
        self._combo_calibration.setCurrentText(material.calibration_mode)
        self._edit_phi.setValue(material.phi)
        self._edit_c.setValue(material.c)
        self._edit_psi.setValue(material.psi)
        self._edit_sigma_y.setValue(material.sigma_y)
        self._check_nonlinear.setChecked(material.nonlinear_elasticity)
        self._edit_E_ref.setValue(material.E_ref)
        self._edit_P_ref.setValue(material.P_ref)
        self._edit_n_exp.setValue(material.n_exp)
        self._visual_material = material.visual_material

    # ------------------------------------------------------------------
    # Validation & acceptance
    # ------------------------------------------------------------------

    def _on_accepted(self):
        """Validate and accept dialog."""
        try:
            name = self._edit_name.text().strip()
            if not name:
                QtWidgets.QMessageBox.warning(self, 'Invalid input', 'Please enter a material name')
                return

            E = self._edit_E.evaluate()
            G = self._edit_G.evaluate()
            K = self._edit_K.evaluate()
            nu = self._edit_nu.evaluate()
            gamma_unsat = self._edit_gamma_unsat.evaluate()
            gamma_sat = self._edit_gamma_sat.evaluate()
            e_init = self._edit_e_init.evaluate()
            n_init = self._edit_n_init.evaluate()
            phi = self._edit_phi.evaluate()
            c = self._edit_c.evaluate()
            psi = self._edit_psi.evaluate()
            sigma_y = self._edit_sigma_y.evaluate()
            E_ref = self._edit_E_ref.evaluate()
            P_ref = self._edit_P_ref.evaluate()
            n_exp = self._edit_n_exp.evaluate()

            # Basic validation
            if E <= 0 or G <= 0 or K <= 0:
                QtWidgets.QMessageBox.warning(self, 'Invalid input', 'Elasticity parameters must be positive')
                return

            if gamma_unsat <= 0 or gamma_sat <= 0:
                QtWidgets.QMessageBox.warning(self, 'Invalid input', 'Unit weights must be positive')
                return

            if e_init < 0 or n_init <= 0 or n_init >= 1:
                QtWidgets.QMessageBox.warning(self, 'Invalid input', 'Void ratio and porosity out of valid range')
                return

            self.accept()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error in parameters: {str(e)}')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def data(self):
        """Return a dict of all field values (for create mode)."""
        return {
            'name': self._edit_name.text().strip(),
            'E': self._edit_E.evaluate(),
            'G': self._edit_G.evaluate(),
            'K': self._edit_K.evaluate(),
            'nu': self._edit_nu.evaluate(),
            'gamma_unsat': self._edit_gamma_unsat.evaluate(),
            'gamma_sat': self._edit_gamma_sat.evaluate(),
            'e_init': self._edit_e_init.evaluate(),
            'n_init': self._edit_n_init.evaluate(),
            'material_type': self._combo_type.currentText(),
            'calibration_mode': self._combo_calibration.currentText(),
            'phi': self._edit_phi.evaluate(),
            'c': self._edit_c.evaluate(),
            'psi': self._edit_psi.evaluate(),
            'sigma_y': self._edit_sigma_y.evaluate(),
            'nonlinear_elasticity': self._check_nonlinear.isChecked(),
            'E_ref': self._edit_E_ref.evaluate(),
            'P_ref': self._edit_P_ref.evaluate(),
            'n_exp': self._edit_n_exp.evaluate(),
            'visual_material': self._visual_material,
        }

    def apply_to(self, material: SandMaterial):
        """Apply dialog values to an existing material (for edit mode)."""
        material.name = self._edit_name.text().strip()
        material.E = self._edit_E.evaluate()
        material.G = self._edit_G.evaluate()
        material.K = self._edit_K.evaluate()
        material.nu = self._edit_nu.evaluate()
        material.gamma_unsat = self._edit_gamma_unsat.evaluate()
        material.gamma_sat = self._edit_gamma_sat.evaluate()
        material.e_init = self._edit_e_init.evaluate()
        material.n_init = self._edit_n_init.evaluate()
        material.material_type = self._combo_type.currentText()
        material.calibration_mode = self._combo_calibration.currentText()
        material.phi = self._edit_phi.evaluate()
        material.c = self._edit_c.evaluate()
        material.psi = self._edit_psi.evaluate()
        material.sigma_y = self._edit_sigma_y.evaluate()
        material.nonlinear_elasticity = self._check_nonlinear.isChecked()
        material.E_ref = self._edit_E_ref.evaluate()
        material.P_ref = self._edit_P_ref.evaluate()
        material.n_exp = self._edit_n_exp.evaluate()
        if self._visual_material is not None:
            material.visual_material = self._visual_material

    # ------------------------------------------------------------------
    # Shader editor
    # ------------------------------------------------------------------

    def _on_edit_shader(self):
        """Open shader editor dialog."""
        try:
            from PyMpc import FxMaterialEditor
            dlg = FxMaterialEditor(self._visual_material, self)
            if dlg.exec():
                self._visual_material = dlg.getMaterial()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', f'Cannot open shader editor: {str(e)}')
