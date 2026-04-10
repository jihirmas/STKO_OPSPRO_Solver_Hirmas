from PySide2 import QtCore, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Materials.asd_plastic_material import ASDPlasticMaterial


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


class ASDPlasticMaterialDialog(QtWidgets.QDialog):
    """
    QDialog for creating a new ASDPlasticMaterial or editing an existing one.

    Usage
    -----
    Create mode::

        dlg = ASDPlasticMaterialDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()

    Edit mode (pre-populate with an existing ASDPlasticMaterial)::

        dlg = ASDPlasticMaterialDialog(material=mat, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()
    """

    def __init__(self, material: ASDPlasticMaterial = None, parent=None, is_new=False):
        super().__init__(parent)

        self._material = material
        self._is_new = is_new
        self._setup_ui()
        self._populate(material)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New ASD Plastic Material' if self._is_new else 'Edit ASD Plastic Material'
        self.setWindowTitle(title)
        self.setMinimumWidth(600)

        ureg = ParameterManager._unit_registry
        _default_E   = 30e9   * ureg.Pa
        _default_nu  = 0.3    * ureg.dimensionless
        _default_rho = 2400.0 * ureg('kg/m^3')
        _default_sigma_y = 250e6 * ureg.Pa

        # Main grid layout
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 120)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 1)

        def _lbl(text):
            l = QtWidgets.QLabel(text)
            l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            return l

        def _desc(text):
            l = QtWidgets.QLabel(text)
            l.setStyleSheet('color: gray; font-style: italic;')
            return l

        row = 0

        # ---- Name ----
        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('e.g. ASD Plastic 1')
        grid.addWidget(_lbl('Name:'), row, 0)
        grid.addWidget(self._edit_name, row, 1, 1, 2)
        row += 1

        # ---- Material Type Section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Material Configuration</b>'), row, 0, 1, 3)
        row += 1

        # Elasticity type
        self._combo_elasticity = QtWidgets.QComboBox()
        self._combo_elasticity.addItems(['LinearIsotropic3D', 'DuncanChang'])
        grid.addWidget(_lbl('Elasticity:'), row, 0)
        grid.addWidget(self._combo_elasticity, row, 1)
        grid.addWidget(_desc('Type of elasticity model'), row, 2)
        row += 1

        # Yield function
        self._combo_yield = QtWidgets.QComboBox()
        self._combo_yield.addItems(['VonMises', 'DruckerPrager', 'MohrCoulomb', 'TensionCutoff'])
        grid.addWidget(_lbl('Yield Function:'), row, 0)
        grid.addWidget(self._combo_yield, row, 1)
        grid.addWidget(_desc('Yield criterion'), row, 2)
        row += 1

        # Plastic flow
        self._combo_flow = QtWidgets.QComboBox()
        self._combo_flow.addItems(['VonMises', 'DruckerPrager', 'MohrCoulomb', 'ConstantDilatancy'])
        grid.addWidget(_lbl('Plastic Flow:'), row, 0)
        grid.addWidget(self._combo_flow, row, 1)
        grid.addWidget(_desc('Flow rule'), row, 2)
        row += 1

        # ---- Elastic Properties Section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Elastic Properties</b>'), row, 0, 1, 3)
        row += 1

        self._edit_E = ExpressionLineEdit(default_value=_default_E)
        grid.addWidget(_lbl('E:'), row, 0)
        grid.addWidget(self._edit_E, row, 1)
        grid.addWidget(_desc("Young's modulus"), row, 2)
        row += 1

        self._edit_nu = ExpressionLineEdit(default_value=_default_nu)
        grid.addWidget(_lbl('\u03bd:'), row, 0)  # ν
        grid.addWidget(self._edit_nu, row, 1)
        grid.addWidget(_desc("Poisson's ratio"), row, 2)
        row += 1

        self._edit_rho = ExpressionLineEdit(default_value=_default_rho)
        grid.addWidget(_lbl('\u03c1:'), row, 0)  # ρ
        grid.addWidget(self._edit_rho, row, 1)
        grid.addWidget(_desc('Mass density'), row, 2)
        row += 1

        # ---- Yield Stress (for VonMises) ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Yield Properties</b>'), row, 0, 1, 3)
        row += 1

        self._edit_sigma_y = ExpressionLineEdit(default_value=_default_sigma_y)
        grid.addWidget(_lbl('Yield Stress:'), row, 0)
        grid.addWidget(self._edit_sigma_y, row, 1)
        grid.addWidget(_desc('Initial yield stress (Von Mises)'), row, 2)
        row += 1

        # Mohr-Coulomb parameters
        self._lbl_MC_c = _lbl('Cohesion (c):')
        self._edit_MC_c = ExpressionLineEdit(default_value=ParameterManager.to_internal_like(0e3 * ureg.Pa))
        self._desc_MC_c = _desc('Mohr-Coulomb cohesion')
        grid.addWidget(self._lbl_MC_c, row, 0)
        grid.addWidget(self._edit_MC_c, row, 1)
        grid.addWidget(self._desc_MC_c, row, 2)
        row += 1

        self._lbl_MC_phi = _lbl('Friction angle (\u03c6):')
        self._edit_MC_phi = ExpressionLineEdit(default_value=30.0 * ureg.dimensionless)
        self._desc_MC_phi = _desc('Mohr-Coulomb friction angle [degrees]')
        grid.addWidget(self._lbl_MC_phi, row, 0)
        grid.addWidget(self._edit_MC_phi, row, 1)
        grid.addWidget(self._desc_MC_phi, row, 2)
        row += 1

        # ---- Hardening Section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Hardening Laws</b>'), row, 0, 1, 3)
        row += 1

        # Scalar hardening
        self._combo_hardening_scalar = QtWidgets.QComboBox()
        self._combo_hardening_scalar.addItems(['NullHardeningScalarFunction', 'ScalarLinearHardeningFunction'])
        grid.addWidget(_lbl('Scalar Hardening:'), row, 0)
        grid.addWidget(self._combo_hardening_scalar, row, 1)
        grid.addWidget(_desc('Scalar hardening law'), row, 2)
        row += 1

        # Tensor hardening
        self._combo_hardening_tensor = QtWidgets.QComboBox()
        self._combo_hardening_tensor.addItems(['NullHardeningTensorFunction', 'TensorLinearHardeningFunction', 'ArmstrongFrederickHardeningFunction'])
        grid.addWidget(_lbl('Tensor Hardening:'), row, 0)
        grid.addWidget(self._combo_hardening_tensor, row, 1)
        grid.addWidget(_desc('Tensor hardening law'), row, 2)
        row += 1

        # ---- Integration Options Section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Integration Options</b>'), row, 0, 1, 3)
        row += 1

        # Integration method
        self._combo_integration = QtWidgets.QComboBox()
        self._combo_integration.addItems([
            'Runge_Kutta_45_Error_Control',
            'Forward_Euler',
            'Backward_Euler',
            'Modified_Euler_Error_Control'
        ])
        grid.addWidget(_lbl('Integration:'), row, 0)
        grid.addWidget(self._combo_integration, row, 1)
        grid.addWidget(_desc('Integration method'), row, 2)
        row += 1

        # Return to yield surface
        self._combo_return_ys = QtWidgets.QComboBox()
        self._combo_return_ys.addItems(['Disabled', 'One_Step_Return', 'Iterative_Return'])
        self._combo_return_ys.setCurrentIndex(1)  # Default: One_Step_Return
        grid.addWidget(_lbl('Return to YS:'), row, 0)
        grid.addWidget(self._combo_return_ys, row, 1)
        grid.addWidget(_desc('Return to yield surface algorithm'), row, 2)
        row += 1

        # Tangent type
        self._combo_tangent = QtWidgets.QComboBox()
        self._combo_tangent.addItems(['Elastic', 'Continuum', 'Secant'])
        grid.addWidget(_lbl('Tangent Type:'), row, 0)
        grid.addWidget(self._combo_tangent, row, 1)
        grid.addWidget(_desc('Tangent stiffness type'), row, 2)
        row += 1

        # Absolute tolerance
        self._edit_f_tol = ExpressionLineEdit(default_value=1.0e-6 * ureg.dimensionless)
        grid.addWidget(_lbl('f_tol:'), row, 0)
        grid.addWidget(self._edit_f_tol, row, 1)
        grid.addWidget(_desc('Yield function absolute tolerance'), row, 2)
        row += 1

        # Max iterations
        self._spin_max_iter = QtWidgets.QSpinBox()
        self._spin_max_iter.setMinimum(1)
        self._spin_max_iter.setMaximum(1000)
        self._spin_max_iter.setValue(100)
        grid.addWidget(_lbl('Max Iterations:'), row, 0)
        grid.addWidget(self._spin_max_iter, row, 1)
        grid.addWidget(_desc('Maximum number of iterations'), row, 2)
        row += 1

        # ---- Vertical spacer ----
        grid.setRowStretch(row, 1)

        # ---- Button box ----
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal
        )
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        # ---- Main layout ----
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(grid)
        main_layout.addSpacing(4)
        main_layout.addWidget(_hline())
        main_layout.addWidget(btn_box)

    # ------------------------------------------------------------------
    # Populate from existing material
    # ------------------------------------------------------------------

    def _populate(self, material: ASDPlasticMaterial):
        """Fill widgets from an existing ASDPlasticMaterial instance."""
        if material is None:
            return
        self._edit_name.setText(str(material.name))
        self._combo_elasticity.setCurrentText(material.elasticity_type)
        self._combo_yield.setCurrentText(material.yield_function)
        self._combo_flow.setCurrentText(material.plastic_flow)
        self._combo_hardening_scalar.setCurrentText(material.hardening_scalar)
        self._combo_hardening_tensor.setCurrentText(material.hardening_tensor)
        self._combo_integration.setCurrentText(material.integration_method)
        self._combo_return_ys.setCurrentText(material.return_to_yield_surface)
        self._combo_tangent.setCurrentText(material.tangent_type)
        
        self._edit_E.set_quantity(material.E)
        self._edit_nu.set_quantity(material.nu)
        self._edit_rho.set_quantity(material.rho)
        self._edit_sigma_y.set_quantity(material.VonMises_YieldStress)
        self._edit_MC_c.set_quantity(material.MC_c)
        self._edit_MC_phi.set_quantity(material.MC_phi)
        self._edit_f_tol.set_quantity(material.f_absolute_tol)
        
        self._spin_max_iter.setValue(int(material.n_max_iterations.magnitude))

    # ------------------------------------------------------------------
    # Validation & acceptance
    # ------------------------------------------------------------------

    def _on_accepted(self):
        errors = []

        # ---- Name ----
        name = self._edit_name.text().strip()
        if not name:
            errors.append('Name must not be empty.')

        # ---- Validate E ----
        E_val = self._edit_E.value
        E_err = self._edit_E.error
        if E_err:
            errors.append(f'E: {E_err}')
        elif E_val.dimensionality != self._edit_E.expected_dimensionality:
            errors.append('E must be a stress/pressure quantity (e.g. 30[GPa]).')
        elif E_val.to_base_units().magnitude <= 0.0:
            errors.append('E must be positive.')

        # ---- Validate nu ----
        nu_val = self._edit_nu.value
        nu_err = self._edit_nu.error
        if nu_err:
            errors.append(f'\u03bd: {nu_err}')
        elif nu_val.dimensionality:
            errors.append('\u03bd must be dimensionless.')
        else:
            nu_mag = float(nu_val.magnitude)
            if not (0.0 <= nu_mag < 0.5):
                errors.append('\u03bd must be in [0, 0.5).')

        # ---- Validate rho ----
        rho_val = self._edit_rho.value
        rho_err = self._edit_rho.error
        if rho_err:
            errors.append(f'\u03c1: {rho_err}')
        elif rho_val.dimensionality != self._edit_rho.expected_dimensionality:
            errors.append('\u03c1 must be a mass-density quantity.')
        elif rho_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03c1 must be positive.')

        # ---- Validate sigma_y ----
        sigma_y_val = self._edit_sigma_y.value
        sigma_y_err = self._edit_sigma_y.error
        if sigma_y_err:
            errors.append(f'Yield stress: {sigma_y_err}')
        elif sigma_y_val.dimensionality != self._edit_sigma_y.expected_dimensionality:
            errors.append('Yield stress must be a stress quantity.')

        if errors:
            QtWidgets.QMessageBox.critical(self, 'Validation Error', '\n'.join(errors))
            return

        # Store validated data
        self._validated_data = {
            'name': name,
            'elasticity_type': self._combo_elasticity.currentText(),
            'yield_function': self._combo_yield.currentText(),
            'plastic_flow': self._combo_flow.currentText(),
            'hardening_scalar': self._combo_hardening_scalar.currentText(),
            'hardening_tensor': self._combo_hardening_tensor.currentText(),
            'integration_method': self._combo_integration.currentText(),
            'return_to_yield_surface': self._combo_return_ys.currentText(),
            'tangent_type': self._combo_tangent.currentText(),
            'E': self._edit_E.value,
            'nu': self._edit_nu.value,
            'rho': self._edit_rho.value,
            'VonMises_YieldStress': self._edit_sigma_y.value,
            'MC_c': self._edit_MC_c.value,
            'MC_phi': self._edit_MC_phi.value,
            'f_absolute_tol': self._edit_f_tol.value,
            'n_max_iterations': self._spin_max_iter.value(),
        }

        self.accept()

    # ------------------------------------------------------------------
    # Get validated data
    # ------------------------------------------------------------------

    def data(self):
        """
        Return the validated input as a plain dict.

        Call this only after the dialog has been accepted.
        """
        return getattr(self, '_validated_data', {})

    def apply_to(self, material: ASDPlasticMaterial):
        """Write the validated data directly onto *material*."""
        d = self.data()
        if not d:
            return
        material.name = d['name']
        material.elasticity_type = d['elasticity_type']
        material.yield_function = d['yield_function']
        material.plastic_flow = d['plastic_flow']
        material.hardening_scalar = d['hardening_scalar']
        material.hardening_tensor = d['hardening_tensor']
        material.integration_method = d['integration_method']
        material.return_to_yield_surface = d['return_to_yield_surface']
        material.tangent_type = d['tangent_type']
        material.E = d['E']
        material.nu = d['nu']
        material.rho = d['rho']
        material.VonMises_YieldStress = d['VonMises_YieldStress']
        material.MC_c = d['MC_c']
        material.MC_phi = d['MC_phi']
        material.f_absolute_tol = d['f_absolute_tol']
        material.n_max_iterations = d['n_max_iterations'] * ParameterManager._unit_registry.dimensionless

