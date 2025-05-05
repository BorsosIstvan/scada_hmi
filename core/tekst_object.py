from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton, QColorDialog, \
    QGraphicsTextItem, QGraphicsPixmapItem


class EenvoudigeTekstDialoog(QDialog):
    def __init__(self, starttekst="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tekst invoeren")

        self.tekst_input = QLineEdit(starttekst)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Voer de tekst in:"))
        layout.addWidget(self.tekst_input)

        self.kleur = QColor("blue")
        self.kleur_button = QPushButton("Kies kleur")
        self.kleur_button.clicked.connect(self.kies_kleur)

        layout.addWidget(self.kleur_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def kies_kleur(self):
        gekozen = QColorDialog.getColor(self.kleur, self, "Kies tekstkleur")
        if gekozen.isValid():
            self.kleur = gekozen


class TekstObject(QGraphicsTextItem):
    def __init__(self, tekst):
        super().__init__(tekst)
        self.setFlags(
            QGraphicsTextItem.ItemIsMovable |
            QGraphicsTextItem.ItemIsSelectable |
            QGraphicsTextItem.ItemIsFocusable
        )
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)

    def wheelEvent(self, event):
        delta = event.delta()
        huidige_font = self.font()
        grootte = huidige_font.pointSize()

        if delta > 0:
            grootte += 1
        elif delta < 0 and grootte > 1:
            grootte -= 1

        nieuwe_font = QFont(huidige_font)
        nieuwe_font.setPointSize(grootte)
        self.setFont(nieuwe_font)

    def mouseDoubleClickEvent(self, event):
        dialoog = EenvoudigeTekstDialoog(self.toPlainText())
        if dialoog.exec():
            nieuwe_tekst = dialoog.tekst_input.text()
            self.setPlainText(nieuwe_tekst)
            nieuwe_kleur = dialoog.kleur
            self.setDefaultTextColor(nieuwe_kleur)

    def to_dict(self):
        return {
            "type": "tekst",
            "tekst": self.toPlainText(),
            "x": self.pos().x(),
            "y": self.pos().y(),
            "kleur": self.defaultTextColor().name(),
            "lettertype": self.font().family(),
            "grootte": self.font().pointSize()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# SCADA BitObject klas


class ScadaBitObject(QGraphicsPixmapItem):
    def __init__(self, afbeelding_true: str, afbeelding_false: str, adres="Q0.0", breedte=64, hoogte=64, parent=None):
        super().__init__(parent)

        self.afbeelding_true = QPixmap(afbeelding_true).scaled(breedte, hoogte)
        self.afbeelding_false = QPixmap(afbeelding_false).scaled(breedte, hoogte)
        self.adres = adres  # zoals 'Q0.0' of 'M10.1'
        self.status = False  # beginstatus

        self.setPixmap(self.afbeelding_false)  # initieel uit
        self.setFlags(
            QGraphicsPixmapItem.ItemIsMovable |
            QGraphicsPixmapItem.ItemIsSelectable
        )
        self.setAcceptHoverEvents(True)

    def set_status(self, status: bool):
        self.status = status
        self.setPixmap(self.afbeelding_true if self.status else self.afbeelding_false)

    def wheelEvent(self, event):
        delta = event.delta()
        factor = 1.1 if delta > 0 else 0.9  # in- of uitzoomen
        self.setScale(self.scale() * factor)

    def mousePressEvent(self, event):
        print("Knop state is:", self.status)
        self.set_status(not self.status)

    def to_dict(self):
        return {
            "type": "bitobject",
            "adres": self.adres,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "breedte": self.pixmap().width(),
            "hoogte": self.pixmap().height(),
            "plaatje_aan": self.afbeelding_true,
            "plaatje_uit": self.afbeelding_false,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        obj = ScadaBitObject(
            afbeelding_true=data["plaatje_aan"],
            afbeelding_false=data["plaatje_uit"],
            adres=data["adres"]
        )
        obj.setPos(float(data["x"]), float(data["y"]))
        if "status" in data:
            obj.set_status(data["status"])
        return obj