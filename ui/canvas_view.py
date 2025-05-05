from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QRectF


class CanvasView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.raster = True
        self.raster_grootte = 20
        self.achtergrond_kleur = "#FFFFFF"

        #  self.setDragMode(QGraphicsView.ScrollHandDrag)

    def setCanvasSettings(self, settings):
        grootte = settings.get("grootte", [800, 600])
        width, height = grootte[0], grootte[1]
        self.scene.setSceneRect(0, 0, width, height)
        self.setFixedSize(width + 2, height + 2)
        self.achtergrond_kleur = settings.get("achtergrond_kleur", "#FFFFFF")
        self.raster = settings.get("raster", True)
        self.raster_grootte = settings.get("raster_grootte", 20)

        self.setStyleSheet(f"background-color: {self.achtergrond_kleur};")
        self.viewport().update()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)

        if self.raster:
            kleur = QColor("#cccccc")
            pen = painter.pen()
            pen.setColor(kleur)
            painter.setPen(pen)

            links = int(rect.left()) - (int(rect.left()) % self.raster_grootte)
            boven = int(rect.top()) - (int(rect.top()) % self.raster_grootte)

            for x in range(links, int(rect.right()), self.raster_grootte):
                painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            for y in range(boven, int(rect.bottom()), self.raster_grootte):
                painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def clear(self):
        self.scene.clear()
