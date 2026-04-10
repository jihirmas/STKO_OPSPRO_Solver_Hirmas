import pkgutil

from PySide2 import QtCore, QtGui, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Materials.concrete_material import ConcreteMaterial
from opspro.Materials.presets.concrete_presets import mc2010_fracture_energy


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


class ConcreteMaterialDialog(QtWidgets.QDialog):
    """
    QDialog for creating a new ConcreteMaterial or editing an existing one.

    Usage
    -----
    Create mode::

        dlg = ConcreteMaterialDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()

    Edit mode (pre-populate with an existing ConcreteMaterial)::

        dlg = ConcreteMaterialDialog(material=mat, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()
    """

    def __init__(self, material: ConcreteMaterial = None, parent=None, is_new=False):
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
        title = 'New Concrete Material' if self._is_new else 'Edit Concrete Material'
        self.setWindowTitle(title)
        self.setMinimumWidth(520)

        ureg = ParameterManager._unit_registry
        _default_E   = 30e9   * ureg.Pa
        _default_nu  = 0.2    * ureg.dimensionless
        _default_rho = 2400.0 * ureg('kg/m^3')
        _default_fcp = 30e6   * ureg.Pa
        _default_ft  = 2.9e6  * ureg.Pa
        _Gt0, _Gc0   = mc2010_fracture_energy(30.0)   # consistent with default fcp = 30 MPa
        _default_Gt  = _Gt0 * ureg('J/m^2')
        _default_Gc  = _Gc0 * ureg('J/m^2')

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
        self._edit_name.setPlaceholderText('e.g. C30/37')
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

        # ---- Stress-strain diagram image -----------------------------
        img_label = QtWidgets.QLabel()
        img_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        img_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        img_label.setStyleSheet('background: white;')
        try:
            image_data = pkgutil.get_data('opspro', 'assets/images/concrete_material_image_001.png')
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

        self._lbl_standard_val = QtWidgets.QLabel()
        self._lbl_standard_val.setTextFormat(QtCore.Qt.RichText)
        grid.addWidget(_lbl('Standard:'), row, 0)
        grid.addWidget(self._lbl_standard_val, row, 1, 1, 2)
        row += 1

        btn_preset = QtWidgets.QPushButton('Load preset\u2026')
        btn_preset.setToolTip('Pre-populate fields from a standard concrete class (EN 1992, ACI 318, \u2026)')
        btn_preset.clicked.connect(self._on_load_preset)
        grid.addWidget(_lbl('Grade:'), row, 0)
        grid.addWidget(btn_preset, row, 1)
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
        self._desc_nonlinear = _desc('Enable fracture-based nonlinear behaviour')
        grid.addWidget(_lbl('Nonlinear:'), row, 0)
        grid.addWidget(self._check_nonlinear, row, 1)
        grid.addWidget(self._desc_nonlinear, row, 2)
        row += 1

        self._lbl_fcp = _lbl('f<sub>cp</sub>:')
        self._edit_fcp = ExpressionLineEdit(default_value=_default_fcp)
        self._desc_fcp = _desc('Peak compressive strength')
        grid.addWidget(self._lbl_fcp, row, 0)
        grid.addWidget(self._edit_fcp, row, 1)
        grid.addWidget(self._desc_fcp, row, 2)
        row += 1

        self._lbl_ft = _lbl('f<sub>t</sub>:')
        self._edit_ft = ExpressionLineEdit(default_value=_default_ft)
        self._desc_ft = _desc('Peak tensile strength')
        grid.addWidget(self._lbl_ft, row, 0)
        grid.addWidget(self._edit_ft, row, 1)
        grid.addWidget(self._desc_ft, row, 2)
        row += 1

        self._lbl_auto_GtGc  = _lbl('Auto G:')
        self._check_auto_GtGc = QtWidgets.QCheckBox()
        self._check_auto_GtGc.setChecked(True)
        self._desc_auto_GtGc  = _desc('Compute G<sub>t</sub>, G<sub>c</sub> from f<sub>cp</sub> via Model Code 2010')
        grid.addWidget(self._lbl_auto_GtGc,  row, 0)
        grid.addWidget(self._check_auto_GtGc, row, 1)
        grid.addWidget(self._desc_auto_GtGc,  row, 2)
        row += 1

        self._lbl_Gt = _lbl('G<sub>t</sub>:')
        self._edit_Gt = ExpressionLineEdit(default_value=_default_Gt)
        self._desc_Gt = _desc('Tensile frac. energy  [MC2010: 73\u00b7f<sub>cp</sub><sup>0.18</sup>, J/m<sup>2</sup>]')
        grid.addWidget(self._lbl_Gt, row, 0)
        grid.addWidget(self._edit_Gt, row, 1)
        grid.addWidget(self._desc_Gt, row, 2)
        row += 1

        self._lbl_Gc = _lbl('G<sub>c</sub>:')
        self._edit_Gc = ExpressionLineEdit(default_value=_default_Gc)
        self._desc_Gc = _desc('Compressive frac. energy  [MC2010: 250\u00b7G<sub>t</sub>, J/m<sup>2</sup>]')
        grid.addWidget(self._lbl_Gc, row, 0)
        grid.addWidget(self._edit_Gc, row, 1)
        grid.addWidget(self._desc_Gc, row, 2)
        row += 1

        self._check_nonlinear.toggled.connect(self._on_nonlinear_toggled)
        self._check_auto_GtGc.toggled.connect(self._on_auto_GtGc_toggled)
        self._on_nonlinear_toggled(False)  # initialise to disabled state

        # Reset provenance badge whenever the user edits any preset-derived field
        for widget in (self._edit_E, self._edit_nu, self._edit_rho,
                       self._edit_fcp, self._edit_ft, self._edit_Gt, self._edit_Gc):
            widget.textEdited.connect(self._on_preset_field_edited)
        # fcp edits also trigger auto-recompute of Gt/Gc
        self._edit_fcp.textEdited.connect(self._recompute_fracture_energy)

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
                f'<b>{self._preset_standard}</b> \u2014 {self._preset_designation}'
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
            self._lbl_fcp, self._edit_fcp, self._desc_fcp,
            self._lbl_ft,  self._edit_ft,  self._desc_ft,
            self._lbl_auto_GtGc, self._check_auto_GtGc, self._desc_auto_GtGc,
        ):
            w.setEnabled(enabled)
        # Gt/Gc are editable only when nonlinear is ON and auto is OFF
        auto = self._check_auto_GtGc.isChecked()
        for w in (self._lbl_Gt, self._edit_Gt, self._desc_Gt,
                  self._lbl_Gc, self._edit_Gc, self._desc_Gc):
            w.setEnabled(enabled and not auto)

    # ------------------------------------------------------------------
    # Auto fracture energy toggle
    # ------------------------------------------------------------------

    def _on_auto_GtGc_toggled(self, auto: bool):
        nonlinear = self._check_nonlinear.isChecked()
        for w in (self._lbl_Gt, self._edit_Gt, self._desc_Gt,
                  self._lbl_Gc, self._edit_Gc, self._desc_Gc):
            w.setEnabled(nonlinear and not auto)
        if auto and nonlinear:
            self._recompute_fracture_energy()

    def _recompute_fracture_energy(self):
        """Recompute Gt/Gc from fcp using Model Code 2010, if auto mode is on."""
        if not self._check_auto_GtGc.isChecked():
            return
        if self._edit_fcp.error:
            return
        try:
            # Explicit conversion to MPa — do not rely on to_base_units() being SI
            fcp_mpa = float(self._edit_fcp.value.to('MPa').magnitude)
            if fcp_mpa <= 0.0:
                return
            Gt_jm2, Gc_jm2 = mc2010_fracture_energy(fcp_mpa)
            ureg = ParameterManager._unit_registry
            Gt_qty = Gt_jm2 * ureg('J/m^2')
            Gc_qty = Gc_jm2 * ureg('J/m^2')
            self._edit_Gt.set_quantity(Gt_qty, keep_unit=True)
            self._edit_Gc.set_quantity(Gc_qty, keep_unit=True)
        except Exception:
            pass

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
        """Open the concrete preset picker and populate all fields."""
        from opspro.Materials.presets import ConcretePresetDialog
        dlg = ConcretePresetDialog(parent=self)
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

        # Always populate all nonlinear fields
        self._edit_fcp.set_quantity(preset.fcp * ureg.Pa, keep_unit=True)
        self._edit_ft.set_quantity(preset.ft * ureg.Pa, keep_unit=True)

        # Set Gt/Gc from preset (already MC2010-computed at preset construction)
        self._edit_Gt.set_quantity(preset.Gt * ureg('J/m^2'), keep_unit=True)
        self._edit_Gc.set_quantity(preset.Gc * ureg('J/m^2'), keep_unit=True)

        # Track provenance — overwrite any previously loaded preset
        self._preset_standard    = preset.standard
        self._preset_designation = preset.designation
        self._update_standard_badge()

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, material: ConcreteMaterial):
        """Fill widgets from an existing ConcreteMaterial instance (edit mode)."""
        if material is None:
            return
        self._edit_name.setText(str(material.name))
        self._edit_E.set_quantity(material.E)
        self._edit_nu.set_quantity(material.nu)
        self._edit_rho.set_quantity(material.rho)
        self._check_nonlinear.setChecked(bool(material.nonlinear))
        self._edit_fcp.set_quantity(material.fcp)
        self._edit_ft.set_quantity(material.ft)
        self._edit_Gt.set_quantity(material.Gt)
        self._edit_Gc.set_quantity(material.Gc)
        self._check_auto_GtGc.setChecked(bool(material.auto_fracture_energy))
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
            errors.append('E must be a stress/pressure quantity (e.g. 30[GPa]).')
        elif E_val.to_base_units().magnitude <= 0.0:
            errors.append('E must be positive.')

        # ---- nu ----
        nu_val = self._edit_nu.value
        nu_err = self._edit_nu.error
        if nu_err:
            errors.append(f'\u03bd: {nu_err}')
        elif nu_val.dimensionality:
            errors.append('\u03bd must be dimensionless (e.g. 0.2).')
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
            errors.append('\u03c1 must be a mass-density quantity (e.g. 2400[kg/m^3]).')
        elif rho_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03c1 must be positive.')

        # ---- nonlinear fields (always validated and stored) ----------
        nonlinear = self._check_nonlinear.isChecked()
        auto_GtGc = self._check_auto_GtGc.isChecked()

        # ---- fcp ----
        fcp_val = self._edit_fcp.value
        fcp_err = self._edit_fcp.error
        if fcp_err:
            errors.append(f'f_cp: {fcp_err}')
        elif fcp_val.dimensionality != self._edit_fcp.expected_dimensionality:
            errors.append('f_cp must be a stress/pressure quantity (e.g. 30[MPa]).')
        elif fcp_val.to_base_units().magnitude <= 0.0:
            errors.append('f_cp must be positive.')

        # ---- ft ----
        ft_val = self._edit_ft.value
        ft_err = self._edit_ft.error
        if ft_err:
            errors.append(f'f_t: {ft_err}')
        elif ft_val.dimensionality != self._edit_ft.expected_dimensionality:
            errors.append('f_t must be a stress/pressure quantity (e.g. 2.9[MPa]).')
        elif ft_val.to_base_units().magnitude <= 0.0:
            errors.append('f_t must be positive.')

        # ---- Gt ----
        Gt_val = self._edit_Gt.value
        Gt_err = self._edit_Gt.error
        if Gt_err:
            errors.append(f'G_t: {Gt_err}')
        elif Gt_val.dimensionality != self._edit_Gt.expected_dimensionality:
            errors.append('G_t must be a fracture energy quantity (e.g. 150[J/m^2]).')
        elif Gt_val.to_base_units().magnitude <= 0.0:
            errors.append('G_t must be positive.')

        # ---- Gc ----
        Gc_val = self._edit_Gc.value
        Gc_err = self._edit_Gc.error
        if Gc_err:
            errors.append(f'G_c: {Gc_err}')
        elif Gc_val.dimensionality != self._edit_Gc.expected_dimensionality:
            errors.append('G_c must be a fracture energy quantity (e.g. 30000[J/m^2]).')
        elif Gc_val.to_base_units().magnitude <= 0.0:
            errors.append('G_c must be positive.')

        if errors:
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._validated_data = {
            'name':                name,
            'E':                   E_val,
            'nu':                  nu_val,
            'rho':                 rho_val,
            'nonlinear':           nonlinear,
            'auto_fracture_energy': auto_GtGc,
            'fcp':                 fcp_val,
            'ft':                  ft_val,
            'Gt':                  Gt_val,
            'Gc':                  Gc_val,
            'preset_standard':     self._preset_standard,
            'preset_designation':  self._preset_designation,
            'visual_material':     self._visual_material,
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def data(self):
        """
        Return the validated input as a plain dict.

        Keys: ``name`` (str), ``E``, ``nu``, ``rho`` (pint.Quantity),
        ``nonlinear`` (bool), ``fcp``, ``ft``, ``Gt``, ``Gc`` (pint.Quantity),
        ``preset_standard``, ``preset_designation`` (str).

        Call this only after the dialog has been accepted.
        """
        return getattr(self, '_validated_data', {})

    def apply_to(self, material: ConcreteMaterial):
        """Write the validated data directly onto *material*."""
        d = self.data()
        if not d:
            return
        material.name      = d['name']
        material.E         = d['E']
        material.nu        = d['nu']
        material.rho       = d['rho']
        material.nonlinear = d['nonlinear']
        material.fcp       = d['fcp']
        material.ft        = d['ft']
        material.Gt        = d['Gt']
        material.Gc                    = d['Gc']
        material.auto_fracture_energy   = d.get('auto_fracture_energy', True)
        material.preset_standard        = d.get('preset_standard',    '')
        material.preset_designation     = d.get('preset_designation', '')
        material.visual_material        = d.get('visual_material',    None)
