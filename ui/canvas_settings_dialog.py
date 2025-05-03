from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton,
    QCheckBox, QColorDialog
)
from PySide6.QtGui import QColor


class CanvasSettingsDialog(QDialog):
    def __init__(self, huidige_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Canvas instellingen")
        self.setMinimumWidth(300)
        self.settings = huidige_settings.copy()

        layout = QVBoxLayout()

        self.breedte_input = QSpinBox()
        self.breedte_input.setRange(100, 10000)
        self.breedte_input.setValue(huidige_settings["grootte"][0])

        self.hoogte_input = QSpinBox()
        self.hoogte_input.setRange(100, 10000)
        self.hoogte_input.setValue(huidige_settings["grootte"][1])

        grootte_layout = QHBoxLayout()
        grootte_layout.addWidget(QLabel("Breedte:"))
        grootte_layout.addWidget(self.breedte_input)
        grootte_layout.addWidget(QLabel("Hoogte:"))
        grootte_layout.addWidget(self.hoogte_input)
        layout.addLayout(grootte_layout)

        self.raster_checkbox = QCheckBox("Raster tonen")
        self.raster_checkbox.setChecked(huidige_settings["raster"])
        layout.addWidget(self.raster_checkbox)

        self.rastergrootte_input = QSpinBox()
        self.rastergrootte_input.setRange(2, 200)
        self.rastergrootte_input.setValue(huidige_settings["raster_grootte"])
        layout.addWidget(QLabel("Rastergrootte:"))
        layout.addWidget(self.rastergrootte_input)

        self.kleur_button = QPushButton("Achtergrondkleur kiezen")
        self.kleur_button.clicked.connect(self.kies_kleur)
        self.kleur = QColor(huidige_settings["achtergrond_kleur"])
        layout.addWidget(self.kleur_button)

        knop_layout = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Annuleren")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        knop_layout.addWidget(ok)
        knop_layout.addWidget(cancel)
        layout.addLayout(knop_layout)

        self.setLayout(layout)

    def kies_kleur(self):
        kleur = QColorDialog.getColor(self.kleur, self)
        if kleur.isValid():
            self.kleur = kleur

    def opgehaalde_settings(self):
        return {
            "grootte": [self.breedte_input.value(), self.hoogte_input.value()],
            "achtergrond_kleur": self.kleur.name(),
            "raster": self.raster_checkbox.isChecked(),
            "raster_grootte": self.rastergrootte_input.value()
        }
