from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem

from PySide6.QtCore import Qt

from graphics.movable_item import MovableItem

from PySide6.QtGui import QFont

from PySide6.QtGui import QFont, QColor


class SCADAObject(MovableItem):
    def __init__(self, x, y, w, h, label="", naam="", plc_tag=None, label_style=None):
        super().__init__(x, y, w, h)
        self.label = label
        self.naam = naam
        self.plc_tag = plc_tag or {"plc": "", "type": "Coil (1bit)", "address": 0}
        self.label_style = label_style or {
            "font": "Arial",
            "size": 10,
            "color": "#000000"  # zwart in hex
        }

        self.label_item = QGraphicsTextItem(self.label, self)
        font = QFont(self.label_style["font"], self.label_style["size"])
        self.label_item.setFont(font)
        self.label_item.setDefaultTextColor(QColor(self.label_style["color"]))

        self._update_label_position()

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def to_dict(self):
        return {
            "type": "SCADAObject",
            "x": self.x(),
            "y": self.y(),
            "w": self.rect().width(),
            "h": self.rect().height(),
            "label": self.label,
            "naam": self.naam,
            "plc_tag": self.plc_tag,
            "label_style": self.label_style
        }

    @classmethod
    def from_dict(cls, data):
        x = data.get("x", 0)
        y = data.get("y", 0)
        w = data.get("w", 100)
        h = data.get("h", 50)
        label = data.get("label", "")
        naam = data.get("naam", "")
        plc_tag = data.get("plc_tag", {})
        label_style = data.get("label_style", {
            "font": "Arial",
            "size": 10,
            "color": "#000000"
        })

        return cls(x, y, w, h, label=label, naam=naam,
                   plc_tag=plc_tag, label_style=label_style)

    def _update_label_position(self):
        rect = self.rect()
        text_rect = self.label_item.boundingRect()
        x = (rect.width() - text_rect.width()) / 2
        y = (rect.height() - text_rect.height()) / 2
        self.label_item.setPos(rect.x() + x, rect.y() + y)

    def set_label(self, text):
        self.label = text
        self.label_item.setPlainText(text)
        self._update_label_position()
