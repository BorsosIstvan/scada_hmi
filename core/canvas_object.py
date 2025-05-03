from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton, QColorDialog, \
    QGraphicsTextItem


class EenvoudigeTekstDialoog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tekst invoeren")

        self.tekst_input = QLineEdit("Hoi wereld")

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

class SchaalbaarTekstItem(QGraphicsTextItem):
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