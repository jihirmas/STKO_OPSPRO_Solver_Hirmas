from PySide2 import QtCore, QtWidgets

from opspro.Settings.document_settings import DocumentSettings
from opspro.parameters.ParameterManager import ParameterManager


# ---------------------------------------------------------------------------
# Filter ParameterManager._unit_common_symbols by base dimensionality.
# Each list contains only symbols whose unit is purely that one dimension.
# ---------------------------------------------------------------------------

def _filter_by_dim(dim_key: str):
    """Return symbols from _unit_common_symbols whose dimensionality is
    exactly {dim_key: 1} (i.e. a pure base unit of that kind)."""
    ureg = ParameterManager._unit_registry
    result = []
    for sym in ParameterManager._unit_common_symbols:
        try:
            unit = ureg.parse_units(sym)
            dims = dict(unit.dimensionality)
            if dims == {dim_key: 1}:
                result.append(sym)
        except Exception:
            pass
    return result


_LENGTH_UNITS      = _filter_by_dim('[length]')
_MASS_UNITS        = _filter_by_dim('[mass]')
_TIME_UNITS        = _filter_by_dim('[time]')
_TEMPERATURE_UNITS = _filter_by_dim('[temperature]')


class DocumentSettingsDialog(QtWidgets.QDialog):
    """
    QDialog for editing a :class:`DocumentSettings` instance.

    Usage::

        dlg = DocumentSettingsDialog(settings, parent=parent_widget)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            dlg.apply_to(settings)   # write validated data back

    The dialog never mutates the passed *settings* object until
    :meth:`apply_to` is called explicitly by the caller.
    """

    def __init__(self, settings: DocumentSettings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._setup_ui()
        self._populate(settings)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        self.setWindowTitle('Document Settings')
        self.setMinimumWidth(380)

        # ---- tab widget ---------------------------------------------
        self._tab_widget = QtWidgets.QTabWidget()
        self._tab_widget.addTab(self._build_unit_system_tab(), 'Unit System')

        # ---- button box ---------------------------------------------
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
        )
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        # ---- main layout --------------------------------------------
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self._tab_widget)
        main_layout.addWidget(btn_box)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

    def _build_unit_system_tab(self) -> QtWidgets.QWidget:
        """Build the Unit System tab and return it as a widget."""
        tab = QtWidgets.QWidget()

        outer = QtWidgets.QVBoxLayout(tab)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(12)

        # ---- explanatory label --------------------------------------
        info_label = QtWidgets.QLabel(
            '<b>Reference Unit System</b><br><br>'
            'Define the four independent base units (length, mass, time, '
            'temperature) that form the reference unit system for this document.<br><br>'
            'All derived quantities — force, pressure, density, stiffness, etc. — '
            'are automatically expressed in terms of these base units. '
            'For example, choosing <i>mm · t · s</i> yields force in N and '
            'stress in MPa.'
        )
        info_label.setWordWrap(True)
        info_label.setTextFormat(QtCore.Qt.RichText)
        outer.addWidget(info_label)

        # ---- separator ----------------------------------------------
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Sunken)
        outer.addWidget(sep)

        # ---- grid: Name | ComboBox | Unit description ---------------
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 90)   # label column
        grid.setColumnStretch(1, 0)         # combobox — natural size
        grid.setColumnStretch(2, 1)         # description — takes remaining space

        ureg = ParameterManager._unit_registry

        def _unit_description(sym: str) -> str:
            try:
                return str(ureg.parse_units(sym))
            except Exception:
                return ''

        def _make_desc_label() -> QtWidgets.QLabel:
            lbl = QtWidgets.QLabel()
            lbl.setStyleSheet('color: gray; font-style: italic;')
            return lbl

        def _wire(combo: QtWidgets.QComboBox, desc: QtWidgets.QLabel):
            def _update(text):
                desc.setText(_unit_description(text))
            combo.currentTextChanged.connect(_update)
            _update(combo.currentText())    # initialise immediately

        rows = [
            ('Length:',      '_combo_length',      _LENGTH_UNITS),
            ('Mass:',        '_combo_mass',         _MASS_UNITS),
            ('Time:',        '_combo_time',         _TIME_UNITS),
            ('Temperature:', '_combo_temperature',  _TEMPERATURE_UNITS),
        ]
        for row_idx, (label_text, attr_name, items) in enumerate(rows):
            lbl = QtWidgets.QLabel(label_text)
            lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            combo = QtWidgets.QComboBox()
            combo.addItems(items)
            setattr(self, attr_name, combo)

            desc = _make_desc_label()
            setattr(self, attr_name.replace('_combo_', '_desc_'), desc)

            grid.addWidget(lbl,   row_idx, 0)
            grid.addWidget(combo, row_idx, 1)
            grid.addWidget(desc,  row_idx, 2)
            _wire(combo, desc)

        outer.addLayout(grid)

        # ---- pro-tip ------------------------------------------------
        tip = QtWidgets.QLabel(
            '<b>&#128161; Pro tip — unit system and numerical conditioning</b><br><br>'
            'The FEM stiffness matrix <b>K</b> mixes entries of different physical '
            'dimensions. For <i>beam / frame</i> elements the translational block '
            'scales as <span style="font-family:monospace;">EI/L³</span> while the '
            'rotational block scales as <span style="font-family:monospace;">EI/L</span>, '
            'so their ratio grows as <span style="font-family:monospace;">1/L²</span>. '
            'On large models (L in the range of metres) working in '
            '<b>mm</b> inflates this ratio by 10⁶ or more, worsening the '
            'condition number and potentially causing solver inaccuracies or '
            'convergence failures.<br><br>'
            'Recommended practice:<br>'
            '&nbsp;&nbsp;• <b>Structural / infrastructure models</b> (bridges, buildings, '
            'geotechnics): use <b>m · t · s</b> (F → kN, σ → kPa) or '
            '<b>m · kg · s</b> (SI, F → N, σ → Pa).<br>'
            '&nbsp;&nbsp;• <b>Detailed / connection models</b> (joints, welds, '
            'cross-sections): <b>mm · t · s</b> (F → N, σ → MPa) is fine '
            'because element lengths stay in a compact, well-conditioned range.'
        )
        tip.setWordWrap(True)
        tip.setTextFormat(QtCore.Qt.RichText)
        tip.setContentsMargins(10, 10, 10, 10)
        tip.setStyleSheet(
            'QLabel {'
            '  background-color: #EEF5FF;'   # very light blue tint
            '  border: 1px solid #2798FC;'   # brand blue (39, 152, 252)
            '  border-radius: 4px;'
            '  color: #1A1A1A;'              # near-black, matches icon grey
            '}'
        )
        outer.addWidget(tip)
        outer.addStretch()

        return tab

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self, settings: DocumentSettings):
        """Set combo boxes to match the current settings values."""
        self._set_combo(self._combo_length,      settings.length_unit)
        self._set_combo(self._combo_mass,         settings.mass_unit)
        self._set_combo(self._combo_time,         settings.time_unit)
        self._set_combo(self._combo_temperature,  settings.temperature_unit)

    @staticmethod
    def _set_combo(combo: QtWidgets.QComboBox, value: str):
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    # ------------------------------------------------------------------
    # Validation & acceptance
    # ------------------------------------------------------------------

    def _on_accepted(self):
        self._validated_data = {
            'length_unit':      self._combo_length.currentText(),
            'mass_unit':        self._combo_mass.currentText(),
            'time_unit':        self._combo_time.currentText(),
            'temperature_unit': self._combo_temperature.currentText(),
        }
        self.accept()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def data(self) -> dict:
        """
        Return the validated input as a plain dict.

        Keys: ``length_unit``, ``mass_unit``, ``time_unit``,
        ``temperature_unit`` (all ``str``).

        Call this only after the dialog has been accepted.
        """
        return getattr(self, '_validated_data', {})

    def apply_to(self, settings: DocumentSettings):
        """
        Write the validated data onto *settings* and call
        :meth:`~DocumentSettings.apply` to propagate the new unit system.
        """
        d = self.data()
        if not d:
            return
        settings.length_unit      = d['length_unit']
        settings.mass_unit        = d['mass_unit']
        settings.time_unit        = d['time_unit']
        settings.temperature_unit = d['temperature_unit']
        settings.apply()
