import pint

from PySide2.QtWidgets import (
    QApplication, QLineEdit, QCompleter,
    QStyle, QStyleOptionFrame
)
from PySide2.QtGui import (
    QStandardItemModel, QStandardItem,
    QColor, QFontMetrics,
    QPainter, QPalette
)
from PySide2.QtCore import (
    Qt, QRegExp, QEvent
)

from opspro.parameters.ParameterManager import ParameterManager

class _expression_gui_utils:
    @staticmethod
    def make_tooltip(value: pint.Quantity) -> str:
        us = ParameterManager.get_unit_system()
        ival = ParameterManager.to_internal(value)
        internal_label = f"Internal ({us.name}):" if us else "SI base units:"
        qstring = ParameterManager.get_common_quantity_name(ival)

        rows = [
            ("Input:",          f"{value:.4g~P}"),
            (internal_label,    f"{ival:.4g~P}"),
            ("Dimensionality:", f"{ival.units.dimensionality:P}"),
        ]
        if qstring is not None:
            rows.append(("Quantity:", qstring))

        td_label = "text-align: right; font-weight: bold; width: 150px; padding: 4px 8px;"
        td_value = "padding: 4px 8px;"
        inner = ''.join(
            f"<tr>"
            f"<td style='{td_label}'>{lbl}</td>"
            f"<td style='{td_value}'>{val}</td>"
            f"</tr>"
            for lbl, val in rows
        )
        return f"<table style='border-collapse: collapse;'>{inner}</table>"

    @staticmethod
    def make_error_tooltip(msg: str) -> str:
        return f"<span style='color: red; font-weight: bold;'>{msg}</span>"

class ExpressionHighlighter:
    """Logic-only syntax highlighter usable on any string."""

    def __init__(self, symbols=None):
        # Define text colors and styles
        # TODO: make configurable
        # TODO: make it static/shared and update it when needed
        self._default_color = QColor("black")
        self._unit_color = QColor(50, 100, 200)
        self._symbol_color = QColor(200, 0, 200)
        self._error_color = QColor("red")

        # Regex rules
        self._rules = []

        # Symbols from list
        if symbols:
            pattern = r"\b(" + "|".join(map(QRegExp.escape, symbols)) + r")\b"
            self._rules.append((QRegExp(pattern), self._symbol_color))

        # Units inside [ ... ]
        self._rules.append((QRegExp(r"\[[^\]]+\]"), self._unit_color))

    def highlight(self, text: str, has_error=False):
        """
        Given text, return a list of (substring, QColor) tuples.
        If has_error=True, all text is red.
        """
        if has_error:
            return [(text, self._error_color)]

        result = []
        last_index = 0

        # Collect matches
        matches = []
        for regex, color in self._rules:
            i = regex.indexIn(text, 0)
            while i >= 0:
                matches.append((i, regex.matchedLength(), color))
                i = regex.indexIn(text, i + regex.matchedLength())

        # Sort by position
        matches.sort(key=lambda m: m[0])

        # Remove overlapping matches (keep first)
        non_overlapping = []
        current_end = -1
        for start, length, color in matches:
            if start >= current_end:
                non_overlapping.append((start, length, color))
                current_end = start + length
            # else: skip because it overlaps

        # Build final segment list
        for start, length, color in non_overlapping:
            if start > last_index:
                result.append((text[last_index:start], self._default_color))
            result.append((text[start:start + length], color))
            last_index = start + length
        if last_index < len(text):
            result.append((text[last_index:], self._default_color))

        # Ensure at least one segment
        if not result:
            result.append((text, self._default_color))

        # done
        return result

class ExpressionLineEdit(QLineEdit):
    # Shared across all instances — built once on first construction.
    # ExpressionHighlighter is stateless during highlight() calls, so sharing is safe.
    _shared_highlighter: 'ExpressionHighlighter' = None

    def __init__(self, parent=None, default_value: pint.Quantity = None):
        super().__init__(parent)

        # Store state
        self._value: pint.Quantity = pint.Quantity(0)
        self._error: str = ""

        if default_value is not None:
            # Preferred unit for display (e.g. Pa, kg/m^3) — taken directly from the
            # default_value so the UI always shows the unit the caller chose.
            self._preferred_unit = default_value.units
            # Non-empty dimensionality → use it to coerce bare numbers at eval time.
            # Dimensionless values have an empty dict as dimensionality, treat as None.
            dim = default_value.dimensionality
            self._default_dimensionality = dim if dim else None
            # Placeholder
            unit_str = format(default_value.units, '~P')
            if unit_str:
                self.setPlaceholderText(f"e.g. {default_value.magnitude:g}[{unit_str}]")
            else:
                self.setPlaceholderText(f"e.g. {default_value.magnitude:g}")
        else:
            self._preferred_unit = None
            self._default_dimensionality = None
            self.setPlaceholderText("e.g. 5")
        self.setClearButtonEnabled(True)

        # Shared syntax highlighter (built once from the static symbol list)
        if ExpressionLineEdit._shared_highlighter is None:
            ExpressionLineEdit._shared_highlighter = ExpressionHighlighter(ParameterManager.all_symbols)
        self._highlighter = ExpressionLineEdit._shared_highlighter

        # Completer
        symbols = ParameterManager.all_symbols
        self._completer = QCompleter(self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        model = QStandardItemModel(self._completer)
        for w in symbols:
            model.appendRow(QStandardItem(w))
        self._completer.setModel(model)

        # Make text transparent to avoid default painting (Active/Inactive only).
        # Disabled is left at its system default and handled by QLineEdit's
        # native disabled-state painting.
        palette = self.palette()
        palette.setColor(QPalette.Active,   QPalette.Text, QColor(0, 0, 0, 0))
        palette.setColor(QPalette.Inactive, QPalette.Text, QColor(0, 0, 0, 0))
        self.setPalette(palette)

        # Connections
        self._completer.activated.connect(self._insert_completion)
        self.textChanged.connect(self._evaluate_expression)

    @property
    def value(self) -> pint.Quantity:
        return self._value

    @property
    def error(self) -> str:
        return self._error

    @property
    def preferred_unit(self):
        """The user-friendly unit derived from default_value (e.g. Pa), or None."""
        return self._preferred_unit

    @property
    def expected_dimensionality(self):
        """Dimensionality derived from default_value, or None for dimensionless/unset."""
        return self._default_dimensionality

    def set_quantity(self, qty: pint.Quantity, keep_unit: bool = False):
        """Set the field text from *qty*.

        Parameters
        ----------
        qty : pint.Quantity
            The value to display.
        keep_unit : bool, optional
            When *True* and the field already contains a valid, non-zero value
            whose dimensionality is compatible with *qty*, the incoming quantity
            is converted to the **existing field unit** before display.  This
            lets procedural updates (preset loading, auto fracture-energy) honour
            whatever unit the user previously typed, instead of overwriting it
            with a different unit representation.

        If a default dimensionality is configured and *qty* has an incompatible
        dimensionality, a warning is printed and the field is reset to zero in
        the preferred unit instead.
        """
        if self._default_dimensionality is not None and qty.dimensionality != self._default_dimensionality:
            pref_str = format(self._preferred_unit, '~') if self._preferred_unit is not None else '?'
            print(
                f"Warning [ExpressionLineEdit.set_quantity]: incompatible dimensionality "
                f"(got {qty.dimensionality:P}, expected {self._default_dimensionality:P}). "
                f"Resetting to 0[{pref_str}]."
            )
            unit = format(self._preferred_unit, '~').replace(' ** ', '^').replace('**', '^') \
                if self._preferred_unit is not None else ''
            self.setText(f"0[{unit}]" if unit else "0")
            return
        # Optionally reuse the unit currently shown in the field.
        if keep_unit and self._value is not None and self._value.magnitude != 0:
            try:
                qty = qty.to(self._value.units)
            except pint.DimensionalityError:
                pass
        # Dimensionality is compatible — display with the (possibly converted) unit.
        unit = format(qty.units, '~').replace(' ** ', '^').replace('**', '^')
        if unit:
            self.setText(f"{qty.magnitude:.6g}[{unit}]")
        else:
            self.setText(f"{qty.magnitude:.6g}")

    def _evaluate_expression(self):
        try:
            expr = self.text()
            if expr.strip():
                val = ParameterManager.evaluate(expr)
                if self._default_dimensionality is not None:
                    if not val.dimensionality:
                        # Bare number — assume the preferred unit (e.g. Pa for E).
                        val = val.magnitude * ParameterManager.get_unit_for(self._default_dimensionality)
                    elif val.dimensionality != self._default_dimensionality:
                        # Unit was provided but has the wrong dimensionality.
                        self._eval_set_error(
                            f"Wrong dimensionality: expected {self._default_dimensionality:P}, "
                            f"got {val.dimensionality:P}."
                        )
                        return
                self._eval_set(val)
            else:
                self._eval_clear()
        except Exception as e:
            self._eval_set_error(str(e))

    def _eval_clear(self):
        self._value = pint.Quantity(0)
        self._error = ""
        self.setToolTip("")

    def _eval_set(self, val: pint.Quantity):
        self._value = val
        self._error = ""
        tooltip_html = _expression_gui_utils.make_tooltip(val)
        self.setToolTip(tooltip_html)

    def _eval_set_error(self, msg: str):
        self._value = pint.Quantity(0)
        self._error = msg
        self.setToolTip(_expression_gui_utils.make_error_tooltip(msg))

    def _insert_completion(self, completion):
        # handle the insertion of the selected completion
        text = self.text()
        pos = self.cursorPosition()
        # Find the start of the "word under cursor"
        start = pos
        while start > 0 and (text[start - 1].isalnum() or text[start - 1] in "_."):
            start -= 1
        # Find the end of the word under cursor
        end = pos
        while end < len(text) and (text[end].isalnum() or text[end] in "_."):
            end += 1
        # Replace the word with the completion
        new_text = text[:start] + completion + text[end:]
        self.setText(new_text)
        # Move cursor to the end of inserted completion
        self.setCursorPosition(start + len(completion))

    def keyPressEvent(self, event):
        try:

            # Force single-line behavior
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                event.ignore()
                return

            # Default QLineEdit behavior
            super().keyPressEvent(event)
            
            # Completer trigger
            if not self._completer or not self._completer.model():
                return
            
            # Find the current "word" (simulate cursor.WordUnderCursor)
            text = self.text()
            pos = self.cursorPosition()
            start = pos
            while start > 0 and (text[start - 1].isalnum() or text[start - 1] in "_."):
                start -= 1
            end = pos
            while end < len(text) and (text[end].isalnum() or text[end] in "_."):
                end += 1
            prefix = text[start:pos]
            if len(prefix) >= 1:
                self._completer.setCompletionPrefix(prefix)
                # Calculate popup position near cursor
                cursor_rect = self.cursorRect()
                popup = self._completer.popup()
                cursor_rect.setWidth(
                    popup.sizeHintForColumn(0)
                    + popup.verticalScrollBar().sizeHint().width()
                )
                self._completer.complete(cursor_rect)
            else:
                self._completer.popup().hide()

        except Exception as e:
            print(f"Error in keyPressEvent: {e}")

    def _paint_highlighted_text(self):
        # get text
        text = self.text()
        if not text:
            return
        
        # Use QApplication.style() rather than self.style(): the per-widget
        # style pointer can be a deleted C++ object during widget teardown.
        app_style = QApplication.style()

        # setup painter
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            # init style option
            opt = QStyleOptionFrame()
            self.initStyleOption(opt)
                
            # clip to text area (QStyle.SE_LineEditContents is a class-level enum
            # constant — safe to use without a live style instance)
            contents_rect = app_style.subElementRect(QStyle.SE_LineEditContents, opt, self)
            painter.setClipRect(contents_rect)

            # text position
            fm = QFontMetrics(self.font())
            x = contents_rect.left() + 2
            y = contents_rect.bottom() - fm.descent() - 1

            # Selection info
            sel_start = self.selectionStart()
            sel_len = len(self.selectedText())
            sel_end = sel_start + sel_len if sel_len > 0 else -1

            # highlight
            if self.isEnabled():
                segments = self._highlighter.highlight(text, has_error=bool(self._error))
            else:
                segments = [(text, self.palette().color(QPalette.Disabled, QPalette.Text))]

            text_index = 0
            for token, color in segments:
                token_len = len(token)
                token_start = text_index
                token_end = token_start + token_len
                # If no selection or token fully outside selection
                if sel_len == 0 or token_end <= sel_start or token_start >= sel_end:
                    hadv = fm.horizontalAdvance(token)
                    painter.setPen(color)
                    painter.drawText(x, y, token)
                    x += hadv
                else:
                    # There is an overlap — split the token visually
                    for i, ch in enumerate(token):
                        idx = token_start + i
                        in_selection = sel_start <= idx < sel_end
                        hadv = fm.horizontalAdvance(ch)
                        if not in_selection:
                            painter.setPen(color)
                            painter.drawText(x, y, ch)
                        x += hadv
                text_index += token_len
        finally:
            painter.end()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.isEnabled():
            return
        try:
            self._paint_highlighted_text()
        except Exception as e:
            print(f"Error in paintEvent: {e}")

    def event(self, e):
        # Intercept Tab key before default focus handling
        try:
            if (
                e.type() == QEvent.KeyPress
                and e.key() == Qt.Key_Tab
                and self._completer
                and self._completer.popup()
                and self._completer.popup().isVisible()
            ):
                popup = self._completer.popup()
                index = popup.currentIndex()
                if not index.isValid() and self._completer.completionCount() > 0:
                    # Select first item in the popup
                    first_index = self._completer.completionModel().index(0, 0)
                    popup.setCurrentIndex(first_index)
                self._completer.popup().hide()
                self._completer.activated.emit(self._completer.currentCompletion())
                return True  # mark event as handled
        except Exception as e:
            print(f"Error in event handling: {e}")
        # default behavior
        return super().event(e)



def example_expression_line_edit():
    # get current application
    #app = QApplication.instance()
    # make a QDialog with the name of the application as title
    from PySide2.QtWidgets import QDialog, QVBoxLayout, QLineEdit
    dialog = QDialog()
    #dialog.setWindowTitle(app.applicationName())
    dialog.setLayout(QVBoxLayout())
    # w = ExpressionLineEdit()
    # dialog.layout().addWidget(w)
    # dialog.layout().addWidget(QLineEdit())
    # add a spacer
    from PySide2.QtWidgets import QSpacerItem, QSizePolicy
    dialog.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    # execute the dialog
    dialog.exec_()
