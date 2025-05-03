import os.path

from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QGraphicsTextItem, QDialog
from PySide6.QtGui import QAction, QFont, QColor

from core.canvas_object import EenvoudigeTekstDialoog, SchaalbaarTekstItem, ScadaBitObject
from project.project_data import nieuw_project, opslaan_project, openen_project
from ui.canvas_settings_dialog import CanvasSettingsDialog
from ui.canvas_view import CanvasView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCADA HMI")
        self.resize(800, 600)

        self.project_data = None
        self.canvas_view = CanvasView(self)
        self.setCentralWidget(self.canvas_view)

        self._create_menubalk()
        self.nieuw_project_aanmaken()

    def _create_menubalk(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        actie_nieuw = QAction("Nieuw project", self)
        actie_nieuw.triggered.connect(self.nieuw_project_aanmaken)
        file_menu.addAction(actie_nieuw)

        actie_open = QAction("Project openen", self)
        actie_open.triggered.connect(self.openen_project)
        file_menu.addAction(actie_open)

        actie_opslaan = QAction("Project opslaan", self)
        actie_opslaan.triggered.connect(self.opslaan_project)
        file_menu.addAction(actie_opslaan)

        file_menu.addSeparator()

        actie_exit = QAction("Afsluiten", self)
        actie_exit.triggered.connect(self.close)
        file_menu.addAction(actie_exit)

        instellingen_menu = menu_bar.addMenu("Instellingen")

        canvas_actie = QAction("Canvas instellingen", self)
        canvas_actie.triggered.connect(self.open_canvas_instellingen)
        instellingen_menu.addAction(canvas_actie)

        # Tools menu
        tools_menu = menu_bar.addMenu("Gereedschap")

        add_text_action = QAction("Tekstobject toevoegen", self)
        add_text_action.triggered.connect(self.voeg_tekstobject_toe)
        tools_menu.addAction(add_text_action)

        toon_text = QAction("Tekstobject tonen", self)
        toon_text.triggered.connect(self.sla_canvasobjecten_op)
        tools_menu.addAction(toon_text)

        add_bitobject_action = QAction("Button/Lamp toevoegen", self)
        add_bitobject_action.triggered.connect(self.voeg_bitobject_toe)
        tools_menu.addAction(add_bitobject_action)


    def nieuw_project_aanmaken(self):
        self.project_data = nieuw_project("Nieuw project")
        self.canvas_view.setCanvasSettings(self.project_data["canvas"])
        self.canvas_view.clear()
        self.update_venstertitel()
        # QMessageBox.information(self, "Nieuw", "Nieuw SCADA-project gestart.")

    def openen_project(self):
        bestand, _ = QFileDialog.getOpenFileName(self, "Open project", "", "SCADA Project (*.scada)")
        if bestand:
            self.project_data = openen_project(bestand)
            self.canvas_view.setCanvasSettings(self.project_data["canvas"])
            self.canvas_view.clear()
            self.update_venstertitel()
            QMessageBox.information(self, "Geopend", f"Project geladen uit:\n{bestand}")

        for obj in self.project_data.get("objecten", []):
            if obj["type"] == "tekst":
                self.voeg_tekstobject_toe(
                    tekst=obj["tekst"],
                    x=obj["x"],
                    y=obj["y"],
                    kleur=obj["kleur"],
                    lettertype=obj["lettertype"],
                    grootte=obj["grootte"]
                )

    def opslaan_project(self):
        if self.project_data:
            bestand, _ = QFileDialog.getSaveFileName(self, "Opslaan project", "", "SCADA Project (*.scada)")
            if bestand:
                if not bestand.endswith(".scada"):
                    bestand += ".scada"
                self.project_data["metadata"]["naam"] = os.path.basename(bestand)
                opslaan_project(self.project_data, bestand)
                QMessageBox.information(self, "Opgeslagen", f"Project opgeslagen als:\n{bestand}")
        else:
            QMessageBox.warning(self, "Geen project", "Er is nog geen project om op te slaan.")

    def update_venstertitel(self):
        if self.project_data:
            naam = self.project_data["metadata"]["naam"]
            self.setWindowTitle(f"SCADA HMI - {naam}")

    def open_canvas_instellingen(self):
        if not self.project_data:
            QMessageBox.warning(self, "Geen project", "Open of maak eerst een project aan.")
            return

        dialog = CanvasSettingsDialog(self.project_data["canvas"], self)
        if dialog.exec():
            nieuwe_settings = dialog.opgehaalde_settings()
            self.project_data["canvas"] = nieuwe_settings
            self.canvas_view.setCanvasSettings(nieuwe_settings)
            self.update_venstertitel()  # 👈 Venstertitel updaten

    def voeg_tekstobject_toe(self, tekst="Hoi wereld", x=100, y=100, kleur="blue", lettertype="Arial", grootte=16):

        text_item = SchaalbaarTekstItem(str(tekst))
        text_item.setPos(QPointF(x, y))
        text_item.setFont(QFont(lettertype, grootte))
        text_item.setDefaultTextColor(QColor(kleur))

        self.canvas_view.scene.addItem(text_item)

    def sla_canvasobjecten_op(self):
        objecten = []
        for item in self.canvas_view.scene.items():
            object_data = {
                "type": "tekst",
                "tekst": item.toPlainText(),
                "x": item.pos().x(),
                "y": item.pos().y(),
                "kleur": item.defaultTextColor().name(),
                "lettertype": item.font().family(),
                "grootte": item.font().pointSize()
            }
            objecten.append(object_data)
            print(item.toPlainText())
        self.project_data["objecten"] = objecten

    def voeg_bitobject_toe(self):
        bitobject = ScadaBitObject("graphics/lamp_on.png", "graphics/lamp_off.png", adres="Q0.0")
        bitobject.setPos(100, 100)
        self.canvas_view.scene.addItem(bitobject)