import os.path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QGraphicsTextItem, QDialog
from PySide6.QtGui import QAction, QFont, QColor

from core import project_context
from core.object_tabel_dialoog import ObjectTabelDialoog
from core.project_context import variabelen_lijst
from core.scada_image_object import ScadaImageObject
from core.tekst_object import EenvoudigeTekstDialoog, TekstObject, ScadaBitObject
from core.communicatie import CommunicatieDialoog, CommunicatieInstellingen
from core.scada_object import ScadaObject, InstellingenDialoog
from core.variabele_object import VariabelenDialoog, Variabele, VariabelenLijst
from core.variable_object import VariabeleBewerkenDialoog
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

        com_setting = QAction("Communicatie instellen", self)
        com_setting.triggered.connect(self.open_communicatie_dialoog)
        instellingen_menu.addAction(com_setting)

        var_setting = QAction("Variabelen instellen", self)
        var_setting.triggered.connect(self.open_object_tabel_dialoog)
        instellingen_menu.addAction(var_setting)

        # Tools menu
        tools_menu = menu_bar.addMenu("Gereedschap")

        add_text_action = QAction("Tekstobject toevoegen", self)
        add_text_action.triggered.connect(self.voeg_tekstobject_toe)
        tools_menu.addAction(add_text_action)

        toon_text = QAction("Koppelingen tonen", self)
        toon_text.triggered.connect(self.koppelingen)
        tools_menu.addAction(toon_text)

        add_bitobject_action = QAction("Button/Lamp toevoegen", self)
        add_bitobject_action.triggered.connect(self.voeg_scada_image_object_toe)
        tools_menu.addAction(add_bitobject_action)

        actie_nieuw_object = QAction("Nieuw Object", self)
        actie_nieuw_object.triggered.connect(self.voeg_object_toe)
        tools_menu.addAction(actie_nieuw_object)

    def nieuw_project_aanmaken(self):
        self.project_data = nieuw_project("Nieuw project")
        self.canvas_view.setCanvasSettings(self.project_data["canvas"])
        self.canvas_view.clear()
        self.update_venstertitel()
        project_context.variabelen_lijst = VariabelenLijst()
        # QMessageBox.information(self, "Nieuw", "Nieuw SCADA-project gestart.")

    def openen_project(self):
        bestand, _ = QFileDialog.getOpenFileName(self, "Open project", "", "SCADA Project (*.scada)")
        if bestand:
            self.project_data = openen_project(bestand)
            self.canvas_view.setCanvasSettings(self.project_data["canvas"])
            self.canvas_view.clear()
            self.update_venstertitel()
            project_context.variabelen_lijst = VariabelenLijst.from_list(self.project_data.get("variabelen", []))
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

        for obj_data in self.project_data.get("objecten", []):
            if obj_data["type"] == "scadaimageobject":
                obj = ScadaImageObject.from_dict(obj_data)
                self.canvas_view.scene.addItem(obj)

        for obj in self.project_data.get("objecten", []):
            if obj["type"] == "scadaobject":
                nieuw_obj = ScadaObject(
                    tekst=obj["tekst"],
                    pad_aan=obj["pad_aan"],
                    pad_uit=obj["pad_uit"],
                    adres=obj["adres"],
                    status=obj["status"],
                    breedte=obj["breedte"],
                    hoogte=obj["hoogte"],
                    variabele=obj["variabele"]
                )
                nieuw_obj.setPos(float(obj["x"]), float(obj["y"]))
                nieuw_obj.setScale(obj["schaal"])
                self.canvas_view.scene.addItem(nieuw_obj)

    def opslaan_project(self):
        self.sla_objecten_op()
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

        text_item = TekstObject(str(tekst))
        text_item.setPos(QPointF(x, y))
        text_item.setFont(QFont(lettertype, grootte))
        text_item.setDefaultTextColor(QColor(kleur))

        self.canvas_view.scene.addItem(text_item)

    def sla_tekstobjecten_op(self):
        self.project_data["objecten"] = []

        for item in self.canvas_view.scene.items():
            if isinstance(item, TekstObject):
                self.project_data["objecten"].append(item.to_dict())

    def voeg_bitobject_toe(self):
        bitobject = ScadaBitObject("graphics/lamp_on.png", "graphics/lamp_off.png", adres="Q0.0")
        bitobject.setPos(100, 100)
        self.canvas_view.scene.addItem(bitobject)

    def sla_bitobjecten_op(self):
        self.project_data["objecten"] = []

        for item in self.canvas_view.scene.items():
            if isinstance(item, ScadaBitObject):
                self.project_data["objecten"].append(item.to_dict())

    def voeg_scada_image_object_toe(self):
        siobject = ScadaImageObject(
            x=100,
            y=100,
            pad_aan="graphics/lamp_on.png",
            pad_uit="graphics/lamp_off.png",
            status=False,
        )
        siobject.setPos(100,100)
        self.canvas_view.scene.addItem(siobject)

    def sla_scada_image_object_op(self):
        self.project_data["objecten"] = []

        for item in self.canvas_view.scene.items():
            if isinstance(item, ScadaImageObject):
                self.project_data["objecten"].append(item.to_dict())


    def sla_projectobjecten_op(self):
        self.project_data["objecten"] = []

        for item in self.canvas_view.scene.items():
            if isinstance(item, TekstObject) or isinstance(item, ScadaImageObject):
                self.project_data["objecten"].append(item.to_dict())

    from core.scada_object import ScadaObject

    def voeg_object_toe(self):
        nieuw_obj = ScadaObject(
            x=100,
            y=100,
            tekst="Lampje",
            kleur="blue",
            lettertype="Arial",
            grootte=12,
            pad_aan="graphics/lamp_on.png",
            pad_uit="graphics/lamp_off.png",
            status=False,
            breedte=50,
            hoogte=50,
            adres="Q0.0"
        )
        self.canvas_view.scene.addItem(nieuw_obj)
        self.project_data["objecten"].append(nieuw_obj)

    def sla_objecten_op(self):
        self.project_data["objecten"] = []

        for item in self.canvas_view.scene.items():
            if isinstance(item, ScadaObject):
                self.project_data["objecten"].append(item.to_dict())
        for item in self.canvas_view.scene.items():
            if isinstance(item, TekstObject):
                self.project_data["objecten"].append(item.to_dict())
        for item in self.canvas_view.scene.items():
            if isinstance(item, ScadaImageObject):
                self.project_data["objecten"].append(item.to_dict())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            geselecteerde_items = self.canvas_view.scene.selectedItems()
            for item in geselecteerde_items:
                self.canvas_view.scene.removeItem(item)

    def open_communicatie_dialoog(self):
        # instellingen_obj = CommunicatieInstellingen().to_dict()
        instellingen_obj = self.project_data["communicatie"]
        dialoog = CommunicatieDialoog(instellingen_obj)
        if dialoog.exec():
            self.project_data["communicatie"] = instellingen_obj
            print(instellingen_obj)  # bevat beide TCP en RTU instellingen

    def open_variabelen_dialoog(self):
        dialoog = VariabelenDialoog(project_context.variabelen_lijst)
        if dialoog.exec():
            self.project_data["variabelen"] = project_context.variabelen_lijst.to_list()

    def open_variabele_bewerken_dialoog(self):
        dialoog = VariabeleBewerkenDialoog()
        if dialoog.exec():
            self.project_data["variabelen"] = project_context.variabelen_lijst.to_list()

    def open_object_tabel_dialoog(self):
        var = project_context.variabelen_lijst
        print(var)
        kolommen = ["naam", "type", "adres", "waarde", "beschrijving"]
        dropdowns = {
            "type": ["BOOL", "INT", "REAL"],
            "adres": ["%IX0.0", "%IX0.1","%IX0.2","%IX0.3","%QX0.0","%QX0.1","%IW0", "%QW0"]
        }
        dialoog = ObjectTabelDialoog(var, kolommen, "variabelen beheren", dropdowns, object_klasse=Variabele)
        if dialoog.exec():
            print(var)
            self.project_data["variabelen"] = project_context.variabelen_lijst.to_list()
            print(self.project_data["variabelen"])

    def koppelingen(self):
        koppelingen = {}
        for obj in self.project_data["objecten"]:
            naam = obj.get("variabele", None)
            if not naam:
                continue
            adres = None

            # Zoek het adres dat bij de naam hoort
            for var in project_context.variabelen_lijst:
                if var.naam == naam:
                    adres = var.adres
                    break

            # Voeg toe aan koppelingen als er een adres is gevonden
            if adres:
                if adres not in koppelingen:
                    koppelingen[adres] = []
                koppelingen[adres].append(obj.get("variabele"))

        print(koppelingen)
