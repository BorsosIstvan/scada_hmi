from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QFontComboBox,
    QSpinBox, QComboBox, QFormLayout, QPushButton, QDialogButtonBox
)
from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog


class ObjectPropertiesDialog(QDialog):
    def __init__(self, parent=None, scada_object=None):
        super().__init__(parent)
        self.setWindowTitle("Eigenschappen")

        self.scada_object = scada_object
        label_style = scada_object.label_style

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Naam en Label
        self.naam_input = QLineEdit()
        self.naam_input.setText(scada_object.naam)
        form_layout.addRow("Naam:", self.naam_input)

        self.label_input = QLineEdit()
        self.label_input.setText(scada_object.label)
        form_layout.addRow("Label tekst:", self.label_input)

        # Font
        self.label_font_input = QFontComboBox()
        self.label_font_input.setCurrentFont(label_style.get("font", "Arial"))
        form_layout.addRow("Lettertype:", self.label_font_input)

        # Grootte
        self.label_font_size_input = QSpinBox()
        self.label_font_size_input.setRange(6, 72)
        self.label_font_size_input.setValue(label_style.get("size", 10))
        form_layout.addRow("Lettergrootte:", self.label_font_size_input)

        # Kleur kiezen
        self.label_color_button = QPushButton("Kies kleur")
        self.label_color = QColor(label_style.get("color", "#000000"))

        def kies_kleur():
            kleur = QColorDialog.getColor(self.label_color, self, "Kies tekstkleur")
            if kleur.isValid():
                self.label_color = kleur
                self.label_color_button.setStyleSheet(f"background-color: {kleur.name()}")

        self.label_color_button.clicked.connect(kies_kleur)
        self.label_color_button.setStyleSheet(f"background-color: {self.label_color.name()}")
        form_layout.addRow("Tekstkleur:", self.label_color_button)

        # PLC-gegevens
        self.plc_input = QLineEdit()
        self.plc_input.setText(scada_object.plc_tag.get("plc", ""))
        form_layout.addRow("PLC naam:", self.plc_input)

        self.plc_type_input = QComboBox()
        self.plc_type_input.addItems([
            "Coil (1bit)", "Holding Register (2 byte)",
            "Discrete Input (1bit)", "Analog Input (2 byte)"
        ])
        self.plc_type_input.setCurrentText(scada_object.plc_tag.get("type", "Coil (1bit)"))
        form_layout.addRow("Registertype:", self.plc_type_input)

        self.plc_address_input = QSpinBox()
        self.plc_address_input.setRange(0, 9999)
        self.plc_address_input.setValue(scada_object.plc_tag.get("address", 0))
        form_layout.addRow("PLC adres:", self.plc_address_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def apply_changes(self):
        self.scada_object.naam = self.naam_input.text()
        self.scada_object.set_label(self.label_input.text())

        # Label stijl updaten
        self.scada_object.label_style["font"] = self.label_font_input.currentFont().family()
        self.scada_object.label_style["size"] = self.label_font_size_input.value()
        self.scada_object.label_style["color"] = self.label_color.name()

        # Font direct toepassen
        font = QFont(self.scada_object.label_style["font"],
                     self.scada_object.label_style["size"])
        self.scada_object.label_item.setFont(font)
        self.scada_object.label_item.setDefaultTextColor(QColor(self.scada_object.label_style["color"]))
        self.scada_object._update_label_position()

        # PLC
        self.scada_object.plc_tag["plc"] = self.plc_input.text()
        self.scada_object.plc_tag["type"] = self.plc_type_input.currentText()
        self.scada_object.plc_tag["address"] = self.plc_address_input.value()

