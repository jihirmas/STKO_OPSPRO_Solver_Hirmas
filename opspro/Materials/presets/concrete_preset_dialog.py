"""
concrete_preset_dialog.py
-------------------------
QDialog that lets the user pick a concrete class from the presets database.

Layout
------
* Description label.
* Search box  +  Standard combo  — filter controls at the top.
* Sortable / filterable QTableView showing all preset classes.
* Row-count label.
* OK / Cancel buttons.

Columns
-------
0  Standard     str   e.g. "EN 1992"
1  Designation  str   e.g. "C30/37"
2  Name         str   e.g. "EN 1992 C30/37"
3  E            str   e.g. "32.8 GPa"
4  fcp          str   e.g. "30 MPa"
5  ft           str   e.g. "2.90 MPa"
6  Gt           str   e.g. "135 J/m²"
7  Gc           str   e.g. "33600 J/m²"
8  Notes        str   normative reference

Usage
-----
::

    dlg = ConcretePresetDialog(parent=parent_widget)
    if dlg.exec() == QtWidgets.QDialog.Accepted:
        preset = dlg.selected_preset()   # ConcretePreset | None
"""

import pkgutil

from PySide2 import QtCore, QtGui, QtWidgets

from opspro.Materials.presets.concrete_presets import PRESETS, ConcretePreset


# ---------------------------------------------------------------------------
# Flag icons
# ---------------------------------------------------------------------------

_STANDARD_FLAG_FILE = {
    'ACI 318':   'flag_USA.png',
    'EN 1992':   'flag_EU.png',
    'GB 50010':  'flag_CHN.png',
    'CSA A23.3': 'flag_CAN.png',
}

_STANDARD_ORDER = ['ACI 318', 'EN 1992', 'GB 50010', 'CSA A23.3']


def _standard_rank(std):
    try:
        return _STANDARD_ORDER.index(std)
    except ValueError:
        return len(_STANDARD_ORDER)


def _ordered_standards(presets):
    ordered = [k for k in _STANDARD_ORDER if k in presets]
    ordered += sorted(k for k in presets if k not in _STANDARD_ORDER)
    return ordered


_flag_pixmap_cache = {}


def _flag_icon(standard):
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
_COL_FCP         = 4
_COL_FT          = 5
_COL_GT          = 6
_COL_GC          = 7
_COL_NOTES       = 8

_HEADERS = [
    'Standard',
    'Designation',
    'Name',
    'E',
    'f\u1d9c\u209a',   # fcp
    'f\u209c',         # ft
    'G\u209c',         # Gt
    'G\u1d9c',         # Gc
    'Notes',
]

_NUMERIC_COLS = {_COL_E, _COL_FCP, _COL_FT, _COL_GT, _COL_GC}


# ---------------------------------------------------------------------------
# Helpers — unit formatting
# ---------------------------------------------------------------------------

def _fmt_E(pa):
    return f'{pa / 1e9:.1f} GPa'

def _fmt_stress(pa):
    mpa = pa / 1e6
    if mpa < 10.0:
        return f'{mpa:.2f} MPa'
    return f'{mpa:.1f} MPa'

def _fmt_energy(jm2):
    return f'{jm2:.0f} J/m\u00b2'


# ---------------------------------------------------------------------------
# Row builder
# ---------------------------------------------------------------------------

def _build_rows(presets):
    rows = []
    for standard in _ordered_standards(presets):
        for p in presets[standard]:
            rows.append((
                standard,
                p.designation,
                p.name,
                _fmt_E(p.E),
                _fmt_stress(p.fcp),
                _fmt_stress(p.ft),
                _fmt_energy(p.Gt),
                _fmt_energy(p.Gc),
                p.notes,
            ))
    return rows


# ---------------------------------------------------------------------------
# Table model
# ---------------------------------------------------------------------------

class _PresetTableModel(QtCore.QAbstractTableModel):

    def __init__(self, rows, preset_objects, parent=None):
        super().__init__(parent)
        self._rows    = rows
        self._presets = preset_objects
        self._search_strings = [
            '\t'.join(str(v).lower() for v in row)
            for row in rows
        ]

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

    def preset_at(self, source_row):
        return self._presets[source_row]


# ---------------------------------------------------------------------------
# Sort/filter proxy
# ---------------------------------------------------------------------------

class _PresetFilterProxy(QtCore.QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text_filter     = ''
        self._standard_filter = ''
        self.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def set_text(self, text):
        self._text_filter = text.strip().lower()
        self.invalidateFilter()

    def set_standard(self, label):
        self._standard_filter = label if label != 'All' else ''
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        src = self.sourceModel()
        row = src._rows[source_row]

        if self._standard_filter and row[_COL_STANDARD] != self._standard_filter:
            return False

        if self._text_filter:
            return self._text_filter in src._search_strings[source_row]

        return True

    def lessThan(self, left, right):
        col = left.column()
        if col == _COL_STANDARD:
            src = self.sourceModel()
            ls = src._rows[left.row()][_COL_STANDARD]
            rs = src._rows[right.row()][_COL_STANDARD]
            lr, rr = _standard_rank(ls), _standard_rank(rs)
            if lr != rr:
                return lr < rr
            return ls < rs
        if col in _NUMERIC_COLS:
            src = self.sourceModel()
            lp = src.preset_at(left.row())
            rp = src.preset_at(right.row())
            return _preset_sort_key(lp, col) < _preset_sort_key(rp, col)
        return super().lessThan(left, right)


def _preset_sort_key(p, col):
    if col == _COL_E:   return p.E
    if col == _COL_FCP: return p.fcp
    if col == _COL_FT:  return p.ft
    if col == _COL_GT:  return p.Gt
    if col == _COL_GC:  return p.Gc
    return 0.0


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class ConcretePresetDialog(QtWidgets.QDialog):
    """
    Dialog to select a concrete class from the built-in presets database
    (EN 1992, ACI 318, GB 50010).

    After ``exec()`` returns ``Accepted``, call :meth:`selected_preset` to
    retrieve the chosen :class:`~opspro.Materials.presets.concrete_presets.ConcretePreset`.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Load Concrete Preset')
        self.resize(960, 460)
        self._selected = None
        self._setup_ui()
        self._load_data()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_ui(self):
        self._source_model = _PresetTableModel([], [], self)
        self._proxy = _PresetFilterProxy(self)
        self._proxy.setSourceModel(self._source_model)

        lbl_desc = QtWidgets.QLabel(
            'Select a concrete class to pre-populate the material fields.\n'
            'G\u209c and G\u1d9c are computed via <b>CEB-FIP Model Code 2010</b>: '
            'G\u209c\u202f=\u202f73\u00b7f\u1d9cₚ\u2070\u00b7\u00b9\u2078 [J/m\u00b2], '
            'G\u1d9c\u202f=\u202f250\u00b7G\u209c. '
            'Use <b>Search</b> or the <b>Standard</b> combo to narrow the list.'
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setTextFormat(QtCore.Qt.RichText)

        top_grid = QtWidgets.QGridLayout()
        top_grid.setSpacing(6)
        top_grid.setColumnStretch(1, 1)

        top_grid.addWidget(QtWidgets.QLabel('Search:'), 0, 0)
        self._search_edit = QtWidgets.QLineEdit()
        self._search_edit.setPlaceholderText('Filter across all columns\u2026')
        self._search_edit.setClearButtonEnabled(True)
        self._search_edit.textChanged.connect(self._on_search_text_changed)
        top_grid.addWidget(self._search_edit, 0, 1)

        self._search_timer = QtCore.QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(200)
        self._search_timer.timeout.connect(self._on_search_committed)

        filter_inner = QtWidgets.QHBoxLayout()
        filter_inner.setSpacing(6)
        filter_inner.addWidget(QtWidgets.QLabel('Standard:'))
        self._combo_standard = QtWidgets.QComboBox()
        self._combo_standard.setMinimumWidth(120)
        self._combo_standard.currentTextChanged.connect(self._on_standard_changed)
        filter_inner.addWidget(self._combo_standard)
        filter_inner.addStretch()
        top_grid.addWidget(QtWidgets.QLabel('Filter by:'), 1, 0)
        top_grid.addLayout(filter_inner, 1, 1)

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

        self._proxy.sort(_COL_STANDARD, QtCore.Qt.AscendingOrder)

        self._lbl_count = QtWidgets.QLabel()

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)

        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
        )
        self._btn_ok = btn_box.button(QtWidgets.QDialogButtonBox.Ok)
        self._btn_ok.setEnabled(False)
        btn_box.accepted.connect(self._on_accepted)
        btn_box.rejected.connect(self.reject)

        self._table.selectionModel().selectionChanged.connect(self._on_selection_changed)

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
        ordered_keys = _ordered_standards(PRESETS)
        preset_objects = []
        for key in ordered_keys:
            preset_objects.extend(PRESETS[key])

        rows = _build_rows(PRESETS)
        self._source_model = _PresetTableModel(rows, preset_objects, self)
        self._proxy.setSourceModel(self._source_model)
        self._proxy.sort(_COL_STANDARD, QtCore.Qt.AscendingOrder)

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
        _COL_DESIGNATION: 100,
        _COL_NAME:        170,
        _COL_E:            72,
        _COL_FCP:          72,
        _COL_FT:           72,
        _COL_GT:           80,
        _COL_GC:           88,
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

    def _on_standard_changed(self, text):
        self._proxy.set_standard(text)
        self._update_count()

    def _on_selection_changed(self):
        self._btn_ok.setEnabled(self._table.selectionModel().hasSelection())

    def _on_double_click(self, index):
        if index.isValid():
            self._commit_selection()

    def _on_accepted(self):
        self._commit_selection()

    def _commit_selection(self):
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return
        proxy_row  = indexes[0].row()
        source_row = self._proxy.mapToSource(self._proxy.index(proxy_row, 0)).row()
        self._selected = self._source_model.preset_at(source_row)
        self.accept()

    def _update_count(self):
        total   = self._source_model.rowCount()
        visible = self._proxy.rowCount()
        self._lbl_count.setText(f'{visible} / {total} classes')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def selected_preset(self):
        """Return the chosen :class:`ConcretePreset`, or ``None`` if cancelled."""
        return self._selected
