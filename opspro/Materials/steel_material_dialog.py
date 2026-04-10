import pkgutil

from PySide2 import QtCore, QtGui, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Materials.steel_material import SteelMaterial
from opspro.Materials.presets import SteelPresetDialog

def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line

class SteelMaterialDialog(QtWidgets.QDialog):
    """
    QDialog for creating a new SteelMaterial or editing an existing one.

    Usage
    -----
    Create mode::

        dlg = SteelMaterialDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()

    Edit mode (pre-populate with an existing SteelMaterial)::

        dlg = SteelMaterialDialog(material=mat, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()
    """

    def __init__(self, material: SteelMaterial=None, parent=None, is_new=False):
        super().__init__(parent)

        self._material = material
        self._is_new             = is_new
        self._preset_standard    = ''
        self._preset_designation = ''
        self._visual_material    = None
        self._setup_ui()
        self._populate(material)
        self._update_standard_badge()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New Steel Material' if self._is_new else 'Edit Steel Material'
        self.setWindowTitle(title)
        self.setMinimumWidth(520)

        ureg = ParameterManager._unit_registry
        _default_E         = 210e9  * ureg.Pa
        _default_nu        = 0.3    * ureg.dimensionless
        _default_rho       = 7850.0 * ureg('kg/m^3')
        _default_sigma_y   = 355e6  * ureg.Pa
        _default_sigma_u   = 510e6  * ureg.Pa
        _default_epsilon_u = 0.15   * ureg.dimensionless

        # 3-column grid: label | input | description
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 80)   # label column
        grid.setColumnStretch(1, 0)         # input — natural size
        grid.setColumnStretch(2, 1)         # description — takes remaining space

        def _lbl(text):
            l = QtWidgets.QLabel(text)
            l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            return l

        def _desc(text):
            l = QtWidgets.QLabel(text)
            l.setStyleSheet('color: gray; font-style: italic;')
            return l

        row = 0

        # ---- Name ----------------------------------------------------
        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('e.g. S355')
        self._btn_shader = QtWidgets.QPushButton('Shader…')
        self._btn_shader.setToolTip('Edit visual shader…')
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

        # ---- Stress-strain diagram image ----------------------------
        img_label = QtWidgets.QLabel()
        img_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        img_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        img_label.setStyleSheet('background: white;')
        try:
            image_data = pkgutil.get_data('opspro', 'assets/images/steel_material_image_001.png')
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data)
            img_label.setPixmap(pixmap)
        except Exception:
            pass
        grid.addWidget(img_label, row, 0, 1, 3)
        row += 1

        # ---- Preset section ------------------------------------------
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Preset</b>'), row, 0, 1, 3)
        row += 1

        btn_preset = QtWidgets.QPushButton('Load preset\u2026')
        btn_preset.setToolTip('Pre-populate fields from a standard steel grade (ASTM, \u2026)')
        btn_preset.clicked.connect(self._on_load_preset)
        grid.addWidget(_lbl('Grade:'), row, 0)
        grid.addWidget(btn_preset, row, 1)
        row += 1

        self._lbl_standard_val = QtWidgets.QLabel()
        self._lbl_standard_val.setTextFormat(QtCore.Qt.RichText)
        grid.addWidget(_lbl('Standard:'), row, 0)
        grid.addWidget(self._lbl_standard_val, row, 1, 1, 2)
        row += 1

        # ---- Elastic section -----------------------------------------
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Elastic properties</b>'), row, 0, 1, 3)
        row += 1

        self._edit_E = ExpressionLineEdit(default_value=_default_E)
        grid.addWidget(_lbl('E:'), row, 0)
        grid.addWidget(self._edit_E, row, 1)
        grid.addWidget(_desc("Young's modulus"), row, 2)
        row += 1

        self._edit_nu = ExpressionLineEdit(default_value=_default_nu)
        grid.addWidget(_lbl('\u03bd:'), row, 0) # ν
        grid.addWidget(self._edit_nu, row, 1)
        grid.addWidget(_desc("Poisson's ratio"), row, 2)
        row += 1

        self._edit_rho = ExpressionLineEdit(default_value=_default_rho)
        grid.addWidget(_lbl('\u03c1:'), row, 0) # ρ
        grid.addWidget(self._edit_rho, row, 1)
        grid.addWidget(_desc('Mass density'), row, 2)
        row += 1

        # ---- Nonlinear section ---------------------------------------
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Nonlinear properties</b>'), row, 0, 1, 3)
        row += 1

        self._check_nonlinear = QtWidgets.QCheckBox()
        self._desc_nonlinear = _desc('Enable elasto-plastic behaviour')
        grid.addWidget(_lbl('Nonlinear:'), row, 0)
        grid.addWidget(self._check_nonlinear, row, 1)
        grid.addWidget(self._desc_nonlinear, row, 2)
        row += 1

        self._lbl_sigma_y = _lbl('\u03c3<sub>y</sub>:')
        self._edit_sigma_y = ExpressionLineEdit(default_value=_default_sigma_y)
        self._desc_sigma_y = _desc('Yield strength')
        grid.addWidget(self._lbl_sigma_y, row, 0)
        grid.addWidget(self._edit_sigma_y, row, 1)
        grid.addWidget(self._desc_sigma_y, row, 2)
        row += 1

        self._lbl_sigma_u = _lbl('\u03c3<sub>u</sub>:')
        self._edit_sigma_u = ExpressionLineEdit(default_value=_default_sigma_u)
        self._desc_sigma_u = _desc('Ultimate tensile strength')
        grid.addWidget(self._lbl_sigma_u, row, 0)
        grid.addWidget(self._edit_sigma_u, row, 1)
        grid.addWidget(self._desc_sigma_u, row, 2)
        row += 1

        self._lbl_epsilon_u = _lbl('\u03b5<sub>u</sub>:')
        self._edit_epsilon_u = ExpressionLineEdit(default_value=_default_epsilon_u)
        self._desc_epsilon_u = _desc('Ultimate strain')
        grid.addWidget(self._lbl_epsilon_u, row, 0)
        grid.addWidget(self._edit_epsilon_u, row, 1)
        grid.addWidget(self._desc_epsilon_u, row, 2)
        row += 1

        self._lbl_fracture = _lbl('Fracture:')
        self._check_fracture = QtWidgets.QCheckBox()
        self._desc_fracture = _desc('Stress/stiffness decay beyond \u03b5\u1d64')
        grid.addWidget(self._lbl_fracture, row, 0)
        grid.addWidget(self._check_fracture, row, 1)
        grid.addWidget(self._desc_fracture, row, 2)
        row += 1

        self._check_nonlinear.toggled.connect(self._on_nonlinear_toggled)
        self._on_nonlinear_toggled(False)  # initialise to disabled state

        # Reset provenance badge whenever the user edits any preset-derived field
        for widget in (self._edit_E, self._edit_nu, self._edit_rho,
                       self._edit_sigma_y, self._edit_sigma_u, self._edit_epsilon_u):
            widget.textEdited.connect(self._on_preset_field_edited)

        # ---- vertical spacer (pushes content up) ---------------------
        grid.setRowStretch(row, 1)

        # ---- Button box ----------------------------------------------
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal
        )
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        # ---- Main layout --------------------------------------------
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(grid)
        main_layout.addSpacing(4)
        main_layout.addWidget(_hline())
        main_layout.addWidget(btn_box)

    # ------------------------------------------------------------------
    # Preset provenance badge
    # ------------------------------------------------------------------

    _USER_DEFINED_HTML = '<span style="color:gray;font-style:italic;">User-defined</span>'

    def _update_standard_badge(self):
        if self._preset_standard and self._preset_designation:
            self._lbl_standard_val.setText(
                f'<b>{self._preset_standard}</b> — {self._preset_designation}'
            )
        else:
            self._lbl_standard_val.setText(self._USER_DEFINED_HTML)

    def _on_preset_field_edited(self):
        """Called when the user manually edits any preset-derived input field."""
        if not self._preset_standard and not self._preset_designation:
            return   # already user-defined, nothing to reset
        self._preset_standard    = ''
        self._preset_designation = ''
        self._update_standard_badge()

    # ------------------------------------------------------------------
    # Nonlinear toggle
    # ------------------------------------------------------------------

    def _on_nonlinear_toggled(self, enabled: bool):
        for w in (
            self._lbl_sigma_y,   self._edit_sigma_y,   self._desc_sigma_y,
            self._lbl_sigma_u,   self._edit_sigma_u,   self._desc_sigma_u,
            self._lbl_epsilon_u, self._edit_epsilon_u, self._desc_epsilon_u,
            self._lbl_fracture,  self._check_fracture, self._desc_fracture,
        ):
            w.setEnabled(enabled)

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, material: SteelMaterial):
        """Fill widgets from an existing SteelMaterial instance (edit mode)."""
        if material is None:
            return
        self._edit_name.setText(str(material.name))
        self._edit_E.set_quantity(material.E)
        self._edit_nu.set_quantity(material.nu)
        self._edit_rho.set_quantity(material.rho)
        self._check_nonlinear.setChecked(bool(material.nonlinear))
        self._edit_sigma_y.set_quantity(material.sigma_y)
        self._edit_sigma_u.set_quantity(material.sigma_u)
        self._edit_epsilon_u.set_quantity(material.epsilon_u)
        self._check_fracture.setChecked(bool(material.fracture))
        self._preset_standard    = material.preset_standard
        self._preset_designation = material.preset_designation
        self._visual_material    = material.visual_material
        self._update_standard_badge()

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
            errors.append('E must be a stress/pressure quantity (e.g. 210[GPa]).')
        elif E_val.to_base_units().magnitude <= 0.0:
            errors.append('E must be positive.')

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

        # ---- rho ----
        rho_val = self._edit_rho.value
        rho_err = self._edit_rho.error
        if rho_err:
            errors.append(f'\u03c1: {rho_err}')
        elif rho_val.dimensionality != self._edit_rho.expected_dimensionality:
            errors.append('\u03c1 must be a mass-density quantity (e.g. 7850[kg/m^3]).')
        elif rho_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03c1 must be positive.')

        # ---- nonlinear fields (always validated and stored) ----------
        nonlinear = self._check_nonlinear.isChecked()

        # ---- sigma_y ----
        sigma_y_val = self._edit_sigma_y.value
        sigma_y_err = self._edit_sigma_y.error
        if sigma_y_err:
            errors.append(f'\u03c3_y: {sigma_y_err}')
        elif sigma_y_val.dimensionality != self._edit_sigma_y.expected_dimensionality:
            errors.append('\u03c3_y must be a stress/pressure quantity (e.g. 355[MPa]).')
        elif sigma_y_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03c3_y must be positive.')

        # ---- sigma_u ----
        sigma_u_val = self._edit_sigma_u.value
        sigma_u_err = self._edit_sigma_u.error
        if sigma_u_err:
            errors.append(f'\u03c3\u1d64: {sigma_u_err}')
        elif sigma_u_val.dimensionality != self._edit_sigma_u.expected_dimensionality:
            errors.append('\u03c3\u1d64 must be a stress/pressure quantity (e.g. 510[MPa]).')
        elif sigma_u_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03c3\u1d64 must be positive.')
        elif not sigma_y_err and sigma_u_val.to_base_units().magnitude <= sigma_y_val.to_base_units().magnitude:
            errors.append('\u03c3\u1d64 must be greater than \u03c3_y.')

        # ---- epsilon_u ----
        epsilon_u_val = self._edit_epsilon_u.value
        epsilon_u_err = self._edit_epsilon_u.error
        if epsilon_u_err:
            errors.append(f'\u03b5\u1d64: {epsilon_u_err}')
        elif epsilon_u_val.dimensionality:
            errors.append('\u03b5\u1d64 must be dimensionless (e.g. 0.15).')
        elif float(epsilon_u_val.magnitude) <= 0.0:
            errors.append('\u03b5\u1d64 must be positive.')

        if errors:
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._validated_data = {
            'name':      name,
            'E':         E_val,
            'nu':        nu_val,
            'rho':       rho_val,
            'nonlinear': nonlinear,
            'sigma_y':   sigma_y_val,
            'sigma_u':   sigma_u_val,
            'epsilon_u': epsilon_u_val,
            'fracture':  self._check_fracture.isChecked(),
            'preset_standard':    self._preset_standard,
            'preset_designation': self._preset_designation,
            'visual_material':    self._visual_material,
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def data(self):
        """
        Return the validated input as a plain dict.

        Keys: ``name`` (str), ``E``, ``nu``, ``rho`` (pint.Quantity),
        ``nonlinear`` (bool), ``sigma_y``, ``sigma_u``, ``epsilon_u``
        (pint.Quantity or None when nonlinear is False), ``fracture`` (bool).

        Call this only after the dialog has been accepted.
        """
        return getattr(self, '_validated_data', {})

    def apply_to(self, material: SteelMaterial):
        """Write the validated data directly onto *material*."""
        d = self.data()
        if not d:
            return
        material.name      = d['name']
        material.E         = d['E']
        material.nu        = d['nu']
        material.rho       = d['rho']
        material.nonlinear = d['nonlinear']
        material.sigma_y   = d['sigma_y']
        material.sigma_u   = d['sigma_u']
        material.epsilon_u = d['epsilon_u']
        material.fracture  = d['fracture']
        material.preset_standard    = d.get('preset_standard',    '')
        material.preset_designation = d.get('preset_designation', '')
        material.visual_material    = d.get('visual_material',    None)

    # ------------------------------------------------------------------
    # Shader editor
    # ------------------------------------------------------------------

    def _on_edit_shader(self):
        from opspro.utils.fx_material_utils import edit_fx_material
        result = edit_fx_material(self._visual_material)
        if result is not None:
            self._visual_material = result

    # ------------------------------------------------------------------
    # Preset loader
    # ------------------------------------------------------------------

    def _on_load_preset(self):
        """Open the preset picker and populate all fields from the chosen grade."""
        dlg = SteelPresetDialog(parent=self)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        preset = dlg.selected_preset()
        if preset is None:
            return

        ureg = ParameterManager._unit_registry

        # Always set the name to the preset designation
        self._edit_name.setText(preset.designation)

        self._edit_E.set_quantity(preset.E * ureg.Pa, keep_unit=True)
        self._edit_nu.set_quantity(preset.nu * ureg.dimensionless, keep_unit=True)
        self._edit_rho.set_quantity(preset.rho * ureg('kg/m^3'), keep_unit=True)

        # Always populate the nonlinear fields so the user sees the values,
        # but do not force-enable the nonlinear checkbox — that remains the
        # user's explicit choice.
        self._edit_sigma_y.set_quantity(preset.sigma_y * ureg.Pa, keep_unit=True)
        self._edit_sigma_u.set_quantity(preset.sigma_u * ureg.Pa, keep_unit=True)
        self._edit_epsilon_u.set_quantity(preset.epsilon_u * ureg.dimensionless, keep_unit=True)

        # Track provenance — overwrite any previously loaded preset
        self._preset_standard    = preset.standard
        self._preset_designation = preset.designation
        self._update_standard_badge()
