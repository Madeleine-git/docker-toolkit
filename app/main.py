from fastapi import FastAPI
import platform
import os
import redis
from datetime import datetime

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

LOG_FILE = "/data/entradas.log"

app = FastAPI(
    title="SysAdmin Toolkit API",
    description="API REST para el toolkit de administración de sistemas",
    version=APP_VERSION
)

def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
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

@app.get("/cache/logs")
def logs_cacheados():
    r = get_redis()
    cache_key = "cache:logs"
    cached = r.get(cache_key)
    if cached:
        return {"fuente": "cache", "datos": cached}
    resultado = f"Logs parseados a las {datetime.now()} en {platform.node()}"
    r.setex(cache_key, 30, resultado)
    return {"fuente": "procesado", "datos": resultado}

@app.post("/ips/sospechosas")
def reportar_ip(ip: str):
    r = get_redis()
    r.sadd("ips:sospechosas", ip)
    return {"status": "ok", "ip_reportada": ip}

@app.get("/ips/sospechosas")
def listar_ips():
    r = get_redis()
    ips = r.smembers("ips:sospechosas")
    return {"ips_sospechosas": list(ips)}
