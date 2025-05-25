from PySide6.QtCore import QPointF
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsItem

from core import project_context


class ScadaImageObject(QGraphicsItemGroup):
    def __init__(self, x=0, y=0, pad_aan="", pad_uit="", status=False,
                 breedte=100, hoogte=100, schaal=1.0, variabele="", naam=""):
        super().__init__()

        self.x = x
        self.y = y
        self.pad_aan = pad_aan
        self.pad_uit = pad_uit
        self.status = status
        self.breedte = breedte
        self.hoogte = hoogte
        self.variabele = variabele  # Dit kan later een object zijn
        self.naam = naam

        # Afbeelding
        self.pixmap_item = QGraphicsPixmapItem()
        self.update_pixmap()
        self.addToGroup(self.pixmap_item)

        # Positie en schaal
        self.setPos(QPointF(self.x, self.y))
        self.setScale(schaal)

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )
        self.setAcceptHoverEvents(True)

    def update_pixmap(self):
        pad = self.pad_aan if self.status else self.pad_uit
        if pad:
            pixmap = QPixmap(pad).scaled(self.breedte, self.hoogte, Qt.KeepAspectRatio)
            self.pixmap_item.setPixmap(pixmap)

    def set_status(self, status: bool):
        self.status = status
        self.update_pixmap()

    def to_dict(self):
        return {
            "type": "scadaimageobject",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "pad_aan": self.pad_aan,
            "pad_uit": self.pad_uit,
            "status": self.status,
            "breedte": self.breedte,
            "hoogte": self.hoogte,
            "schaal": self.scale(),
            "variabele": self.variabele if isinstance(self.variabele, str) else getattr(self.variabele, "naam", ""),
            "naam": self.naam
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            x=data.get("x", 0),
            y=data.get("y", 0),
            pad_aan=data.get("pad_aan", ""),
            pad_uit=data.get("pad_uit", ""),
            status=data.get("status", False),
            breedte=data.get("breedte", 100),
            hoogte=data.get("hoogte", 100),
            schaal=data.get("schaal", 1.0),
            variabele=data.get("variabele", ""),
            naam=data.get("naam")
        )
        return obj

    def wheelEvent(self, event):
        factor = 1.1 if event.delta() > 0 else 0.9
        self.setScale(self.scale() * factor)
        event.accept()

    def mouseDoubleClickEvent(self, event):
        dialoog = InstellingenDialoog(self, project_context.variabelen_lijst)
        if dialoog.exec():
            dialoog.apply_changes()

    def mousePressEvent(self, event):
        # Wissel status bij klikken
        self.set_status(not self.status)


    def update_runtime(self):
        for var in project_context.variabelen_lijst:
            if var.naam == self.variabele:
                self.status = bool(int(var.waarde))
                self.set_status(self.status)


#   Instellingen dialoog klasse:

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox
)


class InstellingenDialoog(QDialog):
    def __init__(self, scada_object, variabelen_lijst):
        super().__init__()
        self.setWindowTitle("Instellingen")

        self.scada_object = scada_object
        self.variabelen_lijst = variabelen_lijst

        layout = QVBoxLayout()

        # Naam
        self.naam_input = QLineEdit(getattr(scada_object, "naam", ""))
        layout.addLayout(self._label_input("Naam:", self.naam_input))

        # Pad AAN
        self.pad_aan_input = QLineEdit(scada_object.pad_aan)
        pad_aan_btn = QPushButton("Kies...")
        pad_aan_btn.clicked.connect(lambda: self.kies_pad(self.pad_aan_input))
        layout.addLayout(self._label_input("Beeld (AAN):", self.pad_aan_input, pad_aan_btn))

        # Pad UIT
        self.pad_uit_input = QLineEdit(scada_object.pad_uit)
        pad_uit_btn = QPushButton("Kies...")
        pad_uit_btn.clicked.connect(lambda: self.kies_pad(self.pad_uit_input))
        layout.addLayout(self._label_input("Beeld (UIT):", self.pad_uit_input, pad_uit_btn))

        # Variabele
        self.variabele_input = QComboBox()
        for var in variabelen_lijst:
            naam = var.naam if hasattr(var, "naam") else str(var)
            self.variabele_input.addItem(naam)
        huidige = scada_object.variabele
        if huidige:
            index = self.variabele_input.findText(huidige)
            if index >= 0:
                self.variabele_input.setCurrentIndex(index)
        layout.addLayout(self._label_input("Gekoppelde variabele:", self.variabele_input))

        # OK / Annuleren
        btns = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Annuleren")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        self.setLayout(layout)

    def _label_input(self, label, widget, extra_widget=None):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addWidget(widget)
        if extra_widget:
            row.addWidget(extra_widget)
        return row

    def kies_pad(self, line_edit):
        bestand, _ = QFileDialog.getOpenFileName(self, "Kies afbeelding", "", "Afbeeldingen (*.png *.jpg *.bmp *.gif)")
        if bestand:
            line_edit.setText(bestand)

    def apply_changes(self):
        # Naam instellen (indien aanwezig)
        if hasattr(self.scada_object, "naam"):
            self.scada_object.naam = self.naam_input.text()

        self.scada_object.pad_aan = self.pad_aan_input.text()
        self.scada_object.pad_uit = self.pad_uit_input.text()
        self.scada_object.variabele = self.variabele_input.currentText()
        self.scada_object.update_pixmap()
