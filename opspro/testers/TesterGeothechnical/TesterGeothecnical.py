from io import StringIO
import os
import traceback

from PySide2 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from opspro.testers.TesterGeothechnical.strain_history import StrainHistoryFactory
from opspro.testers.TesterGeothechnical import tester_utils as tu


STRAIN_COMPONENTS = ['\u03B5\u2081\u2081', '\u03B5\u2082\u2082', '\u03B5\u2083\u2083', '\u03B3\u2081\u2082', '\u03B3\u2082\u2083', '\u03B3\u2081\u2083']
STRESS_COMPONENTS = ['\u03C3\u2081\u2081', '\u03C3\u2082\u2082', '\u03C3\u2083\u2083', '\u03C3\u2081\u2082', '\u03C3\u2082\u2083', '\u03C3\u2081\u2083']
STRAIN_SIZE = 6


def _hline():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


class _CompactScrollArea(QtWidgets.QScrollArea):
    def __init__(self, min_height=70, parent=None):
        super().__init__(parent)
        self._min_height = min_height

    def minimumSizeHint(self):
        return QtCore.QSize(0, self._min_height)

    def sizeHint(self):
        return QtCore.QSize(240, self._min_height)


def _scroll_area(widget, min_height=70):
    scroll = _CompactScrollArea(min_height)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
    scroll.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
    scroll.setWidget(widget)
    scroll.setMinimumWidth(0)
    scroll.setMinimumHeight(min_height)
    scroll.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
    return scroll


def _style_splitter(splitter):
    splitter.setHandleWidth(5)
    splitter.setStyleSheet(
        'QSplitter::handle {'
        'background: #cfcfcf;'
        'border: 1px solid #a8a8a8;'
        'margin: 0;'
        '}'
        'QSplitter::handle:hover {'
        'background: #b9cde8;'
        'border: 1px solid #6d8fbd;'
        '}'
    )


class _CompactDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def textFromValue(self, value):
        text = '{:.12g}'.format(float(value))
        return '0' if text == '-0' else text


class PlotWidget(QtWidgets.QWidget):
    def __init__(
        self,
        xlabel,
        ylabel,
        parent=None,
        toolbar=True,
        compact_toolbar=True,
        preferred_height=150,
    ):
        super().__init__(parent)
        self._preferred_height = preferred_height
        self._figure = Figure(figsize=(4.0, 2.4))
        self._canvas = FigureCanvas(self._figure)
        self._toolbar = NavigationToolbar(self._canvas, self) if toolbar else None
        self._axes = self._figure.add_subplot(111)
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._apply_axes_style()
        self._axes.grid(True, alpha=0.25)
        self._figure.subplots_adjust(left=0.13, right=0.98, bottom=0.24, top=0.94)
        self._pan_start = None
        self._canvas.mpl_connect('scroll_event', self._on_scroll)
        self._canvas.mpl_connect('button_press_event', self._on_button_press)
        self._canvas.mpl_connect('button_release_event', self._on_button_release)
        self._canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self._canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        if self._toolbar is not None:
            if compact_toolbar:
                self._toolbar.setIconSize(QtCore.QSize(16, 16))
                self._toolbar.setMaximumHeight(26)
            layout.addWidget(self._toolbar)
        layout.addWidget(self._canvas)
        self.setMinimumHeight(70)

    def sizeHint(self):
        return QtCore.QSize(400, self._preferred_height)

    def minimumSizeHint(self):
        return QtCore.QSize(120, self.minimumHeight())

    def set_series(self, series):
        self._axes.clear()
        self._apply_axes_style()
        self._axes.grid(True, alpha=0.25)
        has_data = False
        for item in series:
            x = item.get('x', [])
            y = item.get('y', [])
            if x and y:
                has_data = True
                self._axes.plot(
                    x,
                    y,
                    item.get('style', '-'),
                    color=item.get('color', None),
                    linewidth=item.get('linewidth', 1.4),
                    label=item.get('label', None),
                )
        if has_data and any(item.get('label') for item in series):
            self._axes.legend(loc='best', fontsize=7)
        self._figure.subplots_adjust(left=0.13, right=0.98, bottom=0.24, top=0.94)
        self._canvas.draw_idle()

    def _apply_axes_style(self):
        self._axes.set_xlabel(self._xlabel, fontsize=8, labelpad=3)
        self._axes.set_ylabel(self._ylabel, fontsize=8, labelpad=3)
        self._axes.tick_params(axis='both', which='major', labelsize=7, pad=2)

    def _on_scroll(self, event):
        if event.inaxes != self._axes or event.xdata is None or event.ydata is None:
            return
        scale = 0.85 if event.button == 'up' else 1.0 / 0.85
        xmin, xmax = self._axes.get_xlim()
        ymin, ymax = self._axes.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        self._axes.set_xlim(
            xdata - (xdata - xmin) * scale,
            xdata + (xmax - xdata) * scale,
        )
        self._axes.set_ylim(
            ydata - (ydata - ymin) * scale,
            ydata + (ymax - ydata) * scale,
        )
        self._canvas.draw_idle()

    def _on_button_press(self, event):
        if event.inaxes != self._axes or event.button not in (2, 3):
            return
        self._pan_start = {
            'x': event.xdata,
            'y': event.ydata,
            'xlim': self._axes.get_xlim(),
            'ylim': self._axes.get_ylim(),
        }

    def _on_button_release(self, event):
        self._pan_start = None

    def _on_motion(self, event):
        if self._pan_start is None or event.inaxes != self._axes:
            return
        if event.xdata is None or event.ydata is None:
            return
        dx = event.xdata - self._pan_start['x']
        dy = event.ydata - self._pan_start['y']
        xmin, xmax = self._pan_start['xlim']
        ymin, ymax = self._pan_start['ylim']
        self._axes.set_xlim(xmin - dx, xmax - dx)
        self._axes.set_ylim(ymin - dy, ymax - dy)
        self._canvas.draw_idle()


class ReferenceDataDialog(QtWidgets.QDialog):
    def __init__(self, strain_size=STRAIN_SIZE, current_results=None, parent=None):
        super().__init__(parent)
        self._strain_size = strain_size
        self._current_results = current_results or ([], [])
        self.strain_data = [[] for _ in range(strain_size)]
        self.stress_data = [[] for _ in range(strain_size)]
        self.setWindowTitle('Load Reference Data')
        self.resize(650, 500)

        layout = QtWidgets.QVBoxLayout(self)
        instructions = QtWidgets.QLabel(
            'Load CSV/text data as repeated strain/stress pairs: '
            '\u03B5\u2081\u2081 \u03C3\u2081\u2081 \u03B5\u2082\u2082 \u03C3\u2082\u2082 ... \u03B3\u2081\u2083 \u03C3\u2081\u2083.'
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        button_layout = QtWidgets.QHBoxLayout()
        self._btn_csv = QtWidgets.QPushButton('Load CSV')
        self._btn_paste = QtWidgets.QPushButton('Paste')
        self._btn_results = QtWidgets.QPushButton('Use Test Results')
        self._btn_clear = QtWidgets.QPushButton('Clear')
        for button in (self._btn_csv, self._btn_paste, self._btn_results, self._btn_clear):
            button_layout.addWidget(button)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)

        self._text = QtWidgets.QPlainTextEdit()
        layout.addWidget(self._text, 1)
        self._status = QtWidgets.QLabel('Ready')
        layout.addWidget(self._status)

        box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        box.accepted.connect(self._on_ok)
        box.rejected.connect(self.reject)
        layout.addWidget(box)

        self._btn_csv.clicked.connect(self._load_csv)
        self._btn_paste.clicked.connect(self._paste)
        self._btn_results.clicked.connect(self._use_results)
        self._btn_clear.clicked.connect(self._text.clear)

    @staticmethod
    def parse_text(text, strain_size=STRAIN_SIZE):
        strain_data = [[] for _ in range(strain_size)]
        stress_data = [[] for _ in range(strain_size)]
        parsed_rows = 0
        for line_number, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            values = [float(value) for value in line.replace(',', ' ').split()]
            expected = 2 * strain_size
            if len(values) < expected:
                raise ValueError(
                    'Line {} has {} values; expected at least {}'.format(
                        line_number, len(values), expected
                    )
                )
            for i in range(strain_size):
                strain_data[i].append(values[2 * i])
                stress_data[i].append(values[2 * i + 1])
            parsed_rows += 1
        if parsed_rows == 0:
            raise ValueError('No valid data rows found')
        return strain_data, stress_data

    def _load_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open CSV file', '', 'CSV Files (*.csv);;All Files (*)'
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as file:
                self._text.setPlainText(file.read())
            self._status.setText('Loaded {}'.format(os.path.basename(path)))
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, 'Error', str(exc))

    def _paste(self):
        text = QtWidgets.QApplication.clipboard().text()
        if text:
            self._text.setPlainText(text)
            self._status.setText('Pasted from clipboard')

    def _use_results(self):
        strain, stress = self._current_results
        if not strain or not strain[0]:
            QtWidgets.QMessageBox.warning(self, 'No results', 'Run a test before using current results.')
            return
        rows = []
        for row in range(len(strain[0])):
            values = []
            for i in range(self._strain_size):
                values.append(str(strain[i][row]))
                values.append(str(stress[i][row]))
            rows.append(' '.join(values))
        self._text.setPlainText('\n'.join(rows))
        self._status.setText('Loaded {} rows from current results'.format(len(rows)))

    def _on_ok(self):
        try:
            self.strain_data, self.stress_data = self.parse_text(
                self._text.toPlainText(), self._strain_size
            )
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, 'Invalid data', str(exc))
            return
        self.accept()


class GeotechnicalTestRunner(QtCore.QObject):
    resultReady = QtCore.Signal(float, object, object)
    logLine = QtCore.Signal(str)
    error = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(self, material, lch, components, time_history, strain_history, parent=None):
        super().__init__(parent)
        self.material = material
        self.lch = lch
        self.components = components
        self.time_history = list(time_history)
        self.strain_history = list(strain_history)
        self.strain = []
        self.stress = []

    @QtCore.Slot()
    def run(self):
        try:
            command, temp_dir, script_file, output_file = self._prepare_test()
            rel_script = os.path.relpath(script_file, temp_dir)
            self.logLine.emit('Running OpenSees: {}'.format(command))
            for line in tu.execute_async([command, rel_script], temp_dir):
                parsed = tu.parse_result_line(line, STRAIN_SIZE)
                if parsed is None:
                    self.logLine.emit(line)
                    continue
                percentage, strain, stress = parsed
                self.strain.append(strain)
                self.stress.append(stress)
                self.resultReady.emit(percentage, strain, stress)
            for path in (script_file, output_file):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass
        except Exception:
            self.error.emit(traceback.format_exc())
        finally:
            self.finished.emit()

    def _prepare_test(self):
        if not self.strain_history:
            raise ValueError('No strain history provided to the tester')

        try:
            import PyMpc
            import PyMpc.App
            from PyMpc import MpcStandardPaths
        except Exception as exc:
            raise RuntimeError('PyMpc is required to run OpenSees from the tester') from exc

        command = PyMpc.App.currentSolverCommand()
        if not command:
            raise RuntimeError('No external OpenSees solver kit is configured')

        temp_dir = '{}{}TesterGeotechnical'.format(MpcStandardPaths.getStandardPathDataLocation(), os.sep)
        temp_dir = temp_dir.replace('\\', '/')
        os.makedirs(temp_dir, exist_ok=True)
        script_file = tu.normalize_path(os.path.join(temp_dir, 'script.tcl'))
        output_file = tu.normalize_path(os.path.join(temp_dir, 'output.txt'))
        template_file = os.path.join(os.path.dirname(__file__), 'template_geotechnical_drained.tcl')

        with open(template_file, 'r', encoding='utf-8') as file:
            template = file.read()

        material_buffer, material_tag = self._write_materials_for_tester(PyMpc, temp_dir)

        flags1 = []
        flags2 = []
        imps = []
        for component in self.components:
            flags1.append(str(component.control))
            flags2.append(str(component.type))
            imps.append(str(component.value))

        script = (
            template.replace('__materials__', material_buffer.getvalue())
            .replace('__lch__', str(float(self.lch)))
            .replace('__tag__', str(material_tag))
            .replace('__time__', tu.list_to_tcl_string(self.time_history))
            .replace('__strain__', tu.list_to_tcl_string(self.strain_history))
            .replace('__flags1__', ' '.join(flags1))
            .replace('__flags2__', ' '.join(flags2))
            .replace('__imps__', ' '.join(imps))
            .replace('__out__', os.path.relpath(output_file, temp_dir).replace('\\', '/'))
        )

        with open(script_file, 'w', encoding='utf-8') as file:
            file.write(script)
        return command, temp_dir, script_file, output_file

    def _write_materials_for_tester(self, PyMpc, temp_dir):
        material_buffer = StringIO()
        legacy_result = self._try_write_legacy_physical_properties(PyMpc, temp_dir, material_buffer)
        if legacy_result is not None:
            return material_buffer, legacy_result

        material_tag = int(getattr(self.material, 'id', 1) or 1)
        if not hasattr(self.material, 'write_tcl_for_tester'):
            raise RuntimeError('Material does not provide write_tcl_for_tester(out_file, tag)')
        returned_tag = self.material.write_tcl_for_tester(material_buffer, material_tag)
        return material_buffer, int(returned_tag or material_tag)

    def _try_write_legacy_physical_properties(self, PyMpc, temp_dir, material_buffer):
        materials = self.material
        if not hasattr(materials, 'items') or not hasattr(materials, 'getlastkey'):
            return None
        try:
            import opspro.testers.TesterGeothechnical.tcl_input as tclin
            import opspro.testers.TesterGeothechnical.write_physical_properties as write_physical_properties
        except Exception:
            return None

        pinfo = tclin.process_info()
        pinfo.out_dir = temp_dir
        try:
            doc = PyMpc.App.caeDocument()
            pinfo.next_physicalProperties_id = doc.physicalProperties.getlastkey(0) + 1
        except Exception:
            pass
        pinfo.out_file = material_buffer
        pinfo.ptype = tclin.process_type.writing_tcl_for_material_tester
        write_physical_properties.write_physical_properties(materials, pinfo, 'materials')
        pinfo.out_file = None
        return materials.getlastkey(0)


class GeotechnicalTesterWidget(QtWidgets.QWidget):
    def __init__(self, material=None, material_factory=None, parent=None):
        super().__init__(parent)
        self._material_factory = material_factory
        self._thread = None
        self._runner = None
        self._strain_results = [[] for _ in range(STRAIN_SIZE)]
        self._stress_results = [[] for _ in range(STRAIN_SIZE)]
        self._reference_strain = [[] for _ in range(STRAIN_SIZE)]
        self._reference_stress = [[] for _ in range(STRAIN_SIZE)]
        self._build_ui()
        self._set_defaults()
        if material is not None:
            self.set_state(getattr(material, 'tester_state', {}) or {})
        self._update_history()
        self._update_components()
        self._update_result_plots()

    def _build_ui(self):
        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(4)

        title = QtWidgets.QLabel('Geotechnical Material Test')
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet('color: #003399; font-size: 11pt;')
        main.addWidget(title)

        description = QtWidgets.QLabel(
            'Here you can test your geotechnical material. After defining material parameters, '
            'choose a strain history and run the test. Material response will show in the chart below.'
        )
        description.setAlignment(QtCore.Qt.AlignCenter)
        description.setWordWrap(True)
        main.addWidget(description)

        note = QtWidgets.QLabel(
            '<i><b>Note:</b> to run the test you need to have at least one external solver kit properly set up.</i>'
        )
        note.setAlignment(QtCore.Qt.AlignCenter)
        note.setWordWrap(True)
        main.addWidget(note)
        main.addWidget(_hline())

        self._history_type = QtWidgets.QComboBox()
        self._history_type.addItems(StrainHistoryFactory.getTypes())
        self._cycles = QtWidgets.QSpinBox()
        self._cycles.setRange(1, 1000)
        self._divisions = QtWidgets.QSpinBox()
        self._divisions.setRange(1, 1000000)
        self._target = _CompactDoubleSpinBox()
        self._target.setDecimals(8)
        self._target.setRange(-1.0e6, 1.0e6)
        self._target.setSingleStep(0.001)
        self._scale_pos = _CompactDoubleSpinBox()
        self._scale_pos.setDecimals(4)
        self._scale_pos.setRange(-1000.0, 1000.0)
        self._scale_neg = _CompactDoubleSpinBox()
        self._scale_neg.setDecimals(4)
        self._scale_neg.setRange(-1000.0, 1000.0)
        self._test_type = QtWidgets.QComboBox()
        self._test_type.addItem('Drained Triaxial')
        self._tested_component = QtWidgets.QComboBox()
        self._tested_component.addItems(STRAIN_COMPONENTS)
        self._lch = _CompactDoubleSpinBox()
        self._lch.setDecimals(6)
        self._lch.setRange(1.0e-12, 1.0e12)
        self._lch.setValue(1.0)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)
        main.addLayout(top_layout, 1)

        form_frame = QtWidgets.QFrame()
        form_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        form_frame.setMinimumSize(QtCore.QSize(235, 168))
        form_frame.setMaximumWidth(285)
        form_frame.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        form_widget = QtWidgets.QWidget()
        form_frame_layout = QtWidgets.QVBoxLayout(form_frame)
        form_frame_layout.setContentsMargins(0, 0, 0, 0)
        form_frame_layout.addWidget(form_widget)
        form = QtWidgets.QGridLayout(form_widget)
        form.setContentsMargins(4, 4, 4, 4)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(4)
        fields = [
            ('Type', self._history_type),
            ('Cycles:', self._cycles),
            ('Divisions:', self._divisions),
            ('Target strain:', self._target),
            ('Test type:', self._test_type),
            ('Pos scale:', self._scale_pos),
            ('Neg scale:', self._scale_neg),
        ]
        for index, (label, widget) in enumerate(fields):
            form.addWidget(QtWidgets.QLabel(label), index, 0)
            form.addWidget(widget, index, 1)
            widget.setMinimumWidth(150)
        form.setColumnStretch(1, 1)
        form.setRowStretch(len(fields), 1)

        form_scroll = _scroll_area(form_frame, min_height=168)
        form_scroll.setMinimumWidth(245)
        form_scroll.setMaximumWidth(300)
        form_scroll.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        top_layout.addWidget(form_scroll, 0, QtCore.Qt.AlignTop)

        self._history_plot = PlotWidget('Pseudo-time', 'Strain', preferred_height=170)
        self._history_plot.setMinimumHeight(145)
        history_container = QtWidgets.QFrame()
        history_container.setFrameShape(QtWidgets.QFrame.StyledPanel)
        history_container.setMinimumSize(QtCore.QSize(260, 185))
        history_container.setMaximumHeight(245)
        history_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        history_layout = QtWidgets.QVBoxLayout(history_container)
        history_layout.setContentsMargins(4, 4, 4, 4)
        history_layout.setSpacing(2)
        history_layout.addWidget(self._history_plot, 1)
        lch_layout = QtWidgets.QHBoxLayout()
        lch_layout.setContentsMargins(0, 0, 0, 0)
        lch_layout.setSpacing(4)
        lch_layout.addWidget(QtWidgets.QLabel('Lch'))
        self._lch.setMinimumWidth(120)
        lch_layout.addWidget(self._lch)
        lch_layout.addStretch(1)
        history_layout.addLayout(lch_layout)
        top_layout.addWidget(history_container, 1)

        component_widget = QtWidgets.QFrame()
        component_widget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        component_layout = QtWidgets.QGridLayout(component_widget)
        component_layout.setContentsMargins(6, 6, 6, 6)
        component_layout.setHorizontalSpacing(4)
        component_layout.setVerticalSpacing(2)
        component_widget.setMinimumSize(QtCore.QSize(245, 185))
        component_widget.setMaximumWidth(330)
        component_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        component_layout.addWidget(QtWidgets.QLabel('<b>Reference Values</b>'), 0, 0, 1, 4)
        component_layout.addWidget(QtWidgets.QLabel('Type'), 1, 0, 1, 2)
        component_layout.addWidget(QtWidgets.QLabel('Reference'), 1, 2, 1, 2)
        self._strain_buttons = []
        self._stress_buttons = []
        self._value_widgets = []
        self._tested_labels = []
        self._button_groups = []
        for i in range(STRAIN_SIZE):
            strain_button = QtWidgets.QRadioButton()
            strain_button.setText(STRAIN_COMPONENTS[i])
            stress_button = QtWidgets.QRadioButton()
            stress_button.setText(STRESS_COMPONENTS[i])
            group = QtWidgets.QButtonGroup(self)
            group.addButton(strain_button)
            group.addButton(stress_button)
            self._button_groups.append(group)
            strain_button.setEnabled(False)
            stress_button.setChecked(True)
            value_widget = _CompactDoubleSpinBox()
            value_widget.setDecimals(8)
            value_widget.setRange(-1.0e18, 1.0e18)
            value_widget.setMinimumWidth(72)
            value_widget.setValue(0.0)
            tested_label = QtWidgets.QLabel('(Tested)')
            tested_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            row = i + 2
            component_layout.addWidget(strain_button, row, 0)
            component_layout.addWidget(stress_button, row, 1)
            component_layout.addWidget(value_widget, row, 2)
            component_layout.addWidget(tested_label, row, 3)
            self._strain_buttons.append(strain_button)
            self._stress_buttons.append(stress_button)
            self._value_widgets.append(value_widget)
            self._tested_labels.append(tested_label)
            strain_button.toggled.connect(self._update_components)
            stress_button.toggled.connect(self._update_components)
            value_widget.valueChanged.connect(self._update_components)
        component_layout.setColumnStretch(2, 1)

        self._result_tabs = QtWidgets.QTabWidget()
        self._result_tabs.setStyleSheet('QTabWidget::pane { border: 1px solid #9f9f9f; }')
        self._result_tabs.setMinimumSize(QtCore.QSize(360, 210))
        self._result_tabs.setMaximumHeight(280)
        self._result_tabs.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self._result_plots = []
        for i in range(STRAIN_SIZE):
            plot = PlotWidget(STRAIN_COMPONENTS[i], STRESS_COMPONENTS[i], preferred_height=190)
            plot.setMinimumHeight(145)
            self._result_plots.append(plot)
            self._result_tabs.addTab(plot, '{}/{}'.format(STRAIN_COMPONENTS[i], STRESS_COMPONENTS[i]))
        result_container = QtWidgets.QWidget()
        result_container.setMinimumHeight(210)
        result_container.setMaximumHeight(310)
        result_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        result_layout = QtWidgets.QHBoxLayout(result_container)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(6)
        result_layout.addWidget(component_widget, 3, QtCore.Qt.AlignTop)
        result_layout.addWidget(self._result_tabs, 9)
        main.addWidget(result_container, 2)

        bottom = QtWidgets.QGridLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setHorizontalSpacing(8)
        bottom.setVerticalSpacing(4)
        self._test_button = QtWidgets.QPushButton('Test')
        self._data_button = QtWidgets.QPushButton('Data...')
        self._reference_button = QtWidgets.QPushButton('Reference Data...')
        self._use_results_button = QtWidgets.QPushButton('Use Results as Calibration')
        self._clear_reference_button = QtWidgets.QPushButton('Clear Reference Data')
        self._progress = QtWidgets.QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setTextVisible(True)
        for button in (self._test_button, self._data_button):
            button.setMinimumWidth(90)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        for button in (self._reference_button, self._use_results_button, self._clear_reference_button):
            button.setMinimumWidth(160)
            button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        bottom.addWidget(self._test_button, 0, 0, 1, 2)
        bottom.addWidget(self._data_button, 0, 2, 1, 2)
        bottom.addWidget(self._reference_button, 0, 4, 1, 8)
        bottom.addWidget(self._use_results_button, 1, 0, 1, 3)
        bottom.addWidget(self._clear_reference_button, 1, 3, 1, 3)
        bottom.addWidget(self._progress, 1, 6, 1, 6)
        for col in range(12):
            bottom.setColumnStretch(col, 1)
        main.addLayout(bottom)

        self._log = QtWidgets.QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(90)
        self._log.setVisible(False)
        main.addWidget(self._log)

        self._history_type.currentTextChanged.connect(self._on_history_type_changed)
        self._cycles.valueChanged.connect(self._update_history)
        self._divisions.valueChanged.connect(self._update_history)
        self._target.valueChanged.connect(self._update_history)
        self._scale_pos.valueChanged.connect(self._update_history)
        self._scale_neg.valueChanged.connect(self._update_history)
        self._tested_component.currentIndexChanged.connect(self._update_components)
        self._test_button.clicked.connect(self._on_test_clicked)
        self._data_button.clicked.connect(self._show_data)
        self._reference_button.clicked.connect(self._load_reference_data)
        self._use_results_button.clicked.connect(self._use_results_as_reference)
        self._clear_reference_button.clicked.connect(self._clear_reference_data)

    @staticmethod
    def _centered(widget):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        layout.addWidget(widget)
        layout.addStretch(1)
        return container

    def _set_defaults(self):
        self._history_type.setCurrentText('CyclicAsymmetric')
        self._target.setValue(-0.003)
        self._scale_pos.setValue(1.0)
        self._scale_neg.setValue(1.0)
        self._on_history_type_changed(self._history_type.currentText())

    def _on_history_type_changed(self, history_name):
        history = StrainHistoryFactory.make(history_name)
        params = history.getDefaultParams()
        blockers = [
            QtCore.QSignalBlocker(self._cycles),
            QtCore.QSignalBlocker(self._divisions),
            QtCore.QSignalBlocker(self._scale_pos),
            QtCore.QSignalBlocker(self._scale_neg),
        ]
        self._cycles.setValue(params.num_cycles)
        self._cycles.setEnabled(params.num_cycles_editable)
        self._divisions.setValue(params.num_divisions)
        self._scale_pos.setValue(params.scale_pos)
        self._scale_neg.setValue(params.scale_neg)
        del blockers
        self._update_history()

    def _make_history(self):
        history = StrainHistoryFactory.make(self._history_type.currentText())
        params = history.getDefaultParams()
        params.num_cycles = self._cycles.value()
        params.num_divisions = self._divisions.value()
        params.target_strain = self._target.value()
        params.scale_pos = self._scale_pos.value()
        params.scale_neg = self._scale_neg.value()
        history.build(params)
        time = []
        if len(history.strain) > 1:
            step = 1.0 / float(len(history.strain) - 1)
            time = [i * step for i in range(len(history.strain))]
        else:
            time = [0.0 for _ in history.strain]
        return time, history.strain

    @QtCore.Slot()
    def _update_history(self):
        try:
            self._time_history, self._strain_history = self._make_history()
        except Exception as exc:
            self._time_history = [0.0]
            self._strain_history = [0.0]
            self._append_log(str(exc))
        self._history_plot.set_series([
            {'x': self._time_history, 'y': self._strain_history, 'color': '#2f76d2', 'label': 'Strain'}
        ])

    @QtCore.Slot()
    def _update_components(self):
        tested = self._tested_component.currentIndex()
        for i in range(STRAIN_SIZE):
            is_tested = i == tested
            self._strain_buttons[i].setEnabled(False)
            self._stress_buttons[i].setEnabled(True)
            if not self._stress_buttons[i].isChecked():
                self._stress_buttons[i].setChecked(True)
            self._value_widgets[i].setEnabled(not is_tested)
            self._tested_labels[i].setVisible(is_tested)

    def _component_data(self):
        tested = self._tested_component.currentIndex()
        data = []
        for i in range(STRAIN_SIZE):
            component = tu.TensorComponentData()
            if self._stress_buttons[i].isChecked():
                component.control = tu.TensorComponentData.STRESS
            if i == tested:
                component.control = tu.TensorComponentData.STRAIN
                component.type = tu.TensorComponentData.TESTED
            component.value = self._value_widgets[i].value()
            data.append(component)
        return data

    def state(self):
        return {
            'history_type': self._history_type.currentText(),
            'num_cycles': self._cycles.value(),
            'num_divisions': self._divisions.value(),
            'target_strain': self._target.value(),
            'scale_positive': self._scale_pos.value(),
            'scale_negative': self._scale_neg.value(),
            'tested_component': self._tested_component.currentIndex(),
            'lch': self._lch.value(),
            'components_strain_control': [button.isChecked() for button in self._strain_buttons],
            'components_values': [widget.value() for widget in self._value_widgets],
            'reference_strain': [list(values) for values in self._reference_strain],
            'reference_stress': [list(values) for values in self._reference_stress],
        }

    def set_state(self, state):
        if not isinstance(state, dict):
            return
        history_type = state.get('history_type', state.get('name', None))
        if history_type in StrainHistoryFactory.getTypes():
            self._history_type.setCurrentText(history_type)
        self._cycles.setValue(int(state.get('num_cycles', state.get('num_cycl', self._cycles.value()))))
        self._divisions.setValue(int(state.get('num_divisions', state.get('num_div', self._divisions.value()))))
        self._target.setValue(float(state.get('target_strain', self._target.value())))
        self._scale_pos.setValue(float(state.get('scale_positive', self._scale_pos.value())))
        self._scale_neg.setValue(float(state.get('scale_negative', self._scale_neg.value())))
        self._tested_component.setCurrentIndex(int(state.get('tested_component', state.get('tested_comp', 0))))
        self._lch.setValue(float(state.get('lch', self._lch.value())))

        controls = state.get('components_strain_control', state.get('components_types', None))
        if controls:
            for value, strain_button, stress_button in zip(controls, self._strain_buttons, self._stress_buttons):
                strain_button.setChecked(bool(value))
                stress_button.setChecked(not bool(value))
        values = state.get('components_values', None)
        if values:
            for value, widget in zip(values, self._value_widgets):
                widget.setValue(float(value))
        ref_strain = state.get('reference_strain', None)
        ref_stress = state.get('reference_stress', None)
        if ref_strain and ref_stress:
            self._reference_strain = [list(values) for values in ref_strain[:STRAIN_SIZE]]
            self._reference_stress = [list(values) for values in ref_stress[:STRAIN_SIZE]]
            while len(self._reference_strain) < STRAIN_SIZE:
                self._reference_strain.append([])
            while len(self._reference_stress) < STRAIN_SIZE:
                self._reference_stress.append([])
        self._update_history()
        self._update_components()
        self._update_result_plots()

    def _current_material(self):
        if self._material_factory is None:
            raise RuntimeError('No material provider is configured for the tester')
        return self._material_factory()

    def _on_test_clicked(self):
        try:
            material = self._current_material()
            if not self._strain_history or abs(self._target.value()) < 1.0e-18:
                raise ValueError('Target strain must be different from zero')
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, 'Cannot run test', str(exc))
            return

        self._strain_results = [[] for _ in range(STRAIN_SIZE)]
        self._stress_results = [[] for _ in range(STRAIN_SIZE)]
        self._progress.setValue(0)
        self._log.clear()
        self._update_result_plots()
        self._set_running(True)

        self._thread = QtCore.QThread(self)
        self._runner = GeotechnicalTestRunner(
            material,
            self._lch.value(),
            self._component_data(),
            self._time_history,
            self._strain_history,
        )
        self._runner.moveToThread(self._thread)
        self._thread.started.connect(self._runner.run)
        self._runner.resultReady.connect(self._on_result_ready)
        self._runner.logLine.connect(self._append_log)
        self._runner.error.connect(self._on_runner_error)
        self._runner.finished.connect(self._thread.quit)
        self._runner.finished.connect(self._runner.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    @QtCore.Slot(float, object, object)
    def _on_result_ready(self, percentage, strain, stress):
        for i in range(STRAIN_SIZE):
            self._strain_results[i].append(strain[i])
            self._stress_results[i].append(stress[i])
        self._progress.setValue(int(round(percentage * 100.0)))
        self._update_result_plots()

    @QtCore.Slot(str)
    def _on_runner_error(self, message):
        self._append_log(message)
        QtWidgets.QMessageBox.warning(self, 'Tester error', message.splitlines()[-1] if message else 'Unknown error')

    @QtCore.Slot(str)
    def _append_log(self, message):
        self._log.setVisible(True)
        self._log.appendPlainText(message)

    @QtCore.Slot()
    def _on_thread_finished(self):
        self._set_running(False)
        self._thread = None
        self._runner = None

    def _set_running(self, running):
        for widget in (
            self._test_button,
            self._data_button,
            self._reference_button,
            self._use_results_button,
            self._clear_reference_button,
        ):
            widget.setEnabled(not running)

    def _update_result_plots(self):
        for i, plot in enumerate(self._result_plots):
            plot.set_series([
                {
                    'x': self._reference_strain[i],
                    'y': self._reference_stress[i],
                    'color': '#d62728',
                    'style': '--',
                    'linewidth': 1.0,
                    'label': 'Reference',
                },
                {
                    'x': self._strain_results[i],
                    'y': self._stress_results[i],
                    'color': '#2f76d2',
                    'label': 'Test',
                },
            ])

    def _show_data(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Tester Data')
        dialog.resize(850, 500)
        layout = QtWidgets.QVBoxLayout(dialog)
        table = QtWidgets.QTableWidget()
        table.setColumnCount(2 * STRAIN_SIZE)
        labels = []
        for strain_label, stress_label in zip(STRAIN_COMPONENTS, STRESS_COMPONENTS):
            labels.extend([strain_label, stress_label])
        table.setHorizontalHeaderLabels(labels)
        count = len(self._strain_results[0]) if self._strain_results else 0
        table.setRowCount(count)
        for row in range(count):
            for col in range(STRAIN_SIZE):
                table.setItem(row, 2 * col, QtWidgets.QTableWidgetItem(str(self._strain_results[col][row])))
                table.setItem(row, 2 * col + 1, QtWidgets.QTableWidgetItem(str(self._stress_results[col][row])))
        layout.addWidget(table)
        box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        box.rejected.connect(dialog.reject)
        layout.addWidget(box)
        dialog.exec_()

    def _load_reference_data(self):
        dialog = ReferenceDataDialog(
            STRAIN_SIZE,
            current_results=(self._strain_results, self._stress_results),
            parent=self,
        )
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self._reference_strain = dialog.strain_data
            self._reference_stress = dialog.stress_data
            self._update_result_plots()

    def _use_results_as_reference(self):
        if not self._strain_results or not self._strain_results[0]:
            QtWidgets.QMessageBox.warning(self, 'No results', 'Run a test before storing calibration data.')
            return
        self._reference_strain = [list(values) for values in self._strain_results]
        self._reference_stress = [list(values) for values in self._stress_results]
        self._update_result_plots()

    def _clear_reference_data(self):
        self._reference_strain = [[] for _ in range(STRAIN_SIZE)]
        self._reference_stress = [[] for _ in range(STRAIN_SIZE)]
        self._update_result_plots()


__all__ = [
    'GeotechnicalTesterWidget',
    'GeotechnicalTestRunner',
    'ReferenceDataDialog',
    'STRAIN_COMPONENTS',
    'STRESS_COMPONENTS',
]
