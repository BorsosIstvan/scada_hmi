from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import QRectF

class MovableItem(QGraphicsRectItem):
    def __init__(self, x=0, y=0, width=100, height=50):
        rect = QRectF(0, 0, width, height)
        super().__init__(rect)
        self.setPos(x, y)

        # Gebruik vlaggen van QGraphicsItem
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )

        self.properties = {
            "label": "",
            "vorm": "rechthoek"
        }

        self.label_item = QGraphicsTextItem("", self)
        self.label_item.setPos(0, -20)

    def update_label(self):
        self.label_item.setPlainText(self.properties["label"])
