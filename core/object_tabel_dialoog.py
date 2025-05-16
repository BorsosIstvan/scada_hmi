from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)
from PySide6.QtCore import Qt


class ObjectTabelDialoog(QDialog):
    def __init__(self, lijst, kolommen, titel="Gegevens Bewerken", dropdown_kolommen=None, object_klasse=None):
        super().__init__()
        self.setWindowTitle(titel)
        self.resize(900, 400)

        self.kolomnamen = kolommen
        self.aantal_kolommen = len(kolommen)
        self.data_lijst = lijst
        self.dropdown_kolommen = dropdown_kolommen or {}
        self.object_klasse = object_klasse

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, self.aantal_kolommen)
        self.table.setHorizontalHeaderLabels(self.kolomnamen)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        knop_layout = QHBoxLayout()
        self.add_button = QPushButton("+")
        self.remove_button = QPushButton("−")
        self.up_button = QPushButton("⬆")
        self.down_button = QPushButton("⬇")
        self.save_button = QPushButton("Opslaan")
        for knop in [self.add_button, self.remove_button, self.up_button, self.down_button, self.save_button]:
            knop_layout.addWidget(knop)
        knop_layout.addStretch()
        layout.addLayout(knop_layout)

        self.add_button.clicked.connect(self.voeg_rij_toe)
        self.remove_button.clicked.connect(self.verwijder_rij)
        self.up_button.clicked.connect(self.verplaats_rij_omhoog)
        self.down_button.clicked.connect(self.verplaats_rij_omlaag)
        self.save_button.clicked.connect(self.opslaan)

        self.vul_tabel()

    def vul_tabel(self):
        self.table.setRowCount(0)
        for item in self.data_lijst:
            self.voeg_rij_toe(item)

    def voeg_rij_toe(self, waarden=None):
        rij = self.table.rowCount()
        self.table.insertRow(rij)

        for kolom in range(self.aantal_kolommen):
            kolomnaam = self.kolomnamen[kolom]
            waarde = ""

            if waarden:
                if isinstance(waarden, dict):
                    waarde = str(waarden.get(kolomnaam, ""))
                else:
                    waarde = str(getattr(waarden, kolomnaam, ""))

            if kolomnaam in self.dropdown_kolommen:
                combo = QComboBox()
                combo.addItems(self.dropdown_kolommen[kolomnaam])
                index = combo.findText(waarde)
                if index >= 0:
                    combo.setCurrentIndex(index)
                self.table.setCellWidget(rij, kolom, combo)
            else:
                self.table.setItem(rij, kolom, QTableWidgetItem(waarde))

    def verwijder_rij(self):
        rij = self.table.currentRow()
        if rij >= 0:
            self.table.removeRow(rij)

    def verplaats_rij_omhoog(self):
        rij = self.table.currentRow()
        if rij > 0:
            self.wissel_rijen(rij, rij - 1)
            self.table.selectRow(rij - 1)

    def verplaats_rij_omlaag(self):
        rij = self.table.currentRow()
        if rij < self.table.rowCount() - 1:
            self.wissel_rijen(rij, rij + 1)
            self.table.selectRow(rij + 1)

    def wissel_rijen(self, rij1, rij2):
        for kolom in range(self.aantal_kolommen):
            kolomnaam = self.kolomnamen[kolom]

            if kolomnaam in self.dropdown_kolommen:
                widget1 = self.table.cellWidget(rij1, kolom)
                widget2 = self.table.cellWidget(rij2, kolom)
                if widget1 and widget2:
                    t1 = widget1.currentText()
                    t2 = widget2.currentText()
                    widget1.setCurrentText(t2)
                    widget2.setCurrentText(t1)
            else:
                item1 = self.table.item(rij1, kolom)
                item2 = self.table.item(rij2, kolom)
                t1 = item1.text() if item1 else ""
                t2 = item2.text() if item2 else ""
                self.table.setItem(rij1, kolom, QTableWidgetItem(t2))
                self.table.setItem(rij2, kolom, QTableWidgetItem(t1))

    def opslaan(self):
        self.data_lijst.clear()
        for rij in range(self.table.rowCount()):
            waarden = {}
            for kolom in range(self.aantal_kolommen):
                kolomnaam = self.kolomnamen[kolom]
                if kolomnaam in self.dropdown_kolommen:
                    combo = self.table.cellWidget(rij, kolom)
                    waarden[kolomnaam] = combo.currentText() if combo else ""
                else:
                    item = self.table.item(rij, kolom)
                    waarden[kolomnaam] = item.text() if item else ""

            if self.object_klasse:
                self.data_lijst.append(self.object_klasse.from_dict(waarden))
            else:
                self.data_lijst.append(waarden)

        self.accept()
