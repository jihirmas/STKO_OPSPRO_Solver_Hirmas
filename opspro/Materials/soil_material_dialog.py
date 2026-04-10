import pkgutil

from PySide2 import QtCore, QtGui, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Materials.soil_material import SoilMaterial


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


class SoilMaterialDialog(QtWidgets.QDialog):
    """
    QDialog for creating a new SoilMaterial or editing an existing one.

    Usage
    -----
    Create mode::

        dlg = SoilMaterialDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()

    Edit mode (pre-populate with an existing SoilMaterial)::

        dlg = SoilMaterialDialog(material=mat, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.data()
    """

    def __init__(self, material: SoilMaterial = None, parent=None, is_new=False):
        super().__init__(parent)

        self._material       = material
        self._is_new         = is_new
        self._visual_material = None
        self._setup_ui()
        self._populate(material)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New Soil Material' if self._is_new else 'Edit Soil Material'
        self.setWindowTitle(title)
        self.setMinimumWidth(520)

        ureg = ParameterManager._unit_registry
        _default_E   = 50e6   * ureg.Pa
        _default_nu  = 0.3    * ureg.dimensionless
        _default_rho = 1800.0 * ureg('kg/m^3')
        _default_phi = 30.0   * ureg.degree
        _default_c   = 10e3   * ureg.Pa

        # 3-column grid: label | input | description
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 80)
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

        # ---- Name ----------------------------------------------------
        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('e.g. Medium Sand')
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
        grid.addWidget(_lbl('\u03bd:'), row, 0)  # ν
        grid.addWidget(self._edit_nu, row, 1)
        grid.addWidget(_desc("Poisson's ratio"), row, 2)
        row += 1

        self._edit_rho = ExpressionLineEdit(default_value=_default_rho)
        grid.addWidget(_lbl('\u03c1:'), row, 0)  # ρ
        grid.addWidget(self._edit_rho, row, 1)
        grid.addWidget(_desc('Mass density'), row, 2)
        row += 1

        # ---- Nonlinear section (Mohr-Coulomb) ------------------------
        grid.addWidget(_hline(), row, 0, 1, 3)
        row += 1
        grid.addWidget(QtWidgets.QLabel('<b>Nonlinear properties (Mohr-Coulomb)</b>'), row, 0, 1, 3)
        row += 1

        self._check_nonlinear = QtWidgets.QCheckBox()
        self._desc_nonlinear = _desc('Enable Mohr-Coulomb plastic behaviour')
        grid.addWidget(_lbl('Nonlinear:'), row, 0)
        grid.addWidget(self._check_nonlinear, row, 1)
        grid.addWidget(self._desc_nonlinear, row, 2)
        row += 1

        self._lbl_phi = _lbl('\u03c6:')   # φ
        self._edit_phi = ExpressionLineEdit(default_value=_default_phi)
        self._desc_phi = _desc('Friction angle')
        grid.addWidget(self._lbl_phi, row, 0)
        grid.addWidget(self._edit_phi, row, 1)
        grid.addWidget(self._desc_phi, row, 2)
        row += 1

        self._lbl_c = _lbl('c:')
        self._edit_c = ExpressionLineEdit(default_value=_default_c)
        self._desc_c = _desc('Cohesion')
        grid.addWidget(self._lbl_c, row, 0)
        grid.addWidget(self._edit_c, row, 1)
        grid.addWidget(self._desc_c, row, 2)
        row += 1

        self._check_nonlinear.toggled.connect(self._on_nonlinear_toggled)
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

        # ---- Main layout ---------------------------------------------
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(grid)
        main_layout.addSpacing(4)
        main_layout.addWidget(_hline())
        main_layout.addWidget(btn_box)

    # ------------------------------------------------------------------
    # Nonlinear toggle
    # ------------------------------------------------------------------

    def _on_nonlinear_toggled(self, enabled: bool):
        for w in (
            self._lbl_phi, self._edit_phi, self._desc_phi,
            self._lbl_c,   self._edit_c,   self._desc_c,
        ):
            w.setEnabled(enabled)

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, material: SoilMaterial):
        """Fill widgets from an existing SoilMaterial instance (edit mode)."""
        if material is None:
            return
        self._edit_name.setText(str(material.name))
        self._edit_E.set_quantity(material.E)
        self._edit_nu.set_quantity(material.nu)
        self._edit_rho.set_quantity(material.rho)
        self._check_nonlinear.setChecked(bool(material.nonlinear))
        self._edit_phi.set_quantity(material.phi)
        self._edit_c.set_quantity(material.c)
        self._visual_material = material.visual_material

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
            errors.append('\u03c1 must be a mass-density quantity (e.g. 1800[kg/m^3]).')
        elif rho_val.to_base_units().magnitude <= 0.0:
            errors.append('\u03c1 must be positive.')

        # ---- nonlinear fields ----------------------------------------
        nonlinear = self._check_nonlinear.isChecked()

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

        if errors:
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._validated_data = {
            'name':          name,
            'E':             E_val,
            'nu':            nu_val,
            'rho':           rho_val,
            'nonlinear':     nonlinear,
            'phi':           phi_val,
            'c':             c_val,
            'visual_material': self._visual_material,
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def data(self):
        """
        Return the validated input as a plain dict.

        Keys: ``name`` (str), ``E``, ``nu``, ``rho``, ``phi``, ``c``
        (pint.Quantity), ``nonlinear`` (bool), ``visual_material``.
        Call this only after the dialog has been accepted.
        """
        return getattr(self, '_validated_data', {})

    def apply_to(self, material: SoilMaterial):
        """Write the validated data directly onto *material*."""
        d = self.data()
        if not d:
            return
        material.name          = d['name']
        material.E             = d['E']
        material.nu            = d['nu']
        material.rho           = d['rho']
        material.nonlinear     = d['nonlinear']
        material.phi           = d['phi']
        material.c             = d['c']
        material.visual_material = d.get('visual_material', None)

    # ------------------------------------------------------------------
    # Shader editor
    # ------------------------------------------------------------------

    def _on_edit_shader(self):
        from opspro.utils.fx_material_utils import edit_fx_material
        result = edit_fx_material(self._visual_material)
        if result is not None:
            self._visual_material = result
