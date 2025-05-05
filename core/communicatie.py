from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QCheckBox,
    QDialogButtonBox, QVBoxLayout, QGroupBox, QPushButton
)
from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.client.serial import ModbusSerialClient


class CommunicatieDialoog(QDialog):
    def __init__(self, instellingen_obj, parent=None):
        super().__init__(parent)
        self.client = None  # Houd de client bij
        self.setWindowTitle("Communicatie-instellingen")
        self.instellingen_obj = instellingen_obj

        self.main_layout = QVBoxLayout(self)

        # ============ TCP Instellingen ============
        self.tcp_group = QGroupBox("Modbus TCP")
        self.tcp_group.setCheckable(True)
        self.tcp_group.setChecked(self.instellingen_obj.get("Modbus TCP", {}).get("actief", False))

        tcp_form = QFormLayout()

        self.tcp_ip = QLineEdit(
            self.instellingen_obj.get("Modbus TCP", {}).get("instellingen", {}).get("ip", "127.0.0.1"))
        self.tcp_port = QSpinBox()
        self.tcp_port.setMaximum(65535)
        self.tcp_port.setValue(self.instellingen_obj.get("Modbus TCP", {}).get("instellingen", {}).get("poort", 502))

        self.tcp_timeout = QSpinBox()
        self.tcp_timeout.setMaximum(60)
        self.tcp_timeout.setValue(self.instellingen_obj.get("Modbus TCP", {}).get("instellingen", {}).get("timeout", 2))

        tcp_form.addRow("IP-adres", self.tcp_ip)
        tcp_form.addRow("Poort", self.tcp_port)
        tcp_form.addRow("Timeout (s)", self.tcp_timeout)

        self.tcp_group.setLayout(tcp_form)
        self.main_layout.addWidget(self.tcp_group)

        # ============ RTU Instellingen ============
        self.rtu_group = QGroupBox("Modbus RTU")
        self.rtu_group.setCheckable(True)
        self.rtu_group.setChecked(self.instellingen_obj.get("Modbus RTU", {}).get("actief", False))

        rtu_form = QFormLayout()

        self.rtu_com = QLineEdit(
            self.instellingen_obj.get("Modbus RTU", {}).get("instellingen", {}).get("com_port", "COM1"))
        self.rtu_baud = QSpinBox()
        self.rtu_baud.setMaximum(115200)
        self.rtu_baud.setValue(
            self.instellingen_obj.get("Modbus RTU", {}).get("instellingen", {}).get("baudrate", 9600))

        self.rtu_timeout = QSpinBox()
        self.rtu_timeout.setMaximum(60)
        self.rtu_timeout.setValue(self.instellingen_obj.get("Modbus RTU", {}).get("instellingen", {}).get("timeout", 2))

        rtu_form.addRow("COM-poort", self.rtu_com)
        rtu_form.addRow("Baudrate", self.rtu_baud)
        rtu_form.addRow("Timeout (s)", self.rtu_timeout)

        self.rtu_group.setLayout(rtu_form)
        self.main_layout.addWidget(self.rtu_group)

        self.start_stop_button = QPushButton("Start communicatie")
        self.start_stop_button.setCheckable(True)
        self.start_stop_button.clicked.connect(self.toggle_communicatie)
        self.main_layout.addWidget(self.start_stop_button)
        # ============ Buttons ============
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.on_accept)
        self.buttons.rejected.connect(self.reject)
        self.main_layout.addWidget(self.buttons)

    def on_accept(self):
        self.instellingen_obj["Modbus TCP"] = {
            "actief": self.tcp_group.isChecked(),
            "instellingen": {
                "ip": self.tcp_ip.text(),
                "poort": self.tcp_port.value(),
                "timeout": self.tcp_timeout.value()
            }
        }

        self.instellingen_obj["Modbus RTU"] = {
            "actief": self.rtu_group.isChecked(),
            "instellingen": {
                "com_port": self.rtu_com.text(),
                "baudrate": self.rtu_baud.value(),
                "timeout": self.rtu_timeout.value()
            }
        }

        self.accept()

    def toggle_communicatie(self):
        if self.start_stop_button.isChecked():
            self.start_stop_button.setText("Stop communicatie")
            # Emit signaal of start hier eventueel communicatie
            print("⏺️ Communicatie starten")
            self.start_communicatie()
        else:
            self.start_stop_button.setText("Start communicatie")
            # Emit signaal of stop hier eventueel communicatie
            print("⏹️ Communicatie stoppen")
            self.stop_communicatie()

    def start_communicatie(self):
        if self.tcp_group.isChecked():
            ip = self.tcp_ip.text()
            poort = self.tcp_port.value()
            timeout = self.tcp_timeout.value()

            self.client = ModbusTcpClient(
                host=ip,
                port=poort,
                timeout=timeout
            )
            if self.client.connect():
                print("✅ Verbonden via Modbus TCP")
            else:
                print("❌ Verbinden via Modbus TCP mislukt")
                self.client = None

        elif self.rtu_group.isChecked():
            com = self.rtu_com.text()
            baud = self.rtu_baud.value()
            timeout = self.rtu_timeout.value()

            self.client = ModbusSerialClient(
                port=com,
                baudrate=baud,
                timeout=timeout,
                stopbits=1,
                bytesize=8,
                parity='N'
            )
            if self.client.connect():
                print("✅ Verbonden via Modbus RTU")
            else:
                print("❌ Verbinden via Modbus RTU mislukt")
                self.client = None

    def stop_communicatie(self):
        if self.client:
            self.client.close()
            print("🔌 Verbinding gesloten")
            self.client = None


class CommunicatieInstellingen:
    def __init__(self, instellingen=None):
        if instellingen is None:
            instellingen = {
                "Modbus TCP": {
                    "actief": False,
                    "instellingen": {
                        "ip": "127.0.0.1",
                        "poort": 502,
                        "timeout": 2
                    }
                },
                "Modbus RTU": {
                    "actief": False,
                    "instellingen": {
                        "com_port": "COM1",
                        "baudrate": 9600,
                        "timeout": 2
                    }
                }
            }
        self.instellingen = instellingen

    def to_dict(self):
        return self.instellingen

    @classmethod
    def from_dict(cls, data):
        return cls(instellingen=data)
