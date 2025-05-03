import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QGraphicsView,
    QGraphicsScene, QGraphicsTextItem, QAction, QMenu
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter


class CanvasObject:
    def __init__(self, object_data):
        self.id = object_data.get("id", "")
        self.type = object_data.get("type", "")
        self.x = object_data.get("x", 0)
        self.y = object_data.get("y", 0)
        self.rotation = object_data.get("rotation", 0)
        self.scale = object_data.get("scale", 1.0)
        self.visible = object_data.get("visible", True)
        self.locked = object_data.get("locked", False)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "scale": self.scale,
            "visible": self.visible,
            "locked": self.locked
        }


class TekstObject(CanvasObject):
    def __init__(self, object_data):
        super().__init__(object_data)
        self.text = object_data.get("text", "")
        self.font_family = object_data.get("font_family", "Arial")
        self.font_size = object_data.get("font_size", 14)
        self.font_color = object_data.get("font_color", "#000000")
        self.graphics_item = self.create_graphics_item()

    def create_graphics_item(self):
        item = QGraphicsTextItem(self.text)
        font = QFont(self.font_family, self.font_size)
        item.setFont(font)
        item.setDefaultTextColor(QColor(self.font_color))
        item.setPos(QPointF(self.x, self.y))
        item.setRotation(self.rotation)
        item.setScale(self.scale)
        item.setVisible(self.visible)
        item.setFlag(item.ItemIsSelectable, True)
        item.setFlag(item.ItemIsMovable, not self.locked)
        return item

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "text": self.text,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_color": self.font_color
        })
        return data


class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(Qt.lightGray)
        self.setSceneRect(-5000, -5000, 10000, 10000)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        spacing = 20
        left = int(rect.left()) - (int(rect.left()) % spacing)
        top = int(rect.top()) - (int(rect.top()) % spacing)
        lines = []
        for x in range(left, int(rect.right()), spacing):
            for y in range(top, int(rect.bottom()), spacing):
                lines.append((x, y))
        pen = QColor(200, 200, 200)
        painter.setPen(pen)
        for x, y in lines:
            painter.drawPoint(x, y)

    def laad_objecten(self, objecten):
        for obj in objecten:
            if obj["type"] == "tekst":
                tekst_obj = TekstObject(obj)
                self.addItem(tekst_obj.graphics_item)


class CanvasView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_data = {"objecten": []}
        self.scene = CanvasScene()
        self.view = CanvasView(self.scene)
        self.setCentralWidget(self.view)
        self.setWindowTitle("Nieuw Project")
        self.init_menu()

    def init_menu(self):
        menubar = self.menuBar()

        # Project menu
        project_menu = menubar.addMenu("Project")

        nieuw_action = QAction("Nieuw", self)
        nieuw_action.triggered.connect(self.nieuw_project)
        project_menu.addAction(nieuw_action)

        open_action = QAction("Openen", self)
        open_action.triggered.connect(self.open_project)
        project_menu.addAction(open_action)

        save_action = QAction("Opslaan", self)
        save_action.triggered.connect(self.save_project)
        project_menu.addAction(save_action)

        # Tools menu
        tools_menu = menubar.addMenu("Gereedschap")
        add_text_action = QAction("Tekstobject toevoegen", self)
        add_text_action.triggered.connect(self.voeg_tekstobject_toe)
        tools_menu.addAction(add_text_action)

    def nieuw_project(self):
        self.project_data = {"objecten": []}
        self.scene.clear()
        self.setWindowTitle("Nieuw Project")

    def open_project(self):
        pad, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "JSON bestanden (*.json)")
        if pad:
            with open(pad, "r") as f:
                self.project_data = json.load(f)
            self.scene.clear()
            self.scene.laad_objecten(self.project_data.get("objecten", []))
            self.setWindowTitle(os.path.basename(pad))

    def save_project(self):
        pad, _ = QFileDialog.getSaveFileName(self, "Opslaan Project", "", "JSON bestanden (*.json)")
        if pad:
            with open(pad, "w") as f:
                json.dump(self.project_data, f, indent=4)
            self.setWindowTitle(os.path.basename(pad))

    def voeg_tekstobject_toe(self):
        nieuw_obj = {
            "id": f"tekst_{len(self.project_data['objecten'])+1}",
            "type": "tekst",
            "x": 100,
            "y": 100,
            "text": "Nieuwe Tekst",
            "font_family": "Arial",
            "font_size": 16,
            "font_color": "#000000",
            "visible": True,
            "locked": False
        }
        self.project_data["objecten"].append(nieuw_obj)
        tekst_obj = TekstObject(nieuw_obj)
        self.scene.addItem(tekst_obj.graphics_item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())
