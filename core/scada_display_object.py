from PySide6.QtWidgets import QGraphicsTextItem
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import QPointF

from core import project_context
from core.installingen_dialoog import InstellingenDialoog


class DisplayObject(QGraphicsTextItem):
    def __init__(self, x=0, y=0, variabele="", kleur="black", lettertype="Arial", grootte=12, naam=""):
        super().__init__()
        self.x = x
        self.y = y
        self.variabele = variabele
        self.kleur = kleur
        self.lettertype = lettertype
        self.grootte = grootte
        self.naam = naam

        self.setFont(QFont(self.lettertype, self.grootte))
        self.setDefaultTextColor(QColor(self.kleur))
        self.setPos(QPointF(self.x, self.y))

        self.setFlags(
            QGraphicsTextItem.ItemIsMovable |
            QGraphicsTextItem.ItemIsSelectable
        )
        self.setAcceptHoverEvents(True)

        self.update_display()

    def update_display(self):
        var = next((v for v in project_context.variabelen_lijst if v.naam == self.variabele), None)
        if var:
            self.setPlainText(str(var.waarde))
        else:
            self.setPlainText("??")

    def to_dict(self):
        return {
            "type": "displayobject",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "variabele": self.variabele,
            "kleur": self.kleur,
            "lettertype": self.lettertype,
            "grootte": self.font().pointSize(),
            "naam": self.naam
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            x=data.get("x", 100),
            y=data.get("y", 100),
            variabele=data.get("variabele", ""),
            kleur=data.get("kleur", "black"),
            lettertype=data.get("lettertype", "Arial"),
            grootte=data.get("grootte", 12),
            naam=data.get("naam", "")
        )
        return obj

    def mouseDoubleClickEvent(self, event):
        dialoog = InstellingenDialoog(self, project_context.variabelen_lijst)
        if dialoog.exec():
            dialoog.apply_changes()
            self.update_display()

    def wheelEvent(self, event):
        delta = event.delta()
        huidige_font = self.font()
        grootte = huidige_font.pointSize()

        if delta > 0:
            grootte += 1
        elif delta < 0 and grootte > 1:
            grootte -= 1

        nieuwe_font = QFont(huidige_font)
        nieuwe_font.setPointSize(grootte)
        self.setFont(nieuwe_font)

    def update_runtime(self):
        #if self._gebruikersinput:  # Dan geen update
        #    return
        for var in project_context.variabelen_lijst:
            if var.naam == self.variabele:
                self.update_display()
