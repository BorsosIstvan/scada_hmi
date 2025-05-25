from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from pymodbus.datastore.store import ModbusSequentialDataBlock
import threading
import time

# Setup datastore met 100 holding registers (allemaal op 0)
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 100),  # Discrete Inputs
    co=ModbusSequentialDataBlock(0, [0] * 100),  # Coils
    hr=ModbusSequentialDataBlock(0, [0] * 100),  # Holding Registers
    ir=ModbusSequentialDataBlock(0, [0] * 100),  # Input Registers
)
context = ModbusServerContext(slaves=store, single=True)


# Deze functie verhoogt elke seconde register[0]
def update_register():
    value = 0
    while True:
        time.sleep(1)
        value = (value + 1) % 100

        # Holding registers (3)
        context[0].setValues(3, 0, [value, value + 1, value +3])
        # Input registers (4)
        context[0].setValues(4, 0, [value * 2, value * 2 + 1])
        # Coils (1)
        coils = [(value >> i) & 1 for i in range(8)]
        context[0].setValues(1, 0, coils)
        # Discrete Inputs (2)
        context[0].setValues(2, 0, [(value + 1) % 2, value % 2])

        print(f"[MODBUS] HR[0]={value}, IR[0]={value * 2}, CO[0]={value % 2}, CO[1]={coils}, DI[0]={(value + 1) % 2}")
        print(context[0].getValues(1, 0, count=1))


# Start de update-thread
t = threading.Thread(target=update_register, daemon=True)
t.start()

# Start Modbus TCP Server op poort 5020
StartTcpServer(context, address=("localhost", 502))
