"""
steel_preset_dialog.py
----------------------
QDialog that lets the user pick a steel grade from the presets database.

Layout
------
* Description label.
* Search box  +  Standard combo  — filter controls at the top.
* Sortable / filterable QTableView showing all preset grades.
* Row-count label.
* OK / Cancel buttons.

Columns
-------
0  Standard     str   e.g. "ASTM"
1  Designation  str   e.g. "A572-50"
2  Name         str   e.g. "ASTM A572 Gr.50"
3  E            str   e.g. "200.0 GPa"
4  σ_y          str   e.g. "345 MPa"
5  σ_u          str   e.g. "448 MPa"
6  ε_u          str   e.g. "21.0 %"   (elongation at fracture, 2" gauge)
7  Notes        str   normative reference

Usage
-----
::

    dlg = SteelPresetDialog(parent=parent_widget)
    if dlg.exec() == QtWidgets.QDialog.Accepted:
        preset = dlg.selected_preset()   # SteelPreset | None
"""

import pkgutil

from PySide2 import QtCore, QtGui, QtWidgets

from opspro.Materials.presets.steel_presets import PRESETS, SteelPreset


# ---------------------------------------------------------------------------
# Flag icons — one PNG per national/regional standard family
# ---------------------------------------------------------------------------

_STANDARD_FLAG_FILE: dict[str, str] = {
    'ASTM': 'flag_USA.png',
    'API' : 'flag_USA.png',
    'AISI': 'flag_USA.png',
    'ASME': 'flag_USA.png',
    'EN'  : 'flag_EU.png',
    'JIS' : 'flag_JPN.png',
    'GB'    : 'flag_CHN.png',
    'AS/NZS': 'flag_AUS.png',
    'IS'    : 'flag_IND.png',
    'CSA'   : 'flag_CAN.png',
    'UNI'   : 'flag_ITA.png',
}

# Canonical display order for the Standard column and combo box.
# Any standard not listed here will appear at the end, sorted alphabetically.
_STANDARD_ORDER: list[str] = ['ASTM', 'API', 'AISI', 'ASME', 'EN', 'JIS', 'GB', 'AS/NZS', 'IS', 'CSA', 'UNI']


def _standard_rank(std: str) -> int:
    """Return sort rank for *std*; unknown standards go after the known ones."""
    try:
        return _STANDARD_ORDER.index(std)
    except ValueError:
        return len(_STANDARD_ORDER)


def _ordered_standards(presets: dict) -> list[str]:
    """Return the keys of *presets* in canonical display order."""
    ordered = [k for k in _STANDARD_ORDER if k in presets]
    ordered += sorted(k for k in presets if k not in _STANDARD_ORDER)
    return ordered

_flag_pixmap_cache: dict[str, QtGui.QIcon | None] = {}


def _flag_icon(standard: str) -> 'QtGui.QIcon | None':
    """Return a cached QIcon for *standard*, or None if unknown."""
    fname = _STANDARD_FLAG_FILE.get(standard)
    if fname is None:
        return None
    if fname not in _flag_pixmap_cache:
        raw = pkgutil.get_data('opspro', f'assets/images/{fname}')
        if raw:
            pm = QtGui.QPixmap()
            pm.loadFromData(raw)
            _flag_pixmap_cache[fname] = QtGui.QIcon(pm) if not pm.isNull() else None
        else:
            _flag_pixmap_cache[fname] = None
    return _flag_pixmap_cache[fname]


# ---------------------------------------------------------------------------
# Column indices
# ---------------------------------------------------------------------------

_COL_STANDARD    = 0
_COL_DESIGNATION = 1
_COL_NAME        = 2
_COL_E           = 3
_COL_SIGMA_Y     = 4
_COL_SIGMA_U     = 5
_COL_EPSILON_U   = 6
_COL_NOTES       = 7

_HEADERS = [
    'Standard',
    'Designation',
    'Name',
    'E',
    '\u03c3\u02b8',       # σ_y
    '\u03c3\u1d64',       # σ_u
    '\u03b5\u1d64',       # ε_u
    'Notes',
]

_NUMERIC_COLS = {_COL_E, _COL_SIGMA_Y, _COL_SIGMA_U, _COL_EPSILON_U}


# ---------------------------------------------------------------------------
# Helpers — unit formatting
# ---------------------------------------------------------------------------

def _fmt_E(pa: float) -> str:
    return f'{pa / 1e9:.1f} GPa'

def _fmt_stress(pa: float) -> str:
    return f'{pa / 1e6:.0f} MPa'

def _fmt_strain(val: float) -> str:
    return f'{val * 100:.1f} %'


# ---------------------------------------------------------------------------
# Row builder
# ---------------------------------------------------------------------------

def _build_rows(presets: dict[str, list[SteelPreset]]) -> list[tuple]:
    """Flatten PRESETS into display rows (one tuple per grade) in canonical order."""
    rows = []
    for standard in _ordered_standards(presets):
        for p in presets[standard]:
            rows.append((
                standard,
                p.designation,
                p.name,
                _fmt_E(p.E),
                _fmt_stress(p.sigma_y),
                _fmt_stress(p.sigma_u),
                _fmt_strain(p.epsilon_u),
                p.notes,
            ))
    return rows


# ---------------------------------------------------------------------------
# Table model
# ---------------------------------------------------------------------------

class _PresetTableModel(QtCore.QAbstractTableModel):

    def __init__(self, rows: list[tuple], preset_objects: list[SteelPreset], parent=None):
        super().__init__(parent)
        self._rows    = rows
        self._presets = preset_objects          # parallel list — same indexing
        # Pre-computed lowercase tab-joined strings for free-text search
        self._search_strings = [
            '\t'.join(str(v).lower() for v in row)
            for row in rows
        ]

    # ------------------------------------------------------------------
    def rowCount(self, parent=QtCore.QModelIndex()):
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 0 if parent.isValid() else len(_HEADERS)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return _HEADERS[section]
        return None

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = self._rows[index.row()]
        col = index.column()

        if role == QtCore.Qt.DisplayRole:
            return str(row[col])

        if role == QtCore.Qt.DecorationRole:
            if col == _COL_STANDARD:
                return _flag_icon(str(row[col]))

        if role == QtCore.Qt.TextAlignmentRole:
            if col in _NUMERIC_COLS:
                return int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            if col == _COL_NOTES:
                return int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            return int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        if role == QtCore.Qt.ForegroundRole:
            if col == _COL_NOTES:
                return QtGui.QColor(120, 120, 120)

        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def preset_at(self, source_row: int) -> SteelPreset:
        return self._presets[source_row]


# ---------------------------------------------------------------------------
# Sort/filter proxy
# ---------------------------------------------------------------------------

class _PresetFilterProxy(QtCore.QSortFilterProxyModel):
    """
    Supports two independent filter conditions, ANDed together:

    * Free-text substring across all columns (case-insensitive, debounced).
    * Exact match on Standard column ('' means all).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text_filter     = ''
        self._standard_filter = ''
        self.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def set_text(self, text: str):
        self._text_filter = text.strip().lower()
        self.invalidateFilter()

    def set_standard(self, label: str):
        self._standard_filter = label if label != 'All' else ''
        self.invalidateFilter()

    # ------------------------------------------------------------------
    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        src = self.sourceModel()
        row = src._rows[source_row]

        if self._standard_filter and row[_COL_STANDARD] != self._standard_filter:
            return False

        if self._text_filter:
            return self._text_filter in src._search_strings[source_row]

        return True

    def lessThan(self, left: QtCore.QModelIndex, right: QtCore.QModelIndex) -> bool:
        col = left.column()
        if col == _COL_STANDARD:
            src = self.sourceModel()
            ls = src._rows[left.row()][_COL_STANDARD]
            rs = src._rows[right.row()][_COL_STANDARD]
            lr, rr = _standard_rank(ls), _standard_rank(rs)
            if lr != rr:
                return lr < rr
            return ls < rs  # tie-break alphabetically (unknown standards)
        if col in _NUMERIC_COLS:
            # Sort by the underlying float value stored in the SteelPreset,
            # not the formatted string — keeps numeric ordering correct.
            src = self.sourceModel()
            lp = src.preset_at(left.row())
            rp = src.preset_at(right.row())
            lv = _preset_sort_key(lp, col)
            rv = _preset_sort_key(rp, col)
            return lv < rv
        return super().lessThan(left, right)


def _preset_sort_key(p: SteelPreset, col: int) -> float:
    if col == _COL_E:        return p.E
    if col == _COL_SIGMA_Y:  return p.sigma_y
    if col == _COL_SIGMA_U:  return p.sigma_u
    if col == _COL_EPSILON_U: return p.epsilon_u
    return 0.0


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class SteelPresetDialog(QtWidgets.QDialog):
    """
    Dialog to select a steel preset from the built-in ASTM (and future)
    database.

    After ``exec()`` returns ``Accepted``, call :meth:`selected_preset` to
    retrieve the chosen :class:`~opspro.Materials.presets.steel_presets.SteelPreset`.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Load Steel Preset')
        self.resize(900, 460)
        self._selected: SteelPreset | None = None
        self._setup_ui()
        self._load_data()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_ui(self):
        # ---- source model + proxy ------------------------------------
        self._source_model = _PresetTableModel([], [], self)
        self._proxy = _PresetFilterProxy(self)
        self._proxy.setSourceModel(self._source_model)

        # ---- description label ---------------------------------------
        lbl_desc = QtWidgets.QLabel(
            'Select a structural steel grade to pre-populate the material fields.\n'
            'All values are <b>minimum guaranteed</b> values from the relevant standard. '
            'Use <b>Search</b> or the <b>Standard</b> combo to narrow the list.'
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setTextFormat(QtCore.Qt.RichText)

        # ---- filter row ----------------------------------------------
        top_grid = QtWidgets.QGridLayout()
        top_grid.setSpacing(6)
        top_grid.setColumnStretch(1, 1)

        # Search
        top_grid.addWidget(QtWidgets.QLabel('Search:'), 0, 0)
        self._search_edit = QtWidgets.QLineEdit()
        self._search_edit.setPlaceholderText('Filter across all columns…')
        self._search_edit.setClearButtonEnabled(True)
        self._search_edit.textChanged.connect(self._on_search_text_changed)
        top_grid.addWidget(self._search_edit, 0, 1)

        self._search_timer = QtCore.QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(200)
        self._search_timer.timeout.connect(self._on_search_committed)

        # Standard combo
        filter_inner = QtWidgets.QHBoxLayout()
        filter_inner.setSpacing(6)
        filter_inner.addWidget(QtWidgets.QLabel('Standard:'))
        self._combo_standard = QtWidgets.QComboBox()
        self._combo_standard.setMinimumWidth(100)
        self._combo_standard.currentTextChanged.connect(self._on_standard_changed)
        filter_inner.addWidget(self._combo_standard)
        filter_inner.addStretch()
        top_grid.addWidget(QtWidgets.QLabel('Filter by:'), 1, 0)
        top_grid.addLayout(filter_inner, 1, 1)

        # ---- table view ----------------------------------------------
        self._table = QtWidgets.QTableView()
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self._table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self._table.doubleClicked.connect(self._on_double_click)

        vh = self._table.verticalHeader()
        vh.hide()
        vh.setDefaultSectionSize(22)

        hh = self._table.horizontalHeader()
        hh.setSectionsMovable(True)
        hh.setStretchLastSection(False)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        hh.setSectionResizeMode(_COL_NOTES, QtWidgets.QHeaderView.Stretch)

        # default sort: Standard (canonical order) — within each standard, source order is preserved
        self._proxy.sort(_COL_STANDARD, QtCore.Qt.AscendingOrder)

        # ---- row count label -----------------------------------------
        self._lbl_count = QtWidgets.QLabel()

        # ---- separator -----------------------------------------------
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)

        # ---- button box ----------------------------------------------
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
        )
        self._btn_ok = btn_box.button(QtWidgets.QDialogButtonBox.Ok)
        self._btn_ok.setEnabled(False)          # enabled only when a row is selected
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        # keep OK enabled/disabled in sync with the selection
        self._table.selectionModel().selectionChanged.connect(self._on_selection_changed)

        # ---- main layout --------------------------------------------
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(8, 8, 8, 8)
        vbox.setSpacing(6)
        vbox.addWidget(lbl_desc)
        vbox.addLayout(top_grid)
        vbox.addWidget(self._table)
        vbox.addWidget(self._lbl_count)
        vbox.addWidget(separator)
        vbox.addWidget(btn_box)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_data(self):
        # Flatten presets into parallel lists in canonical order: rows + preset objects
        ordered_keys = _ordered_standards(PRESETS)
        preset_objects: list[SteelPreset] = []
        for key in ordered_keys:
            preset_objects.extend(PRESETS[key])

        rows = _build_rows(PRESETS)
        self._source_model = _PresetTableModel(rows, preset_objects, self)
        self._proxy.setSourceModel(self._source_model)
        self._proxy.sort(_COL_STANDARD, QtCore.Qt.AscendingOrder)

        # Populate standard combo (with flag icons) in canonical order
        self._combo_standard.blockSignals(True)
        self._combo_standard.clear()
        for std in ['All'] + ordered_keys:
            icon = _flag_icon(std)
            if icon is not None:
                self._combo_standard.addItem(icon, std)
            else:
                self._combo_standard.addItem(std)
        self._combo_standard.blockSignals(False)

        self._set_initial_column_widths()
        self._update_count()

    _COLUMN_WIDTHS = {
        _COL_STANDARD:    90,
        _COL_DESIGNATION: 110,
        _COL_NAME:        190,
        _COL_E:            80,
        _COL_SIGMA_Y:      70,
        _COL_SIGMA_U:      70,
        _COL_EPSILON_U:    60,
    }

    def _set_initial_column_widths(self):
        hh = self._table.horizontalHeader()
        for col, width in self._COLUMN_WIDTHS.items():
            hh.resizeSection(col, width)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_search_text_changed(self):
        self._search_timer.start()

    def _on_search_committed(self):
        self._proxy.set_text(self._search_edit.text())
        self._update_count()

    def _on_standard_changed(self, text: str):
        self._proxy.set_standard(text)
        self._update_count()

    def _on_selection_changed(self):
        self._btn_ok.setEnabled(self._table.selectionModel().hasSelection())

    def _on_double_click(self, index: QtCore.QModelIndex):
        if index.isValid():
            self._commit_selection()

    def _on_accepted(self):
        self._commit_selection()

    def _commit_selection(self):
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return
        proxy_row   = indexes[0].row()
        source_row  = self._proxy.mapToSource(self._proxy.index(proxy_row, 0)).row()
        self._selected = self._source_model.preset_at(source_row)
        self.accept()

    def _update_count(self):
        total   = self._source_model.rowCount()
        visible = self._proxy.rowCount()
        self._lbl_count.setText(f'{visible} / {total} grades')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def selected_preset(self) -> SteelPreset | None:
        """Return the chosen :class:`SteelPreset`, or ``None`` if cancelled."""
        return self._selected
