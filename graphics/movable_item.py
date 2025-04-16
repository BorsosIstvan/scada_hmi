from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem


class MovableItem(QGraphicsRectItem):
    def __init__(self, x=0, y=0, w=100, h=50):
        super().__init__(x, y, w, h)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setBrush(QBrush(QColor("lightgray")))

    def to_dict(self):
        rect = self.rect()
        return {
            "x": rect.x(),
            "y": rect.y(),
            "w": rect.width(),
            "h": rect.height(),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["x"], data["y"], data["w"], data["h"])