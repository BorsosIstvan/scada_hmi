class Variable:
    def __init__(self, naam, var_type, adres, beschrijving=""):
        self.naam = naam
        self.var_type = var_type
        self.adres = adres
        self.beschrijving = beschrijving

    def to_dict(self):
        return {
            "naam": self.naam,
            "var_type": self.var_type,
            "adres": self.adres,
            "beschrijving": self.beschrijving
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            naam=data["naam"],
            var_type=data["var_type"],
            adres=data["adres"],
            beschrijving=data.get("beschrijving", "")
        )


from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt


class VariabeleBewerkenDialoog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Variabele Bewerken")
        self.resize(900, 400)

        # Hoofd-layout
        main_layout = QVBoxLayout(self)

        # Knoppen rechtsboven
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("+")
        self.remove_button = QPushButton("−")
        self.up_button = QPushButton("↑")
        self.down_button = QPushButton("↓")

        for btn in [self.add_button, self.remove_button, self.up_button, self.down_button]:
            btn.setFixedSize(30, 30)
            button_layout.addWidget(btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Tabel
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "#", "Naam", "Type", "Adres", "Beschrijving"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)
        main_layout.addWidget(self.table)

        # Signalen koppelen
        self.add_button.clicked.connect(self.voeg_rij_toe)
        self.remove_button.clicked.connect(self.verwijder_rij)
        self.up_button.clicked.connect(self.verplaats_omhoog)
        self.down_button.clicked.connect(self.verplaats_omlaag)

    def voeg_rij_toe(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(8):
            self.table.setItem(row, col, QTableWidgetItem(""))

        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

    def verwijder_rij(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)
            self.hernummer_rijen()

    def verplaats_omhoog(self):
        row = self.table.currentRow()
        if row > 0:
            self.swap_rows(row, row - 1)
            self.table.selectRow(row - 1)

    def verplaats_omlaag(self):
        row = self.table.currentRow()
        if row < self.table.rowCount() - 1:
            self.swap_rows(row, row + 1)
            self.table.selectRow(row + 1)

    def swap_rows(self, row1, row2):
        for col in range(self.table.columnCount()):
            item1 = self.table.takeItem(row1, col)
            item2 = self.table.takeItem(row2, col)
            self.table.setItem(row1, col, item2)
            self.table.setItem(row2, col, item1)
        self.hernummer_rijen()

    def hernummer_rijen(self):
        for i in range(self.table.rowCount()):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
