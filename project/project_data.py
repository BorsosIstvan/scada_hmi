import pickle
import json
from datetime import datetime


def nieuw_project(naam="Naamloos project"):
    nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "metadata": {
            "naam": naam,
            "gemaakt_op": nu,
            "laatst_bewerkt": nu,
            "versie": "1.0"
        },
        "canvas": {
            "grootte": [800, 600],
            "achtergrond_kleur": "#FFFFFF",
            "raster": True,
            "raster_grootte": 20
        },
        "objecten": [],
        "variabelen": [],
        "communicatie": {
            "Modbus TCP": {
                "actief": True,
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
    }


def opslaan_project(project_data, pad):
    with open(pad, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=4)


def openen_project(pad):
    with open(pad, "r", encoding="utf-8") as f:
        return json.load(f)
