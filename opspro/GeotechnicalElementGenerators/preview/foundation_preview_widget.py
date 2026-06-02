from PySide2 import QtCore, QtGui, QtWidgets

from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode


class FoundationPreviewWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dimension_mode = DimensionMode.TWO_D
        self._summary = {}
        self.setMinimumSize(300, 260)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def set_dimension_mode(self, mode: str):
        self._dimension_mode = DimensionMode.normalize(mode)
        self.update()

    def set_summary(self, summary: dict):
        self._summary = summary or {}
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            painter.fillRect(self.rect(), QtGui.QColor(255, 255, 255))
            self._paint(painter, self.rect().adjusted(12, 12, -12, -12))
        finally:
            painter.end()

    def _paint(self, painter: QtGui.QPainter, rect: QtCore.QRect):
        painter.setPen(QtGui.QPen(QtGui.QColor(120, 120, 120), 1))
        painter.drawText(rect, QtCore.Qt.AlignCenter, 'Preview')

    def _draw_summary(self, painter: QtGui.QPainter, rect: QtCore.QRect, lines: list):
        painter.setPen(QtGui.QColor(60, 60, 60))
        font = painter.font()
        font.setPointSize(max(8, font.pointSize()))
        painter.setFont(font)
        y = rect.bottom() - 54
        for line in lines:
            painter.drawText(rect.left(), y, rect.width(), 18, QtCore.Qt.AlignLeft, line)
            y += 18

