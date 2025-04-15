from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QGraphicsItemGroup
)
from graphics.canvas_view import CanvasView
from graphics.movable_item import MovableItem
import json

from ui.properties_dialog import PropertiesDialog


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

        opslaan_als_action = QAction("Opslaan als...", self)
        opslaan_als_action.triggered.connect(self.opslaan_als)

        bestand_menu.addAction(openen_action)
        bestand_menu.addAction(opslaan_action)
        bestand_menu.addAction(opslaan_als_action)

        # Gereedschap menu
        tools_menu = menu_bar.addMenu("Gereedschap")

        voeg_toe_action = QAction("Voeg object toe", self)
        voeg_toe_action.triggered.connect(self.voeg_object_toe)
        tools_menu.addAction(voeg_toe_action)

        group_action = QAction("Groepeer", self)
        group_action.triggered.connect(self.groepeer_geselecteerde_items)
        tools_menu.addAction(group_action)

        ungroup_action = QAction("Ontgroeperen", self)
        ungroup_action.triggered.connect(self.ontgroepeer_geselecteerde_groep)
        tools_menu.addAction(ungroup_action)

        wissel_action = QAction("Wissel geselecteerde objecten", self)
        wissel_action.triggered.connect(self.wissel_geselecteerde_objecten)
        tools_menu.addAction(wissel_action)

        verwijder_action = QAction("Verwijder geselecteerde objecten", self)
        verwijder_action.setShortcut("Delete")  # optioneel sneltoets
        verwijder_action.triggered.connect(self.verwijder_geselecteerde_objecten)
        tools_menu.addAction(verwijder_action)

        prop_action = QAction("Eigenschappen", self)
        prop_action.triggered.connect(self.show_properties)
        tools_menu.addAction(prop_action)

        bewerken_menu = menu_bar.addMenu("Bewerken")

        kopieer_actie = QAction("Kopieer", self)
        shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)
        shortcut_copy.activated.connect(self.kopieer_geselecteerde_items)
        kopieer_actie.triggered.connect(self.kopieer_geselecteerde_items)
        bewerken_menu.addAction(kopieer_actie)

        plak_actie = QAction("Plak", self)
        shortcut_paste = QShortcut(QKeySequence("Ctrl+V"), self)
        shortcut_paste.activated.connect(self.plak_items)
        plak_actie.triggered.connect(self.plak_items)
        bewerken_menu.addAction(plak_actie)

        knip_action = QAction("Knippen", self)
        shortcut_cut = QShortcut(QKeySequence("Ctrl+X"), self)
        shortcut_cut.activated.connect(self.knip_geselecteerde_items)
        knip_action.triggered.connect(self.knip_geselecteerde_items)
        bewerken_menu.addAction(knip_action)

    def voeg_object_toe(self):
        item = MovableItem(0, 0, 100, 50)
        self.canvas_view.scene().addItem(item)

    def opslaan(self):
        bestandsnaam, _ = QFileDialog.getSaveFileName(self, "Opslaan", "", "JSON bestanden (*.json)")
        if bestandsnaam:
            self._bewaar_canvas(bestandsnaam)

    def opslaan_als(self):
        self.opslaan()  # voorlopig zelfde

    def openen(self):
        bestandsnaam, _ = QFileDialog.getOpenFileName(self, "Openen", "", "JSON bestanden (*.json)")
        if bestandsnaam:
            self._laad_canvas(bestandsnaam)

    def _bewaar_canvas(self, pad):
        items = self.canvas_view.scene().items()
        data = []
        for item in items:
            if isinstance(item, MovableItem):
                rect = item.rect()
                pos = item.pos()
                data.append({
                    "x": pos.x(),
                    "y": pos.y(),
                    "w": rect.width(),
                    "h": rect.height(),
                    "properties": item.properties
                })

        with open(pad, "w") as f:
            json.dump(data, f)

    def _laad_canvas(self, pad):
        try:
            with open(pad, "r") as f:
                data = json.load(f)
            self.canvas_view.scene().clear()
            for item_data in data:
                item = MovableItem(item_data["x"], item_data["y"], item_data["w"], item_data["h"])
                if "properties" in item_data:
                    item.properties = item_data["properties"]
                    item.update_label()
                self.canvas_view.scene().addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Fout bij laden", str(e))

    def groepeer_geselecteerde_items(self):
        selected_items = self.canvas_view.scene().selectedItems()

        if len(selected_items) < 2:
            print("Selecteer minstens twee objecten om te groeperen.")
            return

        # Maak een nieuwe groep aan en voeg de items toe
        group = self.canvas_view.scene().createItemGroup(selected_items)
        group.setFlags(
            QGraphicsItemGroup.ItemIsMovable |
            QGraphicsItemGroup.ItemIsSelectable
        )
        print("Objecten gegroepeerd.")

    def ontgroepeer_geselecteerde_groep(self):
        selected_items = self.canvas_view.scene().selectedItems()

        for item in selected_items:
            if isinstance(item, QGraphicsItemGroup):
                self.canvas_view.scene().destroyItemGroup(item)
                print("Groep ontbonden.")
            else:
                print("Geen groep geselecteerd.")

    def wissel_geselecteerde_objecten(self):
        selected_items = self.canvas_view.scene().selectedItems()
        if len(selected_items) < 2:
            print("Selecteer minstens twee objecten om te wisselen.")
            return

        # Bewaar de originele posities
        positions = [item.pos() for item in selected_items]

        # Verschuif posities in ronde
        for i, item in enumerate(selected_items):
            new_pos = positions[(i + 1) % len(positions)]
            item.setPos(new_pos)

        print("Geselecteerde objecten gewisseld.")

    def verwijder_geselecteerde_objecten(self):
        selected_items = self.canvas_view.scene().selectedItems()
        if not selected_items:
            print("Geen objecten geselecteerd om te verwijderen.")
            return

        for item in selected_items:
            self.canvas_view.scene().removeItem(item)

        print(f"{len(selected_items)} object(en) verwijderd.")

    def show_properties(self):
        selected_items = self.canvas_view.scene().selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            if hasattr(item, "properties"):
                dialog = PropertiesDialog(item.properties)
                if dialog.exec():
                    item.properties = dialog.get_properties()
                    item.update_label()

    def serialize_item(item):
        return {
            "x": item.pos().x(),
            "y": item.pos().y(),
            "rect": [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()],
            "properties": item.properties,
        }

    def deserialize_item(data):
        rect = QRectF(*data["rect"])
        item = MovableItem(rect)
        item.setPos(QPointF(data["x"], data["y"]))
        item.properties = data["properties"]
        item.update_label()
        return item

    def kopieer_geselecteerde_items(self):
        self.clipboard = []
        for item in self.canvas_view.scene().selectedItems():
            if isinstance(item, MovableItem):
                rect = item.rect()
                self.clipboard.append({
                    "x": item.x(),
                    "y": item.y(),
                    "w": rect.width(),
                    "h": rect.height(),
                    "properties": item.properties.copy()
                })

    def plak_items(self):
        for item_data in self.clipboard:
            new_x = item_data["x"] + 20  # Verschuif een beetje
            new_y = item_data["y"] + 20
            item = MovableItem(new_x, new_y, item_data["w"], item_data["h"])
            item.properties = item_data["properties"]
            item.update_label()
            self.canvas_view.scene().addItem(item)

    def knip_geselecteerde_items(self):
        self.kopieer_geselecteerde_items()
        self.verwijder_geselecteerde_objecten()

