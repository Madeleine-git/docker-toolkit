# Integración con Redis: caché y almacenamiento

---

## 1. Instalación de la librería cliente

Se añadió redis-py al requirements.txt:

    redis==5.0.1

Se reconstruyó la imagen con --build para instalar la nueva dependencia.

---

## 2. Conexión a Redis desde Python

    import redis
    import os

    def get_redis():
        return redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", ""),
            decode_responses=True
        )

    El hostname es el nombre del servicio en Docker Compose (redis).
    Docker resuelve el nombre a la IP interna automáticamente.
    decode_responses=True devuelve strings en lugar de bytes.

---

## 3. Caché de logs con Redis

    GET /cache/logs

    Primera llamada: procesa y guarda en Redis con TTL de 30 segundos
        r.setex("cache:logs", 30, resultado)
        Respuesta: {"fuente": "procesado", "datos": "..."}

    Segunda llamada (dentro de 30s): devuelve desde Redis
        cached = r.get("cache:logs")
        Respuesta: {"fuente": "cache", "datos": "..."}

    Después de 30 segundos la clave expira automaticamente (nil).

    Verificado con redis-cli:
        GET cache:logs
        (nil)   <- ya habia expirado

---

## 4. IPs sospechosas con SET de Redis

    POST /ips/sospechosas?ip=192.168.1.100   reportar IP
    GET  /ips/sospechosas                    listar IPs

    Redis SET garantiza elementos únicos sin duplicados.

    Prueba realizada:
        POST ip=192.168.1.100  -> {"status":"ok"}
        POST ip=10.0.0.55      -> {"status":"ok"}
        POST ip=192.168.1.100  -> {"status":"ok"} (duplicado)
        GET  ips sospechosas   -> ["192.168.1.100","10.0.0.55"]

    La IP 192.168.1.100 se reportó dos veces pero
    solo aparece una vez en el SET.

    Comandos Redis usados:
        r.sadd("ips:sospechosas", ip)      añadir al SET
        r.smembers("ips:sospechosas")      leer el SET

---

## 5. Verificación con redis-cli

    docker exec -it toolkit-redis redis-cli -a secretpass123

    SMEMBERS ips:sospechosas
    1) "192.168.1.100"
    2) "10.0.0.55"

    GET cache:logs
    (nil)   <- expiró tras 30 segundos (TTL configurado)

