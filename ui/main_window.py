from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QGraphicsItemGroup
)
from PySide6.QtGui import QFont
from graphics.canvas_view import CanvasView
from graphics.movable_item import MovableItem
import json

from graphics.scada_object import SCADAObject
from ui.object_properties_dialog import ObjectPropertiesDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCADA HMI")
        self.setGeometry(100, 100, 800, 600)

        self.canvas_view = CanvasView()
        self.setCentralWidget(self.canvas_view)

        self._create_menu()

    def _create_menu(self):
        menu_bar = self.menuBar()

        # Bestand menu
        bestand_menu = menu_bar.addMenu("Bestand")

        openen_action = QAction("Openen", self)
        openen_action.triggered.connect(self.openen)

        opslaan_action = QAction("Opslaan", self)
        opslaan_action.triggered.connect(self.opslaan)

        bestand_menu.addAction(openen_action)
        bestand_menu.addAction(opslaan_action)

        # Gereedschap menu
        tools_menu = menu_bar.addMenu("Gereedschap")

        voeg_toe_action = QAction("Voeg object toe", self)
        voeg_toe_action.triggered.connect(self.voeg_object_toe)
        tools_menu.addAction(voeg_toe_action)

        eigenschappen_action = QAction("Eigenschappen", self)
        eigenschappen_action.setShortcut("Ctrl+E")
        eigenschappen_action.triggered.connect(self.open_eigenschappen_dialoog)
        tools_menu.addAction(eigenschappen_action)

        bewerken_menu = menu_bar.addMenu("Bewerken")

        kopieer_actie = QAction("Kopieer", self)
        shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)
        shortcut_copy.activated.connect(self.kopieer_objecten)
        kopieer_actie.triggered.connect(self.kopieer_objecten)
        bewerken_menu.addAction(kopieer_actie)

        plak_actie = QAction("Plak", self)
        shortcut_paste = QShortcut(QKeySequence("Ctrl+V"), self)
        shortcut_paste.activated.connect(self.plak_objecten)
        plak_actie.triggered.connect(self.plak_objecten)
        bewerken_menu.addAction(plak_actie)

        knip_action = QAction("Knippen", self)
        shortcut_cut = QShortcut(QKeySequence("Ctrl+X"), self)
        shortcut_cut.activated.connect(self.knip_geselecteerde_items)
        knip_action.triggered.connect(self.knip_geselecteerde_items)
        bewerken_menu.addAction(knip_action)

        verwijder_action = QAction("Verwijder geselecteerde objecten", self)
        verwijder_action.setShortcut("Delete")  # optioneel sneltoets
        verwijder_action.triggered.connect(self.verwijder_geselecteerde_objecten)
        bewerken_menu.addAction(verwijder_action)

    def voeg_object_toe(self):
        item = SCADAObject(0, 0, 100, 50, label="Nieuwe knop", plc_tag={"plc": "PLC_1", "type": "Coil", "address": 12})
        self.canvas_view.scene().addItem(item)

    def opslaan(self):
        bestand, _ = QFileDialog.getSaveFileName(self, "Bestand opslaan", "", "JSON-bestanden (*.json)")
        if bestand:
            data = []
            for item in self.canvas_view.scene().items():
                if isinstance(item, SCADAObject):
                    data.append(item.to_dict())
            with open(bestand, "w") as f:
                json.dump(data, f, indent=4)

    def opslaan_als(self):
        self.opslaan()  # voorlopig zelfde

    def openen(self):
        bestand, _ = QFileDialog.getOpenFileName(self, "Bestand openen", "", "JSON-bestanden (*.json)")
        if bestand:
            with open(bestand, "r") as f:
                data = json.load(f)
            self.canvas_view.scene().clear()
            for item_data in data:
                if item_data.get("type") == "SCADAObject":
                    item = SCADAObject.from_dict(item_data)
                    self.canvas_view.scene().addItem(item)

    def verwijder_geselecteerde_objecten(self):
        selected_items = self.canvas_view.scene().selectedItems()
        if not selected_items:
            print("Geen objecten geselecteerd om te verwijderen.")
            return

        for item in selected_items:
            self.canvas_view.scene().removeItem(item)

        print(f"{len(selected_items)} object(en) verwijderd.")

    def kopieer_objecten(self):
        self.gekopieerde_items = []
        for item in self.canvas_view.scene().selectedItems():
            if isinstance(item, SCADAObject):
                self.gekopieerde_items.append(item.to_dict())

    def plak_objecten(self):
        for i, item_data in enumerate(self.gekopieerde_items):
            # Maak het SCADA-object aan uit de opgeslagen data
            item = SCADAObject.from_dict(item_data)

            # Verplaats elk object een beetje (optioneel, afhankelijk van de positie)
            offset = 0#10 * (i + 1)  # Zorg ervoor dat objecten niet precies overlappen
            item.setPos(item_data["x"] + offset, item_data["y"] + offset)
            print(item_data["x"])

            # Voeg het item toe aan de scene
            self.canvas_view.scene().addItem(item)

    def knip_geselecteerde_items(self):
        self.kopieer_objecten()
        self.verwijder_geselecteerde_objecten()

    def open_eigenschappen_dialoog(self):
        scene = self.canvas_view.scene()
        selected_items = scene.selectedItems()

        if selected_items:
            item = selected_items[0]  # We nemen het eerste geselecteerde item
            if hasattr(item, 'label'):  # Optioneel: check of het een SCADAObject is
                dialoog = ObjectPropertiesDialog(self, scada_object=item)
                if dialoog.exec():
                    dialoog.apply_changes()

    def apply_object_properties(self, item, dialoog):
        from PySide6.QtGui import QFont

        # Label tekst
        item.set_label(dialoog.label_input.text())

        # Naam instellen
        item.naam = dialoog.naam_input.text()

        # PLC tag info
        item.plc_tag["plc"] = dialoog.plc_input.text()
        item.plc_tag["type"] = dialoog.plc_type_input.currentText()
        item.plc_tag["address"] = dialoog.plc_address_input.value()

        # Font instellen
        font = QFont()
        font.setFamily(dialoog.label_font_input.currentFont().family())
        font.setPointSize(dialoog.label_font_size_input.value())
        item.label_item.setFont(font)

        # Font info opslaan
        item.label_font = font.family()
        item.label_font_size = font.pointSize()

        # Label centreren
        item._update_label_position()
