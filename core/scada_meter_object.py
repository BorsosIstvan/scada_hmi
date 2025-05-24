from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsItem
from PySide6.QtGui import QColor
from PySide6.QtCore import QPointF

from core import project_context
from core.installingen_dialoog import InstellingenDialoog


class ScadaMeterObject(QGraphicsItemGroup):
    def __init__(self, x=0, y=0, breedte=100, hoogte=100,
                 variabele="", min_waarde=0, max_waarde=100, schaal=1.0, naam=""):
        super().__init__()
        self.x = x
        self.y = y
        self.breedte = breedte
        self.hoogte = hoogte
        self.variabele = variabele
        self.min_waarde = min_waarde
        self.max_waarde = max_waarde
        self.schaal = schaal
        self.waarde = 0
        self.naam = naam

        # Achtergrond
        self.rect_item = QGraphicsRectItem(0, 0, breedte, hoogte)
        self.rect_item.setBrush(QColor("lightgray"))
        self.addToGroup(self.rect_item)

        # Waarde-balk
        self.bar_item = QGraphicsRectItem(0, hoogte, breedte, 0)
        self.bar_item.setBrush(QColor("green"))
        self.addToGroup(self.bar_item)

        self.setPos(QPointF(x, y))
        self.setScale(schaal)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )

    def update_from_var(self, waarde):
        self.waarde = waarde
        norm = max(0.0, min(1.0, (waarde - self.min_waarde) / (self.max_waarde - self.min_waarde)))
        bar_hoogte = norm * self.hoogte
        self.bar_item.setRect(0, self.hoogte - bar_hoogte, self.breedte, bar_hoogte)

    def to_dict(self):
        return {
            "type": "scadameter",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "breedte": self.breedte,
            "hoogte": self.hoogte,
            "variabele": self.variabele,
            "min_waarde": self.min_waarde,
            "max_waarde": self.max_waarde,
            "schaal": self.scale(),
            "naam": self.naam
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            x=data.get("x"),
            y=data.get("y"),
            breedte=data.get("breedte"),
            hoogte=data.get("hoogte"),
            variabele=data.get("variabele"),
            min_waarde=data.get("min_waarde"),
            max_waarde=data.get("max_waarde"),
            schaal=data.get("schaal"),
            naam=data.get("naam")
        )
        return obj

    def mouseDoubleClickEvent(self, event):
        dialoog = InstellingenDialoog(self, project_context.variabelen_lijst)
        if dialoog.exec():
            dialoog.apply_changes()

    def update_runtime(self):
        #if self._gebruikersinput:  # Dan geen update
        #    return
        for var in project_context.variabelen_lijst:
            if var.naam == self.variabele:
                self.waarde = float(var.waarde)
                self.update_from_var(self.waarde)


#   Instellingen meter dialoog klasse

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox,
    QLineEdit, QSpinBox, QDoubleSpinBox
)


class InstellingenMeterDialoog(QDialog):
    def __init__(self, meter: "ScadaMeterObject"):
        super().__init__()
        self.setWindowTitle("Meter Instellingen")
        self.meter = meter

        layout = QFormLayout()

        self.var_edit = QLineEdit(meter.variabele)
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(-1e6, 1e6)
        self.min_spin.setValue(meter.min_waarde)

        self.max_spin = QDoubleSpinBox()
        self.max_spin.setRange(-1e6, 1e6)
        self.max_spin.setValue(meter.max_waarde)

        self.breedte_spin = QSpinBox()
        self.breedte_spin.setRange(10, 1000)
        self.breedte_spin.setValue(meter.breedte)

        self.hoogte_spin = QSpinBox()
        self.hoogte_spin.setRange(10, 1000)
        self.hoogte_spin.setValue(meter.hoogte)

        self.schaal_spin = QDoubleSpinBox()
        self.schaal_spin.setRange(0.1, 10.0)
        self.schaal_spin.setSingleStep(0.1)
        self.schaal_spin.setValue(meter.schaal)

        layout.addRow("Variabele", self.var_edit)
        layout.addRow("Min waarde", self.min_spin)
        layout.addRow("Max waarde", self.max_spin)
        layout.addRow("Breedte", self.breedte_spin)
        layout.addRow("Hoogte", self.hoogte_spin)
        layout.addRow("Schaal", self.schaal_spin)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def apply_changes(self):
        self.meter.variabele = self.var_edit.text()
        self.meter.min_waarde = self.min_spin.value()
        self.meter.max_waarde = self.max_spin.value()
        self.meter.breedte = self.breedte_spin.value()
        self.meter.hoogte = self.hoogte_spin.value()
        self.meter.setScale(self.schaal_spin.value())

        # Hertekenen meter
        self.meter.rect_item.setRect(0, 0, self.meter.breedte, self.meter.hoogte)
        self.meter.update_from_var(self.meter.waarde)
