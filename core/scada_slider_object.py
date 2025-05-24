from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsItem
from PySide6.QtGui import QColor
from PySide6.QtCore import QPointF

from core import project_context
from core.installingen_dialoog import InstellingenDialoog


class ScadaSliderObject(QGraphicsItemGroup):
    def __init__(self, x=0, y=0, breedte=40, hoogte=150,
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
        self.waarde = min_waarde
        self.naam = naam

        # Achtergrond
        self.achtergrond = QGraphicsRectItem(0, 0, breedte, hoogte)
        self.achtergrond.setBrush(QColor("lightgray"))
        self.addToGroup(self.achtergrond)

        # Greep (slider knop)
        self.slider_knop = QGraphicsRectItem(0, 0, breedte, 10)
        self.slider_knop.setBrush(QColor("blue"))
        self.addToGroup(self.slider_knop)

        self.setPos(QPointF(x, y))
        self.setScale(schaal)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )

    def set_waarde(self, waarde):
        # Intern bijwerken
        self.waarde = max(self.min_waarde, min(self.max_waarde, waarde))
        verhouding = (self.waarde - self.min_waarde) / (self.max_waarde - self.min_waarde)
        y_pos = self.hoogte - verhouding * self.hoogte
        self.slider_knop.setRect(0, y_pos, self.breedte, 10)

    def mousePressEvent(self, event):
        if project_context.running:
            self.update_slider(event.pos().y())
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if project_context.running:
            self.update_slider(event.pos().y())
        else:
            super().mouseMoveEvent(event)

    def update_slider(self, y):
        verhouding = 1.0 - max(0.0, min(1.0, y / self.hoogte))
        self.waarde = self.min_waarde + verhouding * (self.max_waarde - self.min_waarde)
        self.set_waarde(self.waarde)

    def mouseDoubleClickEvent(self, event):
        dialoog = InstellingenDialoog(self, project_context.variabelen_lijst)
        if dialoog.exec():
            dialoog.apply_changes()

    def to_dict(self):
        return {
            "type": "scadaslider",
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
            x=data.get("x", 0),
            y=data.get("y", 0),
            breedte=data.get("breedte", 100),
            hoogte=data.get("hoogte", 100),
            variabele=data.get("variabele", ""),
            min_waarde=data.get("min_waarde", 0),
            max_waarde=data.get("max_waarde", 100),
            schaal=data.get("schaal", 1.0),
            naam=data.get("naam", "")
        )
        return obj

    def update_runtime(self):
        for var in project_context.variabelen_lijst:
            if var.naam == self.variabele:
                self.waarde = float(var.waarde)
                self.set_waarde(self.waarde)


#   Instellingen silder object klasse

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox,
    QLineEdit, QSpinBox, QDoubleSpinBox
)


class InstellingenSliderDialoog(QDialog):
    def __init__(self, slider: "ScadaSliderObject"):
        super().__init__()
        self.setWindowTitle("Slider Instellingen")
        self.slider = slider

        layout = QFormLayout()

        self.var_edit = QLineEdit(slider.variabele)
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(-1e6, 1e6)
        self.min_spin.setValue(slider.min_waarde)

        self.max_spin = QDoubleSpinBox()
        self.max_spin.setRange(-1e6, 1e6)
        self.max_spin.setValue(slider.max_waarde)

        self.breedte_spin = QSpinBox()
        self.breedte_spin.setRange(10, 500)
        self.breedte_spin.setValue(slider.breedte)

        self.hoogte_spin = QSpinBox()
        self.hoogte_spin.setRange(10, 1000)
        self.hoogte_spin.setValue(slider.hoogte)

        self.schaal_spin = QDoubleSpinBox()
        self.schaal_spin.setRange(0.1, 10.0)
        self.schaal_spin.setValue(slider.schaal)

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
        self.slider.variabele = self.var_edit.text()
        self.slider.min_waarde = self.min_spin.value()
        self.slider.max_waarde = self.max_spin.value()
        self.slider.breedte = self.breedte_spin.value()
        self.slider.hoogte = self.hoogte_spin.value()
        self.slider.setScale(self.schaal_spin.value())

        self.slider.achtergrond.setRect(0, 0, self.slider.breedte, self.slider.hoogte)
        self.slider.set_waarde(self.slider.waarde)


#   Instelling dialoog klasse met variabele combo box:

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog
)


class InstellingenDialoogSl(QDialog):
    def __init__(self, scada_object, variabelen_lijst, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instellingen")

        self.object = scada_object
        self.variabelen_lijst = variabelen_lijst

        layout = QVBoxLayout()

        # Objectnaam of ID (optioneel)
        self.naam_edit = QLineEdit(getattr(self.object, "naam", ""))
        layout.addLayout(self._maak_lijn("Naam / ID", self.naam_edit))

        # Variabele kiezen
        self.variabele_combo = QComboBox()
        self.variabele_combo.addItem("")  # lege optie
        for var in self.variabelen_lijst:
            if hasattr(var, "naam"):
                self.variabele_combo.addItem(var.naam)
        if hasattr(self.object, "variabele") and self.object.variabele:
            index = self.variabele_combo.findText(self.object.variabele)
            if index != -1:
                self.variabele_combo.setCurrentIndex(index)
        layout.addLayout(self._maak_lijn("Variabele", self.variabele_combo))

        # Voor afbeelding-objecten (zoals lamp, schakelaar)
        if hasattr(self.object, "pad_aan"):
            self.pad_aan_edit = QLineEdit(self.object.pad_aan)
            self.pad_aan_button = QPushButton("...")
            self.pad_aan_button.clicked.connect(self.kies_pad_aan)
            layout.addLayout(self._maak_lijn("Pad Aan", self.pad_aan_edit, self.pad_aan_button))

        if hasattr(self.object, "pad_uit"):
            self.pad_uit_edit = QLineEdit(self.object.pad_uit)
            self.pad_uit_button = QPushButton("...")
            self.pad_uit_button.clicked.connect(self.kies_pad_uit)
            layout.addLayout(self._maak_lijn("Pad Uit", self.pad_uit_edit, self.pad_uit_button))

        # Knoppen
        knoppen_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Annuleren")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        knoppen_layout.addWidget(ok_btn)
        knoppen_layout.addWidget(cancel_btn)
        layout.addLayout(knoppen_layout)

        self.setLayout(layout)

    def _maak_lijn(self, label_tekst, widget, extra_widget=None):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_tekst))
        layout.addWidget(widget)
        if extra_widget:
            layout.addWidget(extra_widget)
        return layout

    def kies_pad_aan(self):
        bestand, _ = QFileDialog.getOpenFileName(self, "Kies afbeelding voor AAN", "",
                                                 "Afbeeldingen (*.png *.jpg *.bmp)")
        if bestand:
            self.pad_aan_edit.setText(bestand)

    def kies_pad_uit(self):
        bestand, _ = QFileDialog.getOpenFileName(self, "Kies afbeelding voor UIT", "",
                                                 "Afbeeldingen (*.png *.jpg *.bmp)")
        if bestand:
            self.pad_uit_edit.setText(bestand)

    def apply_changes(self):
        # Naam optioneel
        if hasattr(self.object, "naam"):
            self.object.naam = self.naam_edit.text()

        # Variabele
        self.object.variabele = self.variabele_combo.currentText()

        # Afbeeldingspaden
        if hasattr(self.object, "pad_aan"):
            self.object.pad_aan = self.pad_aan_edit.text()
        if hasattr(self.object, "pad_uit"):
            self.object.pad_uit = self.pad_uit_edit.text()
        if hasattr(self.object, "update_pixmap"):
            self.object.update_pixmap()
