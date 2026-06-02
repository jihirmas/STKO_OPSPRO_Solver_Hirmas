from PySide2 import QtCore, QtGui

from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.preview.foundation_preview_widget import FoundationPreviewWidget


class EmbeddedFoundationPreview(FoundationPreviewWidget):
    def _paint(self, painter: QtGui.QPainter, rect: QtCore.QRect):
        if self._dimension_mode == DimensionMode.THREE_D:
            self._paint_3d(painter, rect)
        else:
            self._paint_2d(painter, rect)

    def _paint_2d(self, painter, rect):
        soil = QtCore.QRect(rect.left() + 20, rect.top() + 88, rect.width() - 40, 100)
        painter.setPen(QtGui.QPen(QtGui.QColor(120, 100, 65), 1))
        painter.setBrush(QtGui.QColor(232, 223, 204))
        painter.drawRect(soil)
        for x in range(soil.left() + 8, soil.right(), 16):
            painter.drawLine(x, soil.top(), x - 28, soil.bottom())

        footing = QtCore.QRect(rect.center().x() - 44, soil.top() - 36, 88, 108)
        painter.setPen(QtGui.QPen(QtGui.QColor(45, 45, 45), 2))
        painter.setBrush(QtGui.QColor(220, 224, 228))
        painter.drawRect(footing)
        painter.drawText(footing.adjusted(0, 8, 0, 0), QtCore.Qt.AlignHCenter, 'foundation')

        painter.setPen(QtGui.QPen(QtGui.QColor(40, 130, 75), 2, QtCore.Qt.DashLine))
        painter.drawRect(footing.adjusted(-5, -5, 5, 5))

        self._draw_summary(
            painter,
            rect,
            [
                'Geometry detected from viewport',
                'Mode: 2D',
                'Mechanical expansion pending',
            ],
        )

    def _paint_3d(self, painter, rect):
        cx = rect.center().x()
        top = rect.top() + 54
        soil = [
            QtCore.QPoint(cx - 90, top + 54),
            QtCore.QPoint(cx - 20, top + 18),
            QtCore.QPoint(cx + 96, top + 56),
            QtCore.QPoint(cx + 24, top + 96),
        ]
        painter.setPen(QtGui.QPen(QtGui.QColor(120, 100, 65), 1))
        painter.setBrush(QtGui.QColor(232, 223, 204))
        painter.drawPolygon(QtGui.QPolygon(soil))
        painter.drawLine(soil[0], QtCore.QPoint(cx - 90, top + 132))
        painter.drawLine(soil[2], QtCore.QPoint(cx + 96, top + 132))
        painter.drawLine(QtCore.QPoint(cx - 90, top + 132), QtCore.QPoint(cx + 24, top + 174))
        painter.drawLine(QtCore.QPoint(cx + 96, top + 132), QtCore.QPoint(cx + 24, top + 174))

        painter.setPen(QtGui.QPen(QtGui.QColor(45, 45, 45), 2))
        painter.setBrush(QtGui.QColor(220, 224, 228))
        block = [
            QtCore.QPoint(cx - 24, top + 38),
            QtCore.QPoint(cx + 20, top + 24),
            QtCore.QPoint(cx + 56, top + 40),
            QtCore.QPoint(cx + 12, top + 58),
        ]
        painter.drawPolygon(QtGui.QPolygon(block))
        painter.drawLine(block[0], QtCore.QPoint(cx - 24, top + 104))
        painter.drawLine(block[1], QtCore.QPoint(cx + 20, top + 88))
        painter.drawLine(block[2], QtCore.QPoint(cx + 56, top + 106))
        painter.drawLine(block[3], QtCore.QPoint(cx + 12, top + 124))
        painter.drawLine(QtCore.QPoint(cx - 24, top + 104), QtCore.QPoint(cx + 12, top + 124))
        painter.drawLine(QtCore.QPoint(cx + 56, top + 106), QtCore.QPoint(cx + 12, top + 124))

        painter.setPen(QtGui.QPen(QtGui.QColor(40, 130, 75), 2, QtCore.Qt.DashLine))
        painter.drawPolyline(QtGui.QPolygon(block + [block[0]]))

        self._draw_summary(
            painter,
            rect,
            [
                'Geometry detected from viewport',
                'Mode: 3D',
                'Interface faces pending',
            ],
        )
