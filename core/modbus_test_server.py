from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from pymodbus.datastore.store import ModbusSequentialDataBlock
import threading
import time

# Setup datastore met 100 holding registers (allemaal op 0)
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 100)
)
context = ModbusServerContext(slaves=store, single=True)


# Deze functie verhoogt elke seconde register[0]
def update_register():
    value = 0
    while True:
        time.sleep(1)
        value = (value + 1) % 65536
        context[0].setValues(3, 0, [value])
        print(f"[MODBUS] Register[0] = {value}")


# Start de update-thread
t = threading.Thread(target=update_register, daemon=True)
t.start()

# Start Modbus TCP Server op poort 5020
StartTcpServer(context, address=("localhost", 502))
