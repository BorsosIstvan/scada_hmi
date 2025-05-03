import pickle
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
        "communicatie": {
            "type": "Modbus TCP",
            "instellingen": {
                "ip": "127.0.0.1",
                "poort": 502,
                "timeout": 2
            }
        }
    }


def opslaan_project(project_data, pad):
    with open(pad, "wb") as f:
        pickle.dump(project_data, f)


def openen_project(pad):
    with open(pad, "rb") as f:
        return pickle.load(f)
