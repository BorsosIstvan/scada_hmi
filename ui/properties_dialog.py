from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton

class PropertiesDialog(QDialog):
    def __init__(self, properties):
        super().__init__()
        self.setWindowTitle("Eigenschappen")
        self.properties = properties.copy()

        self.layout = QVBoxLayout()

        self.label_input = QLineEdit(self.properties.get("label", ""))
        self.layout.addWidget(QLabel("Label:"))
        self.layout.addWidget(self.label_input)

        # Meer velden kunnen we later toevoegen...

        self.ok_button = QPushButton("OK")
        self.layout.addWidget(self.ok_button)
        self.setLayout(self.layout)

        self.ok_button.clicked.connect(self.accept)

    def get_properties(self):
        self.properties["label"] = self.label_input.text()
        return self.properties
