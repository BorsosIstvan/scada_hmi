from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QCheckBox
)


class InstellingenDialoog(QDialog):
    def __init__(self, scada_object, variabelen_lijst, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instellingen")

        self.object = scada_object
        self.variabelen_lijst = variabelen_lijst

        layout = QVBoxLayout()

        # Naam
        self.naam_edit = QLineEdit(getattr(self.object, "naam", ""))
        layout.addLayout(self._maak_lijn("Naam / ID", self.naam_edit))

        # Variabele kiezen
        self.variabele_combo = QComboBox()
        self.variabele_combo.addItem("")
        for var in self.variabelen_lijst:
            if hasattr(var, "naam"):
                self.variabele_combo.addItem(var.naam)
        if hasattr(self.object, "variabele") and self.object.variabele:
            index = self.variabele_combo.findText(self.object.variabele)
            if index != -1:
                self.variabele_combo.setCurrentIndex(index)
        layout.addLayout(self._maak_lijn("Variabele", self.variabele_combo))

        # Voor slider/min/max/orientatie
        if hasattr(self.object, "minimum") and hasattr(self.object, "maximum"):
            self.minimum_edit = QLineEdit(str(self.object.minimum))
            self.maximum_edit = QLineEdit(str(self.object.maximum))
            layout.addLayout(self._maak_lijn("Minimum", self.minimum_edit))
            layout.addLayout(self._maak_lijn("Maximum", self.maximum_edit))

        if hasattr(self.object, "horizontaal"):
            self.horizontaal_checkbox = QCheckBox("Horizontaal")
            self.horizontaal_checkbox.setChecked(self.object.horizontaal)
            layout.addWidget(self.horizontaal_checkbox)

        # Afbeeldingen
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
        knoppen = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Annuleren")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        knoppen.addWidget(ok_btn)
        knoppen.addWidget(cancel_btn)
        layout.addLayout(knoppen)

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
        if hasattr(self.object, "naam"):
            self.object.naam = self.naam_edit.text()

        self.object.variabele = self.variabele_combo.currentText()

        if hasattr(self.object, "minimum") and hasattr(self.object, "maximum"):
            try:
                self.object.minimum = float(self.minimum_edit.text())
                self.object.maximum = float(self.maximum_edit.text())
            except ValueError:
                pass  # eventueel melding geven

        if hasattr(self.object, "horizontaal"):
            self.object.horizontaal = self.horizontaal_checkbox.isChecked()

        if hasattr(self.object, "pad_aan"):
            self.object.pad_aan = self.pad_aan_edit.text()
        if hasattr(self.object, "pad_uit"):
            self.object.pad_uit = self.pad_uit_edit.text()
        if hasattr(self.object, "update_pixmap"):
            self.object.update_pixmap()
