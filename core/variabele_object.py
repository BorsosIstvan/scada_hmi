from functools import partial


class Variabele:
    def __init__(self, naam, type, adres, waarde, beschrijving=""):
        self.naam = naam  # Unieke naam van de variabele
        self.type = type  # "bit", "int", "float", "string", ...
        self.adres = adres  # Bijv. "HR0", "%QX0.0", enz.
        self.waarde = waarde
        self.beschrijving = beschrijving  # Optioneel

    def to_dict(self):
        return {
            "naam": self.naam,
            "type": self.type,
            "adres": self.adres,
            "waarde": self.waarde,
            "beschrijving": self.beschrijving
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            naam=data["naam"],
            type=data["type"],
            adres=data["adres"],
            waarde=data["waarde"],
            beschrijving=data.get("beschrijving", "")
        )


#  Dialoog variabelen

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QComboBox, QDialogButtonBox, QMessageBox, QWidget
)


class VariabelenDialoog(QDialog):
    def __init__(self, variabelen_lijst, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Beheer variabelen")
        self.resize(600, 400)
        self.variabelen_lijst = variabelen_lijst

        self.layout = QVBoxLayout(self)

        self.tabel = QTableWidget(0, 5)
        self.tabel.setHorizontalHeaderLabels(["Naam", "Type", "Adres", "Beschrijving", "Verwijder"])
        self.layout.addWidget(self.tabel)

        knoppen_layout = QHBoxLayout()
        self.voeg_toe_knop = QPushButton("Voeg toe")
        self.bewerk_knop = QPushButton("Bewerk geselecteerd")
        knoppen_layout.addWidget(self.voeg_toe_knop)
        knoppen_layout.addWidget(self.bewerk_knop)
        self.layout.addLayout(knoppen_layout)

        self.voeg_toe_knop.clicked.connect(self.voeg_toe)
        self.bewerk_knop.clicked.connect(self.bewerk_geselecteerd)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.rejected.connect(self.accept)
        self.layout.addWidget(self.buttons)

        self.tabel.itemChanged.connect(self.verwerk_bewerking)

        self.laad_tabel()

    def laad_tabel(self):
        self.tabel.setRowCount(0)
        for var in self.variabelen_lijst:
            self.voeg_tabelrij_toe(var)

    def voeg_tabelrij_toe(self, var):
        row = self.tabel.rowCount()
        self.tabel.insertRow(row)
        self.tabel.setItem(row, 0, QTableWidgetItem(var.naam))
        # self.tabel.setItem(row, 1, QTableWidgetItem(var.var_type))
        combo = QComboBox()
        combo.addItems(["bit", "int", "float", "string"])
        combo.setCurrentText(var.var_type)
        combo.currentTextChanged.connect(lambda text, r=row: self.type_gewijzigd(r, text))
        self.tabel.setCellWidget(row, 1, combo)
        self.tabel.setItem(row, 2, QTableWidgetItem(var.adres))
        self.tabel.setItem(row, 3, QTableWidgetItem(var.beschrijving))

        # Maak verwijderknop
        verwijder_knop = QPushButton("X")
        verwijder_knop.clicked.connect(partial(self.verwijder_variabele, row))
        self.tabel.setCellWidget(row, 4, verwijder_knop)

    def voeg_toe(self):
        dialoog = VariabeleBewerkenDialoog()
        if dialoog.exec() == QDialog.Accepted:
            var = dialoog.get_variabele()
            self.variabelen_lijst.append(var)
            self.voeg_tabelrij_toe(var)

    def bewerk_geselecteerd(self):
        row = self.tabel.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Geen selectie", "Selecteer een rij om te bewerken.")
            return

        huidige = self.variabelen_lijst[row]
        dialoog = VariabeleBewerkenDialoog(huidige)
        if dialoog.exec() == QDialog.Accepted:
            nieuwe = dialoog.get_variabele()
            self.variabelen_lijst[row] = nieuwe
            self.tabel.setItem(row, 0, QTableWidgetItem(nieuwe.naam))
            self.tabel.setItem(row, 1, QTableWidgetItem(nieuwe.var_type))
            self.tabel.setItem(row, 2, QTableWidgetItem(nieuwe.adres))
            self.tabel.setItem(row, 3, QTableWidgetItem(nieuwe.beschrijving))

    def verwijder_variabele(self, row):
        confirm = QMessageBox.question(
            self, "Bevestigen", "Weet je zeker dat je deze variabele wilt verwijderen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            del self.variabelen_lijst[row]
            self.tabel.removeRow(row)

    def verwerk_bewerking(self, item):
        row = item.row()
        col = item.column()

        if row < 0 or row >= len(self.variabelen_lijst):
            return  # Veiligheidscheck

        waarde = item.text()
        variabele = self.variabelen_lijst[row]

        if col == 0:
            variabele.naam = waarde
        elif col == 1:
            variabele.var_type = waarde
        elif col == 2:
            variabele.adres = waarde
        elif col == 3:
            variabele.beschrijving = waarde

    def type_gewijzigd(self, row, nieuwe_type):
        if row < 0 or row >= len(self.variabelen_lijst):
            return
        self.variabelen_lijst[row].var_type = nieuwe_type


class VariabeleBewerkenDialoog(QDialog):
    def __init__(self, variabele=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Variabele instellen")
        self.setModal(True)

        self.layout = QVBoxLayout(self)

        self.naam_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["bit", "int", "float", "string"])
        self.adres_input = QLineEdit()
        self.beschrijving_input = QLineEdit()

        self.layout.addWidget(QLabel("Naam:"))
        self.layout.addWidget(self.naam_input)
        self.layout.addWidget(QLabel("Type:"))
        self.layout.addWidget(self.type_input)
        self.layout.addWidget(QLabel("Adres:"))
        self.layout.addWidget(self.adres_input)
        self.layout.addWidget(QLabel("Beschrijving:"))
        self.layout.addWidget(self.beschrijving_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        if variabele:
            self.naam_input.setText(variabele.naam)
            self.type_input.setCurrentText(variabele.var_type)
            self.adres_input.setText(variabele.adres)
            self.beschrijving_input.setText(variabele.beschrijving)

    def get_variabele(self):
        return Variabele(
            self.naam_input.text(),
            self.type_input.currentText(),
            self.adres_input.text(),
            self.beschrijving_input.text()
        )


# Variabelen lijst klasse

class VariabelenLijst(list):
    def to_list(self):
        return [v.to_dict() for v in self]

    @classmethod
    def from_list(cls, data_list):
        return cls([Variabele.from_dict(data) for data in data_list])
