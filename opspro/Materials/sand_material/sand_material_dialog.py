import pkgutil

from PySide2 import QtCore, QtGui, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Materials.sand_material.sand_material import SandMaterial
from opspro.Materials.sand_material.elasticity_properties_formulas import compute_elastic_constants


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


class SandMaterialDialog(QtWidgets.QDialog):
    """
    QDialog for creating a new SandMaterial or editing an existing one.

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

        self._material       = material
        self._is_new         = is_new
        self._visual_material = None
        self._setup_ui()
        self._populate(material)
        self._on_material_type_changed(self._combo_type.currentText())
        self._update_elasticity_disabled_states()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New Sand Material' if self._is_new else 'Edit Sand Material'
        self.setWindowTitle(title)
        self.setMinimumWidth(750)
        self.setMinimumHeight(650)

        ureg = ParameterManager._unit_registry
        _default_E           = 50e6    * ureg.Pa
        _default_G           = 20e6    * ureg.Pa
        _default_K           = 40e6    * ureg.Pa
        _default_nu          = 0.3     * ureg.dimensionless
        _default_gamma_unsat = 16000.0 * ureg('kg/m^3')
        _default_gamma_sat   = 18000.0 * ureg('kg/m^3')
        _default_e_init      = 0.8     * ureg.dimensionless
        _default_n_init      = 0.444   * ureg.dimensionless
        _default_phi         = 30.0    * ureg.degree
        _default_c           = 10e3    * ureg.Pa
        _default_psi         = 0.0     * ureg.degree
        _default_sigma_y     = 100e3   * ureg.Pa
        _default_E_ref       = 50e6    * ureg.Pa
        _default_P_ref       = 100e3   * ureg.Pa
        _default_n_exp       = 0.5     * ureg.dimensionless

        # 3-column grid: label | input | description
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 100)
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
        self._edit_name.setPlaceholderText('e.g. Dense Sand')
        self._btn_shader = QtWidgets.QPushButton('Shader\u2026')
        self._btn_shader.setToolTip('Edit visual shader\u2026')
        try:
            icon_data = pkgutil.get_data('opspro', 'assets/images/shader.ico')
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(icon_data)
            self._btn_shader.setIcon(QtGui.QIcon(pixmap))
        except Exception:
            pass
        self._btn_shader.clicked.connect(self._on_edit_shader)
        name_layout = QtWidgets.QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.addWidget(self._edit_name)
        name_layout.addWidget(self._btn_shader)
        grid.addWidget(_lbl('Name:'), row, 0)
        grid.addLayout(name_layout, row, 1, 1, 2)
        row += 1

        # ---- Constitutive model images (one per type, hidden/shown dynamically) ----
        # Mohr-Coulomb image
        self._img_mohr_coulomb = QtWidgets.QLabel()
        self._img_mohr_coulomb.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._img_mohr_coulomb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self._img_mohr_coulomb.setStyleSheet('background: white;')
        try:
            image_data = pkgutil.get_data('opspro', 'assets/images/sand_material_mohr_coulomb.png')
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data)
            self._img_mohr_coulomb.setPixmap(pixmap)
        except Exception:
            pass
        grid.addWidget(self._img_mohr_coulomb, row, 0, 1, 3)
        row += 1

        # Drucker-Prager image
        self._img_drucker_prager = QtWidgets.QLabel()
        self._img_drucker_prager.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._img_drucker_prager.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self._img_drucker_prager.setStyleSheet('background: white;')
        try:
            image_data = pkgutil.get_data('opspro', 'assets/images/sand_material_drucker_prager.png')
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data)
            self._img_drucker_prager.setPixmap(pixmap)
        except Exception:
            pass
        grid.addWidget(self._img_drucker_prager, row, 0, 1, 3)
        row += 1

        # Von-Mises image
        self._img_von_mises = QtWidgets.QLabel()
        self._img_von_mises.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._img_von_mises.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self._img_von_mises.setStyleSheet('background: white;')
        try:
            image_data = pkgutil.get_data('opspro', 'assets/images/sand_material_von_mises.png')
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data)
            self._img_von_mises.setPixmap(pixmap)
        except Exception:
            pass
        grid.addWidget(self._img_von_mises, row, 0, 1, 3)
        row += 1

        # Initially hide all images (will be shown by _on_material_type_changed)
        self._img_mohr_coulomb.setVisible(False)
        self._img_drucker_prager.setVisible(False)
        self._img_von_mises.setVisible(False)

        # ---- Elasticity section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Elasticity properties</b>'), row, 0, 1, 3)
        row += 1

        # ---- Elasticity pair selector ----
        # Define all possible pairs of known elastic constants and their compute options
        self._elasticity_pairs = [
            ('E, ν (compute G, K)', {'known': ['E', 'nu'], 'computed': ['G', 'K'], 'func': lambda E, nu: compute_elastic_constants(E=E, v=nu)}),
            ('E, G (compute ν, K)', {'known': ['E', 'G'], 'computed': ['nu', 'K'], 'func': lambda E, G: compute_elastic_constants(E=E, G=G)}),
            ('E, K (compute ν, G)', {'known': ['E', 'K'], 'computed': ['nu', 'G'], 'func': lambda E, K: compute_elastic_constants(E=E, K=K)}),
            ('G, ν (compute E, K)', {'known': ['G', 'nu'], 'computed': ['E', 'K'], 'func': lambda G, nu: compute_elastic_constants(G=G, v=nu)}),
            ('G, K (compute E, ν)', {'known': ['G', 'K'], 'computed': ['E', 'nu'], 'func': lambda G, K: compute_elastic_constants(G=G, K=K)}),
            ('K, ν (compute E, G)', {'known': ['K', 'nu'], 'computed': ['E', 'G'], 'func': lambda K, nu: compute_elastic_constants(K=K, v=nu)}),
        ]

        self._combo_elasticity_pair = QtWidgets.QComboBox()
        self._combo_elasticity_pair.addItems([pair[0] for pair in self._elasticity_pairs])
        self._combo_elasticity_pair.setCurrentIndex(0)  # Default: E, ν
        self._combo_elasticity_pair.currentIndexChanged.connect(self._on_elasticity_pair_changed)
        grid.addWidget(_lbl('Known values:'), row, 0)
        grid.addWidget(self._combo_elasticity_pair, row, 1)
        grid.addWidget(_desc('Select which two elastic constants are known; others will be computed automatically'), row, 2)
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

        # Connect signals to auto-compute missing values
        self._edit_E.textChanged.connect(self._on_elasticity_value_changed)
        self._edit_G.textChanged.connect(self._on_elasticity_value_changed)
        self._edit_K.textChanged.connect(self._on_elasticity_value_changed)
        self._edit_nu.textChanged.connect(self._on_elasticity_value_changed)
        
        # Track disabled state for E due to elasticity pair selection (separate from nonlinear)
        self._E_disabled_by_elasticity = False

        # ---- Unit weight and void ratio section ----
        # ---- Unit weight section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Unit weight</b>'), row, 0, 1, 3)
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

        # ---- Void ratio section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Void ratio</b>'), row, 0, 1, 3)
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

        # ---- Material type section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Non-linear properties</b>'), row, 0, 1, 3)
        row += 1

        self._combo_type = QtWidgets.QComboBox()
        self._combo_type.addItems(SandMaterial.MATERIAL_TYPES)
        self._combo_type.currentTextChanged.connect(self._on_material_type_changed)
        grid.addWidget(_lbl('Type:'), row, 0)
        grid.addWidget(self._combo_type, row, 1)
        grid.addWidget(_desc('Presets'), row, 2)
        row += 1

        # ---- Drucker-Prager calibration mode ----
        self._lbl_calibration = _lbl('Calibration:')
        self._combo_calibration = QtWidgets.QComboBox()
        self._combo_calibration.addItems(SandMaterial.CALIBRATION_MODES)
        self._desc_calibration = _desc('Calibration mode for Drucker-Prager')
        grid.addWidget(self._lbl_calibration, row, 0)
        grid.addWidget(self._combo_calibration, row, 1)
        grid.addWidget(self._desc_calibration, row, 2)
        row += 1

        # ---- Strength parameters section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Strength parameters</b>'), row, 0, 1, 3)
        row += 1

        self._lbl_sigma_y = _lbl('\u03c3_y:')   # σ_y
        self._edit_sigma_y = ExpressionLineEdit(default_value=_default_sigma_y)
        self._desc_sigma_y = _desc('Yield stress (Von-Mises)')
        grid.addWidget(self._lbl_sigma_y, row, 0)
        grid.addWidget(self._edit_sigma_y, row, 1)
        grid.addWidget(self._desc_sigma_y, row, 2)
        row += 1

        self._lbl_c = _lbl('c:')
        self._edit_c = ExpressionLineEdit(default_value=_default_c)
        self._desc_c = _desc('Cohesion')
        grid.addWidget(self._lbl_c, row, 0)
        grid.addWidget(self._edit_c, row, 1)
        grid.addWidget(self._desc_c, row, 2)
        row += 1

        self._lbl_phi = _lbl('\u03c6:')   # φ
        self._edit_phi = ExpressionLineEdit(default_value=_default_phi)
        self._desc_phi = _desc('Friction angle')
        grid.addWidget(self._lbl_phi, row, 0)
        grid.addWidget(self._edit_phi, row, 1)
        grid.addWidget(self._desc_phi, row, 2)
        row += 1

        self._lbl_psi = _lbl('\u03a8:')   # Ψ
        self._edit_psi = ExpressionLineEdit(default_value=_default_psi)
        self._desc_psi = _desc('Dilatancy angle')
        grid.addWidget(self._lbl_psi, row, 0)
        grid.addWidget(self._edit_psi, row, 1)
        grid.addWidget(self._desc_psi, row, 2)
        row += 1

        # ---- Nonlinear elasticity section ----
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Nonlinear elasticity (optional)</b>'), row, 0, 1, 3)
        row += 1

        self._check_nonlinear = QtWidgets.QCheckBox()
        self._desc_nonlinear = _desc('Enable pressure-dependent elasticity')
        grid.addWidget(_lbl('Enable:'), row, 0)
        grid.addWidget(self._check_nonlinear, row, 1)
        grid.addWidget(self._desc_nonlinear, row, 2)
        row += 1

        self._lbl_E_ref = _lbl('E_ref:')
        self._edit_E_ref = ExpressionLineEdit(default_value=_default_E_ref)
        self._desc_E_ref = _desc('Reference elasticity')
        grid.addWidget(self._lbl_E_ref, row, 0)
        grid.addWidget(self._edit_E_ref, row, 1)
        grid.addWidget(self._desc_E_ref, row, 2)
        row += 1

        self._lbl_P_ref = _lbl('P_ref:')
        self._edit_P_ref = ExpressionLineEdit(default_value=_default_P_ref)
        self._desc_P_ref = _desc('Reference pressure')
        grid.addWidget(self._lbl_P_ref, row, 0)
        grid.addWidget(self._edit_P_ref, row, 1)
        grid.addWidget(self._desc_P_ref, row, 2)
        row += 1

        self._lbl_n_exp = _lbl('n:')
        self._edit_n_exp = ExpressionLineEdit(default_value=_default_n_exp)
        self._desc_n_exp = _desc('Elasticity exponent')
        grid.addWidget(self._lbl_n_exp, row, 0)
        grid.addWidget(self._edit_n_exp, row, 1)
        grid.addWidget(self._desc_n_exp, row, 2)
        row += 1

        self._check_nonlinear.toggled.connect(self._on_nonlinear_toggled)
        self._edit_E_ref.textChanged.connect(self._on_E_ref_changed)
        self._on_nonlinear_toggled(False)

        # ---- vertical spacer -----------------------------------------
        grid.setRowStretch(row, 1)

        # ---- Button box ----------------------------------------------
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal
        )
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        # ---- Main layout with scroll area ----------------------------
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_content.setLayout(grid)
        scroll.setWidget(scroll_content)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.addSpacing(4)
        main_layout.addWidget(_hline())
        main_layout.addWidget(btn_box)

    # ------------------------------------------------------------------
    # Material type toggle
    # ------------------------------------------------------------------

    def _update_image(self, material_type: str):
        """Show/hide images based on selected material type."""
        self._img_mohr_coulomb.setVisible(material_type == 'Mohr-Coulomb')
        self._img_drucker_prager.setVisible(material_type == 'Drucker-Prager')
        self._img_von_mises.setVisible(material_type == 'Von-Mises')

    def _on_material_type_changed(self, material_type: str):
        try:
            if material_type == 'Mohr-Coulomb':
                self._lbl_calibration.setVisible(False)
                self._combo_calibration.setVisible(False)
                self._desc_calibration.setVisible(False)
                self._lbl_phi.setVisible(True)
                self._edit_phi.setVisible(True)
                self._desc_phi.setVisible(True)
                self._lbl_c.setVisible(True)
                self._edit_c.setVisible(True)
                self._desc_c.setVisible(True)
                self._lbl_psi.setVisible(True)
                self._edit_psi.setVisible(True)
                self._desc_psi.setVisible(True)
                self._lbl_sigma_y.setVisible(False)
                self._edit_sigma_y.setVisible(False)
                self._desc_sigma_y.setVisible(False)

            elif material_type == 'Drucker-Prager':
                self._lbl_calibration.setVisible(True)
                self._combo_calibration.setVisible(True)
                self._desc_calibration.setVisible(True)
                self._lbl_phi.setVisible(True)
                self._edit_phi.setVisible(True)
                self._desc_phi.setVisible(True)
                self._lbl_c.setVisible(True)
                self._edit_c.setVisible(True)
                self._desc_c.setVisible(True)
                self._lbl_psi.setVisible(True)
                self._edit_psi.setVisible(True)
                self._desc_psi.setVisible(True)
                self._lbl_sigma_y.setVisible(False)
                self._edit_sigma_y.setVisible(False)
                self._desc_sigma_y.setVisible(False)

            elif material_type == 'Von-Mises':
                self._lbl_calibration.setVisible(False)
                self._combo_calibration.setVisible(False)
                self._desc_calibration.setVisible(False)
                self._lbl_phi.setVisible(False)
                self._edit_phi.setVisible(False)
                self._desc_phi.setVisible(False)
                self._lbl_c.setVisible(True)
                self._edit_c.setVisible(True)
                self._desc_c.setVisible(True)
                self._lbl_psi.setVisible(False)
                self._edit_psi.setVisible(False)
                self._desc_psi.setVisible(False)
                self._lbl_sigma_y.setVisible(True)
                self._edit_sigma_y.setVisible(True)
                self._desc_sigma_y.setVisible(True)
        except Exception as e:
            pass
        
        # Update displayed image based on material type
        self._update_image(material_type)
        
        # Ensure elasticity disabled states are updated
        self._update_elasticity_disabled_states()

    # ------------------------------------------------------------------
    # Nonlinear elasticity toggle
    # ------------------------------------------------------------------

    def _on_nonlinear_toggled(self, enabled: bool):
        # Enable/disable nonlinear elasticity fields
        for w in (
            self._lbl_E_ref, self._edit_E_ref, self._desc_E_ref,
            self._lbl_P_ref, self._edit_P_ref, self._desc_P_ref,
            self._lbl_n_exp, self._edit_n_exp, self._desc_n_exp,
        ):
            w.setEnabled(enabled)
        
        # When enabling nonlinear elasticity, disable E (unless it's already disabled by elasticity pair)
        if enabled:
            E_val = self._edit_E.value
            self._edit_E.setEnabled(False)
            # Copy E value to E_ref
            
            self._edit_E_ref.set_quantity(E_val)
        else:
            # When disabling nonlinear elasticity, restore E enabled state based on elasticity pair
            self._update_elasticity_disabled_states()

    # ------------------------------------------------------------------
    # E_ref synchronization
    # ------------------------------------------------------------------

    def _on_E_ref_changed(self):
        """When E_ref changes and nonlinear is enabled, update E display."""
        if self._check_nonlinear.isChecked():
            E_ref_val = self._edit_E_ref.value
            self._edit_E.set_quantity(E_ref_val)

    # ------------------------------------------------------------------
    # Elasticity properties auto-computation
    # ------------------------------------------------------------------

    def _on_elasticity_pair_changed(self, index: int):
        """Handle elasticity pair selection change."""
        self._update_elasticity_disabled_states()

    def _update_elasticity_disabled_states(self):
        """Update which elasticity fields are disabled based on current pair selection and nonlinear state."""
        try:
            # Get current elasticity pair configuration
            index = self._combo_elasticity_pair.currentIndex()
            if index < 0 or index >= len(self._elasticity_pairs):
                return

            pair_config = self._elasticity_pairs[index][1]
            known_fields = pair_config['known']
            computed_fields = pair_config['computed']

            # Check if nonlinear elasticity is enabled (which always disables E)
            nonlinear_enabled = self._check_nonlinear.isChecked()

            # Update disabled state for each field
            field_widgets = {
                'E': self._edit_E,
                'G': self._edit_G,
                'K': self._edit_K,
                'nu': self._edit_nu,
            }

            for field_name, widget in field_widgets.items():
                # If nonlinear is enabled and field is E, always disable
                if nonlinear_enabled and field_name == 'E':
                    widget.setEnabled(False)
                    self._E_disabled_by_elasticity = False
                # If field is computed, disable it
                elif field_name in computed_fields:
                    widget.setEnabled(False)
                    if field_name == 'E':
                        self._E_disabled_by_elasticity = True
                # Otherwise, enable it
                else:
                    widget.setEnabled(True)
                    if field_name == 'E':
                        self._E_disabled_by_elasticity = False

        except Exception as e:
            pass

    def _on_elasticity_value_changed(self):
        """Auto-compute missing elastic constants when a known value changes."""
        try:
            # Get current elasticity pair configuration
            index = self._combo_elasticity_pair.currentIndex()
            if index < 0 or index >= len(self._elasticity_pairs):
                return

            pair_config = self._elasticity_pairs[index][1]
            known_fields = pair_config['known']
            computed_fields = pair_config['computed']

            # Map field names to their widgets
            field_to_widget = {
                'E': self._edit_E,
                'G': self._edit_G,
                'K': self._edit_K,
                'nu': self._edit_nu,
            }

            # Get the unit registry
            ureg = ParameterManager._unit_registry

            # Check if all known values are valid and extract them
            known_values = {}
            known_units = {}  # Store original units for pressure quantities
            
            for field_name in known_fields:
                widget = field_to_widget[field_name]
                
                # Check for errors
                if widget.error:
                    return  # If any known field has error, don't compute
                
                # Get the value
                val = widget.value
                if not val or not hasattr(val, 'magnitude'):
                    return  # If value is not available, don't compute
                
                # Store original value and unit
                known_values[field_name] = val
                if field_name in ['E', 'G', 'K']:
                    known_units[field_name] = val.units

            # Now we have all known values, compute the missing ones using SI base units (Pa)
            try:
                # Build kwargs for compute_elastic_constants
                # Convert all pressure quantities to Pa for computation
                kwargs = {}
                for field_name, val in known_values.items():
                    if field_name == 'nu':
                        # Poisson's ratio is dimensionless, use magnitude directly
                        kwargs['v'] = float(val.magnitude)
                    else:
                        # Convert pressure to Pa
                        val_in_pa = val.to(ureg.Pa)
                        kwargs[field_name] = float(val_in_pa.magnitude)
                
                # Call the compute function - it will return all values in the same units as input
                result = compute_elastic_constants(**kwargs)

                # Update computed fields with the result
                # Block signals to avoid infinite recursion
                self._edit_E.blockSignals(True)
                self._edit_G.blockSignals(True)
                self._edit_K.blockSignals(True)
                self._edit_nu.blockSignals(True)

                for field_name in computed_fields:
                    widget = field_to_widget[field_name]
                    
                    # Get the computed value from result
                    # Result keys are: 'E', 'G', 'K', 'v' (not 'nu')
                    result_key = 'v' if field_name == 'nu' else field_name
                    
                    if result_key in result:
                        computed_val = result[result_key]
                        
                        # Create a quantity with the appropriate unit
                        if field_name == 'nu':
                            # Poisson's ratio is dimensionless
                            qtty = computed_val * ureg.dimensionless
                        else:
                            # Use the unit from a known pressure field if available
                            if known_units:
                                # Get the first known unit (they should all be the same)
                                unit = list(known_units.values())[0]
                            else:
                                # Fallback to Pa
                                unit = ureg.Pa
                            
                            # The result is in Pa, convert to the desired unit
                            qtty = (computed_val * ureg.Pa).to(unit)
                        
                        widget.set_quantity(qtty)

                # Reconnect signals
                self._edit_E.blockSignals(False)
                self._edit_G.blockSignals(False)
                self._edit_K.blockSignals(False)
                self._edit_nu.blockSignals(False)

            except Exception as compute_error:
                # If computation fails, just silently ignore
                # This can happen if the values don't make physical sense
                pass

        except Exception as e:
            pass

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, material: SandMaterial):
        """Fill widgets from an existing SandMaterial instance (edit mode)."""
        if material is None:
            return
        try:
            self._edit_name.setText(str(material.name))
            self._edit_E.set_quantity(material.E)
            self._edit_G.set_quantity(material.G)
            self._edit_K.set_quantity(material.K)
            self._edit_nu.set_quantity(material.nu)
            self._edit_gamma_unsat.set_quantity(material.gamma_unsat)
            self._edit_gamma_sat.set_quantity(material.gamma_sat)
            self._edit_e_init.set_quantity(material.e_init)
            self._edit_n_init.set_quantity(material.n_init)
            self._combo_type.setCurrentText(material.material_type)
            self._combo_calibration.setCurrentText(material.calibration_mode)
            self._edit_phi.set_quantity(material.phi)
            self._edit_c.set_quantity(material.c)
            self._edit_psi.set_quantity(material.psi)
            self._edit_sigma_y.set_quantity(material.sigma_y)
            self._check_nonlinear.setChecked(bool(material.nonlinear_elasticity))
            self._edit_E_ref.set_quantity(material.E_ref)
            self._edit_P_ref.set_quantity(material.P_ref)
            self._edit_n_exp.set_quantity(material.n_exp)
            self._visual_material = material.visual_material
        except Exception as e:
            pass

    # ------------------------------------------------------------------
    # Validation & acceptance
    # ------------------------------------------------------------------

    def _on_accepted(self):
        errors = []

        # ---- Name ----
        name = self._edit_name.text().strip()
        if not name:
            errors.append('Name must not be empty.')

        # ---- E ----
        E_val = self._edit_E.value
        E_err = self._edit_E.error
        if E_err:
            errors.append(f'E: {E_err}')
        elif E_val.dimensionality != self._edit_E.expected_dimensionality:
            errors.append('E must be a stress/pressure quantity (e.g. 50[MPa]).')
        elif E_val.to_base_units().magnitude <= 0.0:
            errors.append('E must be positive.')

        # ---- G ----
        G_val = self._edit_G.value
        G_err = self._edit_G.error
        if G_err:
            errors.append(f'G: {G_err}')
        elif G_val.dimensionality != self._edit_G.expected_dimensionality:
            errors.append('G must be a stress/pressure quantity (e.g. 20[MPa]).')
        elif G_val.to_base_units().magnitude <= 0.0:
            errors.append('G must be positive.')

        # ---- K ----
        K_val = self._edit_K.value
        K_err = self._edit_K.error
        if K_err:
            errors.append(f'K: {K_err}')
        elif K_val.dimensionality != self._edit_K.expected_dimensionality:
            errors.append('K must be a stress/pressure quantity (e.g. 40[MPa]).')
        elif K_val.to_base_units().magnitude <= 0.0:
            errors.append('K must be positive.')

        # ---- nu ----
        nu_val = self._edit_nu.value
        nu_err = self._edit_nu.error
        if nu_err:
            errors.append(f'\u03bd: {nu_err}')
        elif nu_val.dimensionality:
            errors.append('\u03bd must be dimensionless (e.g. 0.3).')
        else:
            nu_mag = float(nu_val.magnitude)
            if not (0.0 <= nu_mag < 0.5):
                errors.append('\u03bd must be in [0, 0.5).')

        # ---- gamma_unsat ----
        gamma_unsat_val = self._edit_gamma_unsat.value
        gamma_unsat_err = self._edit_gamma_unsat.error
        if gamma_unsat_err:
            errors.append(f'\u03b3_unsat: {gamma_unsat_err}')
        elif gamma_unsat_val.dimensionality != self._edit_gamma_unsat.expected_dimensionality:
            errors.append('\u03b3_unsat must be a mass-density quantity (e.g. 1600[kg/m^3]).')
        elif gamma_unsat_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03b3_unsat must be positive.')

        # ---- gamma_sat ----
        gamma_sat_val = self._edit_gamma_sat.value
        gamma_sat_err = self._edit_gamma_sat.error
        if gamma_sat_err:
            errors.append(f'\u03b3_sat: {gamma_sat_err}')
        elif gamma_sat_val.dimensionality != self._edit_gamma_sat.expected_dimensionality:
            errors.append('\u03b3_sat must be a mass-density quantity (e.g. 1800[kg/m^3]).')
        elif gamma_sat_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03b3_sat must be positive.')

        # ---- e_init ----
        e_init_val = self._edit_e_init.value
        e_init_err = self._edit_e_init.error
        if e_init_err:
            errors.append(f'e_init: {e_init_err}')
        elif e_init_val.dimensionality:
            errors.append('e_init must be dimensionless.')
        else:
            e_init_mag = float(e_init_val.magnitude)
            if e_init_mag < 0.0:
                errors.append('e_init must be \u2265 0.')

        # ---- n_init ----
        n_init_val = self._edit_n_init.value
        n_init_err = self._edit_n_init.error
        if n_init_err:
            errors.append(f'n_init: {n_init_err}')
        elif n_init_val.dimensionality:
            errors.append('n_init must be dimensionless.')
        else:
            n_init_mag = float(n_init_val.magnitude)
            if not (0.0 < n_init_mag < 1.0):
                errors.append('n_init must be in (0, 1).')

        # ---- phi ----
        phi_val = self._edit_phi.value
        phi_err = self._edit_phi.error
        if phi_err:
            errors.append(f'\u03c6: {phi_err}')
        else:
            try:
                phi_deg = float(phi_val.to('degree').magnitude)
                if not (0.0 <= phi_deg < 90.0):
                    errors.append('\u03c6 must be in [0\u00b0, 90\u00b0).')
            except Exception:
                errors.append('\u03c6 must be an angular quantity (e.g. 30[deg]).')

        # ---- c ----
        c_val = self._edit_c.value
        c_err = self._edit_c.error
        if c_err:
            errors.append(f'c: {c_err}')
        elif c_val.dimensionality != self._edit_c.expected_dimensionality:
            errors.append('c must be a stress/pressure quantity (e.g. 10[kPa]).')
        elif c_val.to_base_units().magnitude < 0.0:
            errors.append('c (cohesion) must be \u2265 0.')

        # ---- psi ----
        psi_val = self._edit_psi.value
        psi_err = self._edit_psi.error
        if psi_err:
            errors.append(f'\u03a8: {psi_err}')
        else:
            try:
                psi_deg = float(psi_val.to('degree').magnitude)
                if not (0.0 <= psi_deg < 90.0):
                    errors.append('\u03a8 must be in [0\u00b0, 90\u00b0).')
            except Exception:
                errors.append('\u03a8 must be an angular quantity (e.g. 0[deg]).')

        # ---- sigma_y ----
        sigma_y_val = self._edit_sigma_y.value
        sigma_y_err = self._edit_sigma_y.error
        if sigma_y_err:
            errors.append(f'\u03c3_y: {sigma_y_err}')
        elif sigma_y_val.dimensionality != self._edit_sigma_y.expected_dimensionality:
            errors.append('\u03c3_y must be a stress/pressure quantity (e.g. 100[kPa]).')
        elif sigma_y_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03c3_y must be positive.')

        # ---- Von-Mises validation: sigma_y and c are mutually exclusive ----
        material_type = self._combo_type.currentText()
        if material_type == 'Von-Mises':
            sigma_y_empty = not sigma_y_val or sigma_y_val.to_base_units().magnitude <= 0.0
            c_empty = not c_val or c_val.to_base_units().magnitude < 0.0
            if sigma_y_empty and c_empty:
                errors.append('Von-Mises: Either \u03c3_y (yield stress) or c (cohesion) must be provided.')
            elif not sigma_y_empty and not c_empty:
                errors.append('Von-Mises: \u03c3_y (yield stress) and c (cohesion) are mutually exclusive. Provide only one.')

        # ---- Nonlinear elasticity fields (if enabled) ----
        nonlinear = self._check_nonlinear.isChecked()
        if nonlinear:
            # ---- E_ref ----
            E_ref_val = self._edit_E_ref.value
            E_ref_err = self._edit_E_ref.error
            if E_ref_err:
                errors.append(f'E_ref: {E_ref_err}')
            elif E_ref_val.dimensionality != self._edit_E_ref.expected_dimensionality:
                errors.append('E_ref must be a stress/pressure quantity (e.g. 50[MPa]).')
            elif E_ref_val.to_base_units().magnitude <= 0.0:
                errors.append('E_ref must be positive.')

            # ---- P_ref ----
            P_ref_val = self._edit_P_ref.value
            P_ref_err = self._edit_P_ref.error
            if P_ref_err:
                errors.append(f'P_ref: {P_ref_err}')
            elif P_ref_val.dimensionality != self._edit_P_ref.expected_dimensionality:
                errors.append('P_ref must be a stress/pressure quantity (e.g. 100[kPa]).')
            elif P_ref_val.to_base_units().magnitude <= 0.0:
                errors.append('P_ref must be positive.')

            # ---- n_exp ----
            n_exp_val = self._edit_n_exp.value
            n_exp_err = self._edit_n_exp.error
            if n_exp_err:
                errors.append(f'n: {n_exp_err}')
            elif n_exp_val.dimensionality:
                errors.append('n must be dimensionless.')
            else:
                n_exp_mag = float(n_exp_val.magnitude)
                if n_exp_mag <= 0.0:
                    errors.append('n must be positive.')
        else:
            E_ref_val = self._edit_E_ref.value
            P_ref_val = self._edit_P_ref.value
            n_exp_val = self._edit_n_exp.value

        if errors:
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._validated_data = {
            'name':                name,
            'E':                   E_val,
            'G':                   G_val,
            'K':                   K_val,
            'nu':                  nu_val,
            'gamma_unsat':         gamma_unsat_val,
            'gamma_sat':           gamma_sat_val,
            'e_init':              e_init_val,
            'n_init':              n_init_val,
            'material_type':       self._combo_type.currentText(),
            'calibration_mode':    self._combo_calibration.currentText(),
            'phi':                 phi_val,
            'c':                   c_val,
            'psi':                 psi_val,
            'sigma_y':             sigma_y_val,
            'nonlinear_elasticity':nonlinear,
            'E_ref':               E_ref_val,
            'P_ref':               P_ref_val,
            'n_exp':               n_exp_val,
            'visual_material':     self._visual_material,
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def data(self):
        """
        Return the validated input as a plain dict.

        Call this only after the dialog has been accepted.
        """
        return getattr(self, '_validated_data', {})

    def apply_to(self, material: SandMaterial):
        """Write the validated data directly onto *material*."""
        d = self.data()
        if not d:
            return
        material.name                = d['name']
        material.E                   = d['E']
        material.G                   = d['G']
        material.K                   = d['K']
        material.nu                  = d['nu']
        material.gamma_unsat         = d['gamma_unsat']
        material.gamma_sat           = d['gamma_sat']
        material.e_init              = d['e_init']
        material.n_init              = d['n_init']
        material.material_type       = d['material_type']
        material.calibration_mode    = d['calibration_mode']
        material.phi                 = d['phi']
        material.c                   = d['c']
        material.psi                 = d['psi']
        material.sigma_y             = d['sigma_y']
        material.nonlinear_elasticity= d['nonlinear_elasticity']
        material.E_ref               = d['E_ref']
        material.P_ref               = d['P_ref']
        material.n_exp               = d['n_exp']
        material.visual_material     = d.get('visual_material', None)

    # ------------------------------------------------------------------
    # Shader editor
    # ------------------------------------------------------------------

    def _on_edit_shader(self):
        from opspro.utils.fx_material_utils import edit_fx_material
        result = edit_fx_material(self._visual_material)
        if result is not None:
            self._visual_material = result
