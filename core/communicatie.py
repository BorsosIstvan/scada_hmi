from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QDialogButtonBox, QVBoxLayout, QGroupBox
)


class CommunicatieDialoog(QDialog):
    def __init__(self, instellingen_obj, parent=None):
        super().__init__(parent)
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


class CommunicatieInstellingen:
    def __init__(self, instellingen=None):
        if instellingen is None:
            instellingen = {
                "Modbus TCP": {
                    "actief": False,
                    "instellingen": {
                        "ip": "127.0.0.1",
                        "poort": 5020,
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


#   Communicatie manager klasse

from pymodbus.client import ModbusTcpClient, ModbusSerialClient


class CommunicatieManager:
    def __init__(self, instellingen):
        self.instellingen = instellingen
        self.tcp_client = None
        self.rtu_client = None
        self.running = False

    def start(self):
        """Start communicatie op basis van actieve instellingen."""
        if self.running:
            return  # reeds actief

        if self.instellingen.get("Modbus TCP", {}).get("actief", False):
            cfg = self.instellingen["Modbus TCP"]["instellingen"]
            self.tcp_client = ModbusTcpClient(
                host=cfg["ip"],
                port=cfg["poort"],
                timeout=cfg["timeout"]
            )
            self.tcp_client.connect()

        if self.instellingen.get("Modbus RTU", {}).get("actief", False):
            cfg = self.instellingen["Modbus RTU"]["instellingen"]
            self.rtu_client = ModbusSerialClient(
                method='rtu',
                port=cfg["com_port"],
                baudrate=cfg["baudrate"],
                timeout=cfg["timeout"]
            )
            self.rtu_client.connect()

        self.running = True

    def stop(self):
        """Stop actieve verbindingen."""
        if self.tcp_client:
            self.tcp_client.close()
            self.tcp_client = None
        if self.rtu_client:
            self.rtu_client.close()
            self.rtu_client = None
        self.running = False

    def update(self):
        """Oproepen in de hoofdloop: regelt automatisch start/stop."""
        from core import project_context  # of waar je deze bewaart

        if project_context.running and not self.running:
            self.start()
        elif not project_context.running and self.running:
            self.stop()

    def lees_holding_register(self, adres, slave_id=1, count=1, protocol="tcp"):
        """Voorbeeld: lees holding registers."""
        if protocol == "tcp" and self.tcp_client:
            return self.tcp_client.read_holding_registers(address=adres, count=count, slave=slave_id)
        elif protocol == "rtu" and self.rtu_client:
            return self.rtu_client.read_holding_registers(address=adres, count=count, slave=slave_id)
        return None

    def lees_input_register(self, adres, slave_id=1, count=1, protocol="tcp"):
        """Voorbeeld: lees ir."""
        if protocol == "tcp" and self.tcp_client:
            return self.tcp_client.read_input_registers(address=adres, count=count, slave=slave_id)
        elif protocol == "rtu" and self.rtu_client:
            return self.rtu_client.read_input_registers(address=adres, count=count, slave=slave_id)
        return None

    def lees_coil(self, adres, slave_id=1, count=1, protocol="tcp"):
        """Voorbeeld: lees co."""
        if protocol == "tcp" and self.tcp_client:
            return self.tcp_client.read_coils(address=adres, count=count, slave=slave_id)
        elif protocol == "rtu" and self.rtu_client:
            return self.rtu_client.read_coils(address=adres, count=count, slave=slave_id)
        return None

    def lees_discrete_input(self, adres, slave_id=1, count=1, protocol="tcp"):
        """Voorbeeld: lees di."""
        if protocol == "tcp" and self.tcp_client:
            return self.tcp_client.read_discrete_inputs(address=adres, count=count, slave=slave_id)
        elif protocol == "rtu" and self.rtu_client:
            return self.rtu_client.read_discrete_inputs(address=adres, count=count, slave=slave_id)
        return None

    def schrijf_coil(self, adres, waarde, slave_id=1, protocol="tcp"):
        """
        Schrijf naar een coil (of meerdere coils).

        waarde: True / False of een lijst van bools, zoals [True, False, True]
        """
        if isinstance(waarde, list):
            # Schrijf meerdere coils
            if protocol == "tcp" and self.tcp_client:
                return self.tcp_client.write_coils(address=adres, values=waarde, slave=slave_id)
            elif protocol == "rtu" and self.rtu_client:
                return self.rtu_client.write_coils(address=adres, values=waarde, slave=slave_id)
        else:
            # Schrijf één coil
            if protocol == "tcp" and self.tcp_client:
                return self.tcp_client.write_coil(address=adres, value=waarde, slave=slave_id)
            elif protocol == "rtu" and self.rtu_client:
                return self.rtu_client.write_coil(address=adres, value=waarde, slave=slave_id)
        return None
