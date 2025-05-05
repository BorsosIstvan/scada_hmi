from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsItem, QDialog, \
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QDialogButtonBox, QComboBox
from PySide6.QtGui import QPixmap, QFont, QColor, Qt
from PySide6.QtCore import QPointF, QRectF

from core import project_context


class ScadaObject(QGraphicsItemGroup):
    def __init__(self, x=0, y=0, tekst="", kleur="black", lettertype="Arial", grootte=12,
                 pad_aan="", pad_uit="", status=False, breedte=100, hoogte=100, adres="",
                 variabele="knop", schaal=1):
        super().__init__()

        self.x = x
        self.y = y
        self.tekst = tekst
        self.kleur = kleur
        self.lettertype = lettertype
        self.grootte = grootte
        self.pad_aan = pad_aan
        self.pad_uit = pad_uit
        self.status = status
        self.breedte = breedte
        self.hoogte = hoogte
        self.adres = adres
        self.schaal = schaal
        self.variabele = variabele

        # Afbeelding
        self.pixmap_item = QGraphicsPixmapItem()
        self.update_pixmap()
        self.addToGroup(self.pixmap_item)

        # Tekst
        if self.tekst:
            self.text_item = QGraphicsTextItem(self.tekst)
            self.text_item.setFont(QFont(self.lettertype, self.grootte))
            self.text_item.setDefaultTextColor(QColor(self.kleur))
            self.text_item.setPos(0, self.hoogte)  # onder het plaatje
            self.addToGroup(self.text_item)

        self.setPos(QPointF(self.x, self.y))

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable #|
            #QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

    def update_pixmap(self):
        path = self.pad_aan if self.status else self.pad_uit
        if path:
            pixmap = QPixmap(path).scaled(self.breedte, self.hoogte)
            self.pixmap_item.setPixmap(pixmap)

    def set_status(self, status: bool):
        self.status = status
        self.update_pixmap()

    def to_dict(self):
        return {
            "type": "scadaobject",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "tekst": self.tekst,
            "kleur": self.kleur,
            "lettertype": self.lettertype,
            "grootte": self.grootte,
            "pad_aan": self.pad_aan,
            "pad_uit": self.pad_uit,
            "status": self.status,
            "breedte": self.breedte,
            "hoogte": self.hoogte,
            "adres": self.adres,
            "schaal": self.scale(),
            "variabele": self.variabele.naam
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def wheelEvent(self, event):
        factor = 1.1 if event.delta() > 0 else 0.9
        self.setScale(self.scale() * factor)
        event.accept()

    def mouseDoubleClickEvent(self, event):
        dialoog = InstellingenDialoog(self, project_context.variabelen_lijst)
        if dialoog.exec():
            dialoog.apply_changes()

    def mousePressEvent(self, event):
        print("Knop state is:", self.status)
        self.set_status(not self.status)


#  Instellingen dialoog klass voor scada objecten.

class InstellingenDialoog(QDialog):
    def __init__(self, obj, variabelenlijst, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Objectinstellingen")
        self.obj = obj
        self.variabelenlijst = variabelenlijst

        layout = QFormLayout(self)

        # Tekstveld
        tekst = obj.text_item.toPlainText() if hasattr(obj, "text_item") else ""
        self.tekst_input = QLineEdit(tekst)

        # Adresveld
        self.adres_input = QLineEdit(obj.adres)

        # Pad voor afbeelding aan
        self.pad_aan_input = QLineEdit(obj.pad_aan)

        # Pad voor afbeelding uit
        self.pad_uit_input = QLineEdit(obj.pad_uit)

        # Variabele combobox
        self.variabele_combo = QComboBox()
        self.variabele_combo.addItem("⟨geen⟩", userData=None)  # Lege keuze

        for var in self.variabelenlijst:
            self.variabele_combo.addItem(var.naam, userData=var)

        # Stel huidige variabele in als die er is
        if hasattr(obj, "variabele") and obj.variabele:
            if isinstance(obj.variabele, str):
                # Als alleen de naam opgeslagen is
                index = self.variabele_combo.findText(obj.variabele)
            elif hasattr(obj.variabele, "naam"):
                # Als een Variabele-object is opgeslagen
                index = self.variabele_combo.findText(obj.variabele.naam)
            else:
                index = -1

            if index != -1:
                self.variabele_combo.setCurrentIndex(index)

        # Toevoegen aan formulier
        layout.addRow("Tekst", self.tekst_input)
        layout.addRow("Adres", self.adres_input)
        layout.addRow("Pad aan", self.pad_aan_input)
        layout.addRow("Pad uit", self.pad_uit_input)
        layout.addRow("Variabele", self.variabele_combo)

        # OK/Cancel knoppen
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def apply_changes(self):
        tekst = self.tekst_input.text()
        self.obj.adres = self.adres_input.text()
        self.obj.pad_aan = self.pad_aan_input.text()
        self.obj.pad_uit = self.pad_uit_input.text()
        self.obj.tekst = tekst
        self.obj.variabele = self.variabele_combo.currentData()

        if not hasattr(self.obj, "text_item"):
            self.obj.text_item = QGraphicsTextItem()
            self.obj.addToGroup(self.obj.text_item)

        self.obj.text_item.setPlainText(tekst)
        self.obj.text_item.setPos(0, self.obj.hoogte)
        self.obj.update_pixmap()
