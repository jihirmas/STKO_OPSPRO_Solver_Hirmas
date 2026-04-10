import pkgutil

from PySide2 import QtCore, QtGui, QtWidgets

from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.ExpressionGuiTools import ExpressionLineEdit
from opspro.Sections.beam_section import BeamSection
from opspro.Sections.presets import registry as section_registry
from opspro.Sections.presets.section_properties import PROP_NAMES, PROP_DESCRIPTIONS, PROP_UNITS


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


def _lbl(text):
    l = QtWidgets.QLabel(text)
    l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    return l


def _desc(text):
    l = QtWidgets.QLabel(text)
    l.setStyleSheet('color: gray; font-style: italic;')
    return l


class BeamSectionDialog(QtWidgets.QDialog):
    """
    QDialog for creating or editing a BeamSection.

    Usage
    -----
    Create mode::

        dlg = BeamSectionDialog(parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            dlg.apply_to(section)

    Edit mode::

        dlg = BeamSectionDialog(section=existing_section, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            dlg.apply_to(existing_section)
    """

    def __init__(self, section: BeamSection = None, parent=None, is_new=False):
        super().__init__(parent)
        self._section = section
        self._is_new = is_new
        self._visual_material = None
        self._param_rows = []   # list of (name_str, lbl_widget, edit_widget, desc_widget)
        self._prop_rows = []    # list of (name_str, lbl_widget, edit_widget, desc_widget)
        self._setup_ui()
        self._populate(section)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        title = 'New Beam Section' if self._is_new else 'Edit Beam Section'
        self.setWindowTitle(title)
        self.setMinimumWidth(560)

        # ---- Top grid (name, combos, image) -----------------------------
        top_grid = QtWidgets.QGridLayout()
        top_grid.setSpacing(8)
        top_grid.setColumnMinimumWidth(0, 50)
        top_grid.setColumnMinimumWidth(2, 50)
        top_grid.setColumnStretch(1, 1)
        top_grid.setColumnStretch(3, 1)

        row = 0

        self._edit_name = QtWidgets.QLineEdit()
        self._edit_name.setPlaceholderText('e.g. IPE 200')
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
        _name_hbox = QtWidgets.QHBoxLayout()
        _name_hbox.setContentsMargins(0, 0, 0, 0)
        _name_hbox.addWidget(self._edit_name)
        _name_hbox.addWidget(self._btn_shader)
        top_grid.addWidget(_lbl('Name:'), row, 0)
        top_grid.addLayout(_name_hbox, row, 1, 1, 3)
        row += 1

        top_grid.addWidget(_hline(), row, 0, 1, 4); row += 1

        self._combo_module = QtWidgets.QComboBox()
        self._combo_module.addItems(section_registry.list_section_types())
        self._combo_preset = QtWidgets.QComboBox()
        top_grid.addWidget(_lbl('Shape:'), row, 0)
        top_grid.addWidget(self._combo_module, row, 1)
        top_grid.addWidget(_lbl('Preset:'), row, 2)
        top_grid.addWidget(self._combo_preset, row, 3)
        row += 1

        self._img_label = QtWidgets.QLabel()
        self._img_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._img_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self._img_label.setStyleSheet('background: white;')
        self._img_label.setFixedHeight(200)
        top_grid.addWidget(self._img_label, row, 0, 1, 4); row += 1

        # ---- Input parameters: container with its own grid --------------
        self._params_container = QtWidgets.QWidget()
        self._params_layout = QtWidgets.QGridLayout(self._params_container)
        self._params_layout.setSpacing(4)
        self._params_layout.setContentsMargins(0, 0, 0, 0)
        self._params_layout.setColumnMinimumWidth(0, 100)
        self._params_layout.setColumnStretch(1, 0)
        self._params_layout.setColumnStretch(2, 1)

        # ---- Output properties section ----------------------------------
        self._props_hline = _hline()
        self._props_header = QtWidgets.QLabel('<b>Section properties</b>')
        self._props_container = QtWidgets.QWidget()
        self._props_layout = QtWidgets.QGridLayout(self._props_container)
        self._props_layout.setSpacing(4)
        self._props_layout.setContentsMargins(0, 0, 0, 0)
        self._props_layout.setColumnMinimumWidth(0, 100)
        self._props_layout.setColumnStretch(1, 0)
        self._props_layout.setColumnStretch(2, 1)
        self._build_prop_rows()

        # ---- Button box -------------------------------------------------
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
        )
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        # ---- Main layout ------------------------------------------------
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_grid)
        main_layout.addWidget(_hline())
        main_layout.addWidget(QtWidgets.QLabel('<b>Input parameters</b>'))
        main_layout.addWidget(self._params_container)
        main_layout.addWidget(self._props_hline)
        main_layout.addWidget(self._props_header)
        main_layout.addWidget(self._props_container)
        main_layout.addStretch(1)
        main_layout.addWidget(_hline())
        main_layout.addWidget(btn_box)

        # ---- Connect signals --------------------------------------------
        self._combo_module.currentTextChanged.connect(self._on_module_changed)
        self._combo_preset.currentTextChanged.connect(self._on_preset_changed)

    def _build_prop_rows(self):
        """Build the fixed output property rows (always 8, always read-only)."""
        _ureg = ParameterManager._unit_registry
        for r, (pname, pdesc, dunit) in enumerate(zip(PROP_NAMES, PROP_DESCRIPTIONS, PROP_UNITS)):
            lbl_w = _lbl(f'{pname}:')
            edit_w = ExpressionLineEdit(default_value=ParameterManager.to_internal_like(0.0 * _ureg(dunit)))
            edit_w.setReadOnly(True)
            desc_w = _desc(pdesc)
            self._props_layout.addWidget(lbl_w, r, 0)
            self._props_layout.addWidget(edit_w, r, 1)
            self._props_layout.addWidget(desc_w, r, 2)
            self._prop_rows.append((pname, lbl_w, edit_w, desc_w))

    # ------------------------------------------------------------------
    # Shader callback
    # ------------------------------------------------------------------

    def _on_edit_shader(self):
        from opspro.utils.fx_material_utils import edit_fx_material
        result = edit_fx_material(self._visual_material)
        if result is not None:
            self._visual_material = result

    # ------------------------------------------------------------------
    # Dynamic input parameter rows
    # ------------------------------------------------------------------

    def _clear_param_rows(self):
        """Destroy all current input parameter widgets."""
        for _, lbl_w, edit_w, desc_w in self._param_rows:
            edit_w.editingFinished.disconnect(self._update_properties)
            lbl_w.deleteLater()
            edit_w.deleteLater()
            desc_w.deleteLater()
        self._param_rows.clear()

    def _build_param_rows(self, module_name: str, source: dict, is_user: bool):
        """Create input parameter widgets for the given module."""
        param_names = section_registry.get_param_names(module_name)
        param_descs = section_registry.get_param_descriptions(module_name)
        mod = section_registry.get_preset_module(module_name)
        param_units = getattr(mod, 'PARAM_UNITS', ['mm'] * len(param_names)) if mod else ['mm'] * len(param_names)
        _ureg = ParameterManager._unit_registry

        for r, pname in enumerate(param_names):
            dunit = param_units[r] if r < len(param_units) else 'mm'
            val = source.get(pname, ParameterManager.to_internal_like(0.0 * _ureg(dunit)))
            pdesc = param_descs[r] if r < len(param_descs) else ''

            lbl_w = _lbl(f'{pname}:')
            edit_w = ExpressionLineEdit(default_value=ParameterManager.to_internal_like(0.0 * _ureg(dunit)))
            edit_w.set_quantity(ParameterManager.to_internal_like(val))
            edit_w.setReadOnly(not is_user)
            edit_w.editingFinished.connect(self._update_properties)
            desc_w = _desc(pdesc)

            self._params_layout.addWidget(lbl_w, r, 0)
            self._params_layout.addWidget(edit_w, r, 1)
            self._params_layout.addWidget(desc_w, r, 2)
            self._param_rows.append((pname, lbl_w, edit_w, desc_w))

    # ------------------------------------------------------------------
    # Dynamic UI updates
    # ------------------------------------------------------------------

    def _on_module_changed(self, module_name: str):
        """Rebuild the preset combo and parameter rows for the new module."""
        self._update_profile_image(module_name)

        # Rebuild preset combo
        self._combo_preset.blockSignals(True)
        self._combo_preset.clear()
        self._combo_preset.addItem('user')
        presets = section_registry.list_presets(module_name)
        for p in presets:
            self._combo_preset.addItem(getattr(p, 'name', str(p)))
        self._combo_preset.blockSignals(False)

        # Hide output section for Custom (input == output)
        is_custom = (module_name == 'Custom')
        self._set_properties_visible(not is_custom)

        # Trigger preset change (this will rebuild param rows)
        self._on_preset_changed(self._combo_preset.currentText())

    def _on_preset_changed(self, preset_name: str):
        """Rebuild parameter rows from the selected preset or CUSTOM defaults."""
        module_name = self._combo_module.currentText()
        is_user = (preset_name == 'user')

        if is_user:
            custom = section_registry.get_custom(module_name)
            if custom is not None:
                source = custom.__dict__.copy()
                source.pop('name', None)
            else:
                source = {}
        else:
            preset = section_registry.get_preset(module_name, preset_name)
            if preset is not None:
                source = preset.__dict__.copy()
                source.pop('name', None)
            else:
                source = {}

        # Rebuild input parameter rows
        self._clear_param_rows()
        self._build_param_rows(module_name, source, is_user)

        self._update_properties()

    def _set_properties_visible(self, visible: bool):
        """Show or hide the entire output properties section."""
        self._props_hline.setVisible(visible)
        self._props_header.setVisible(visible)
        self._props_container.setVisible(visible)

    def _update_properties(self):
        """Recalculate section properties from current input parameters and display them."""
        module_name = self._combo_module.currentText()
        if module_name == 'Custom':
            return

        # Gather current input values
        params = {}
        for pname, _, edit_w, _ in self._param_rows:
            if edit_w.error:
                self._clear_properties()
                return
            params[pname] = edit_w.value

        calc_fn = section_registry.get_calculate_function(module_name)
        if calc_fn is None:
            self._clear_properties()
            return
        try:
            props = calc_fn(params)
        except Exception:
            self._clear_properties()
            return

        for pname, _, edit_w, _ in self._prop_rows:
            val = getattr(props, pname, None)
            if val is not None:
                edit_w.set_quantity(val)

    def _clear_properties(self):
        """Clear all output property fields."""
        for _, _, edit_w, _ in self._prop_rows:
            edit_w.clear()

    def _update_profile_image(self, module_name: str):
        """Load and display the profile image for the given section type."""
        image_path = section_registry.get_profile_image(module_name)
        if image_path:
            try:
                image_data = pkgutil.get_data('opspro', image_path)
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(image_data)
                self._img_label.setPixmap(pixmap)
                return
            except Exception:
                pass
        self._img_label.clear()

    # ------------------------------------------------------------------
    # Population (edit mode)
    # ------------------------------------------------------------------

    def _populate(self, section: BeamSection):
        """Fill widgets from an existing BeamSection (edit mode)."""
        if section is None:
            self._on_module_changed(self._combo_module.currentText())
            return

        # Always pick up visual_material from the passed section (proto or real).
        self._visual_material = section.visual_material

        # Proto section (no preset assigned yet): initialize combos with defaults.
        if section.preset_module is None:
            self._edit_name.setText(str(section.name))
            self._on_module_changed(self._combo_module.currentText())
            return

        self._edit_name.setText(str(section.name))

        # Block the module combo signal and set the index, then call _on_module_changed
        # explicitly. This avoids the bug where setting index 0 (Rectangular — the
        # default first item) emits no currentTextChanged signal and the image / param
        # rows are never built.
        idx = self._combo_module.findText(section.preset_module or '')
        if idx >= 0:
            self._combo_module.blockSignals(True)
            self._combo_module.setCurrentIndex(idx)
            self._combo_module.blockSignals(False)
        self._on_module_changed(section.preset_module or self._combo_module.currentText())

        # Same issue for the preset combo: block and set, then fire manually only when
        # the desired preset is not 'user' (for 'user' _on_module_changed already called
        # _on_preset_changed('user'), so no double-rebuild is needed).
        preset_name = section.preset_name or 'user'
        idx = self._combo_preset.findText(preset_name)
        if idx >= 0:
            self._combo_preset.blockSignals(True)
            self._combo_preset.setCurrentIndex(idx)
            self._combo_preset.blockSignals(False)
        if preset_name != 'user':
            self._on_preset_changed(preset_name)

        # If user-defined, override with actual stored parameters
        if section.preset_name == 'user' and section.parameters:
            for pname, _, edit_w, _ in self._param_rows:
                val = section.parameters.get(pname)
                if val is not None:
                    edit_w.set_quantity(val)
            self._update_properties()

    # ------------------------------------------------------------------
    # Validation & acceptance
    # ------------------------------------------------------------------

    def _on_accepted(self):
        errors = []

        name = self._edit_name.text().strip()
        if not name:
            errors.append('Name must not be empty.')

        module_name = self._combo_module.currentText()
        preset_name = self._combo_preset.currentText()

        params = {}
        for pname, _, edit_w, _ in self._param_rows:
            err = edit_w.error
            if err:
                errors.append(f'{pname}: {err}')
            else:
                params[pname] = edit_w.value

        if errors:
            QtWidgets.QMessageBox.warning(self, 'Invalid input', '\n'.join(errors))
            return

        self._validated_data = {
            'name': name,
            'preset_module': module_name,
            'preset_name': preset_name,
            'parameters': params,
            'visual_material': self._visual_material,
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def data(self):
        """Return validated data as a dict. Call only after acceptance."""
        return getattr(self, '_validated_data', {})

    def apply_to(self, section: BeamSection):
        """Write validated data onto *section*."""
        d = self.data()
        if not d:
            return
        section.name = d['name']
        section.preset_module = d['preset_module']
        section.preset_name = d['preset_name']
        section.parameters = d['parameters']
        section.visual_material = d.get('visual_material')
