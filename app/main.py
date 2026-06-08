cat > ~/docker-toolkit/app/main.py << 'ENDOFFILE'
from fastapi import FastAPI
from inventory_manager import InventoryManager

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
    """Endpoint de inventario: devuelve el inventario del sistema."""
    manager = InventoryManager()
    inventory = manager.get_inventory()
    return {
        "status": "ok",
        "inventory": inventory
    }
ENDOFFILE