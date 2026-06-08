from fastapi import FastAPI
import platform
import os

app = FastAPI(
    title="SysAdmin Toolkit API",
    description="API REST para el toolkit de administración de sistemas",
    version="1.0.0"
)

@app.get("/status")
def get_status():
    """Endpoint de estado: comprueba que la API está viva."""
    return {
        "status": "ok",
        "service": "SysAdmin Toolkit API",
        "version": "1.0.0"
    }

@app.get("/inventory")
def get_inventory():
    """Endpoint de inventario: devuelve información del sistema."""
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
