from fastapi import FastAPI
import platform
import os
from datetime import datetime

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

LOG_FILE = "/data/entradas.log"

app = FastAPI(
    title="SysAdmin Toolkit API",
    description="API REST para el toolkit de administración de sistemas",
    version=APP_VERSION
)

@app.get("/status")
def get_status():
    return {
        "status": "ok",
        "service": "SysAdmin Toolkit API",
        "version": APP_VERSION,
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT
    }

@app.get("/inventory")
def get_inventory():
    return {
        "status": "ok",
        "inventory": {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_version": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count()
        }
    }

@app.post("/log")
def escribir_log(mensaje: str):
    os.makedirs("/data", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {mensaje}\n")
    return {"status": "ok", "mensaje": mensaje}

@app.get("/log")
def leer_log():
    if not os.path.exists(LOG_FILE):
        return {"entradas": []}
    with open(LOG_FILE, "r") as f:
        lineas = f.readlines()
    return {"entradas": lineas}
