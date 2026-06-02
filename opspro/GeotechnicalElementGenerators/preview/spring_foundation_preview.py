from PySide2 import QtCore, QtGui

from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.preview.foundation_preview_widget import FoundationPreviewWidget


class SpringFoundationPreview(FoundationPreviewWidget):
    def _paint(self, painter: QtGui.QPainter, rect: QtCore.QRect):
        mode = self._dimension_mode
        center_x = rect.center().x()
        top = rect.top() + 18

        painter.setPen(QtGui.QPen(QtGui.QColor(45, 45, 45), 2))
        painter.setBrush(QtGui.QColor(235, 238, 241))
        footing = QtCore.QRect(center_x - 72, top + 70, 144, 42)
        painter.drawRect(footing)
        painter.drawText(footing, QtCore.Qt.AlignCenter, 'footing')

        painter.setBrush(QtGui.QColor(55, 120, 180))
        painter.drawEllipse(QtCore.QPoint(center_x, top + 20), 7, 7)
        painter.drawLine(center_x, top + 27, center_x, footing.top())

        spring_pen = QtGui.QPen(QtGui.QColor(40, 130, 75), 2)
        painter.setPen(spring_pen)
        if mode == DimensionMode.TWO_D:
            self._draw_spring(painter, center_x - 48, footing.bottom() + 8, center_x - 48, footing.bottom() + 52)
            self._draw_spring(painter, center_x, footing.bottom() + 8, center_x, footing.bottom() + 52)
            self._draw_rotation(painter, center_x + 48, footing.bottom() + 28)
            labels = [('Kx', center_x - 56), ('Ky', center_x - 8), ('Krz', center_x + 38)]
        else:
            offsets = [-60, -36, -12, 18, 44, 70]
            names = ['Kx', 'Ky', 'Kz', 'Krx', 'Kry', 'Krz']
            for offset, name in zip(offsets, names):
                if name.startswith('Kr'):
                    self._draw_rotation(painter, center_x + offset, footing.bottom() + 30)
                else:
                    self._draw_spring(painter, center_x + offset, footing.bottom() + 8, center_x + offset, footing.bottom() + 48)
            labels = [(name, center_x + offset - 10) for offset, name in zip(offsets, names)]

        painter.setPen(QtGui.QColor(40, 40, 40))
        for text, x in labels:
            painter.drawText(x, footing.bottom() + 70, text)

        mats = self._summary.get('uniaxial_materials', 3 if mode == DimensionMode.TWO_D else 6)
        self._draw_summary(
            painter,
            rect,
            [
                'Generated internally',
                '1 auxiliary node',
                f'{mats} Elastic uniaxial materials',
                '1 zeroLength element',
            ],
        )

    def _draw_spring(self, painter, x1, y1, x2, y2):
        segments = 7
        amp = 7
        points = [QtCore.QPoint(x1, y1)]
        height = y2 - y1
        for i in range(1, segments):
            x = x1 + (amp if i % 2 else -amp)
            y = y1 + int(height * i / segments)
            points.append(QtCore.QPoint(x, y))
        points.append(QtCore.QPoint(x2, y2))
        painter.drawPolyline(QtGui.QPolygon(points))

    def _draw_rotation(self, painter, x, y):
        rect = QtCore.QRect(x - 14, y - 14, 28, 28)
        painter.drawArc(rect, 35 * 16, 285 * 16)
        painter.drawLine(x + 12, y - 8, x + 18, y - 8)
        painter.drawLine(x + 12, y - 8, x + 12, y - 14)
