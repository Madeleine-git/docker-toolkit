# Gestión avanzada y limpieza del entorno

---

## 1. Ciclo de vida con Docker Compose

    docker compose stop      detiene los contenedores, los conserva
    docker compose ps -a     lista incluidos los detenidos (Exited 0)
    docker compose start     arranca los contenedores existentes
                              sin recrearlos, healthchecks se repiten

    Diferencia con down/up:
    down  elimina contenedores y red, hay que recrear todo
    stop/start  conserva contenedores, mas rapido

---

## 2. Reconstruir un solo servicio

    echo "# cambio" >> app/main.py
    docker compose build backend
    docker compose up -d backend

    Resultado:
    - backend reconstruido en 2.4s (cache de dependencias)
    - toolkit-proxy seguia corriendo, 43s sin reiniciar
    - toolkit-redis seguia corriendo, 55s sin reiniciar

    Solo el servicio modificado se reconstruye y recrea.
    Los demas servicios no se ven afectados.

---

## 3. Escalado del servicio backend

Para escalar fue necesario quitar container_name del backend,
ya que Docker requiere nombres unicos por contenedor.

    docker compose up -d --scale backend=3

    Resultado:
    docker-toolkit-backend-1   Up (healthy)
    docker-toolkit-backend-2   Up (healthy)
    docker-toolkit-backend-3   Up (healthy)

    Las 3 replicas healthy. NGINX resuelve "backend" via
    Docker DNS y distribuye peticiones entre las replicas
    (round-robin basico).

    curl -k https://localhost/status
    {"status":"ok",...}   <- sigue respondiendo correctamente

Vuelta a 1 instancia:

    docker compose up -d --scale backend=1

    Las replicas 2 y 3 se eliminaron automaticamente,
    solo quedo backend-1.

---

## 4. Monitorizacion con docker stats

    docker stats --no-stream

    NAME                       CPU%    MEM USAGE   MEM%
    docker-toolkit-backend-1   0.24%   34.02MiB    3.72%
    toolkit-proxy              0.00%   3.066MiB    0.34%
    toolkit-redis              0.48%   5.238MiB    0.57%

    Consumo total: ~42MB de 914MB disponibles (4.6%)

    docker stats muestra en tiempo real CPU, memoria, red
    y I/O de disco por contenedor. --no-stream toma una
    sola lectura en lugar de actualizar continuamente.

---

## 5. Limpieza del sistema

    docker system df    (antes)

    TYPE            TOTAL   SIZE      RECLAIMABLE
    Images          3       996.1MB   0B
    Containers      3       327.7kB   0B
    Local Volumes   3       285B      135B
    Build Cache     12      513.4MB   283.8kB

    docker system prune -f

    Total reclaimed space: 283.8kB
    (4 objetos de cache de build eliminados)

    docker system df    (despues)

    Build Cache     8       513.1MB   0B

Se uso prune sin -a para no eliminar las imagenes en uso
por los 3 servicios activos. Solo se limpio cache de build
obsoleta de versiones anteriores del Dockerfile.

---

## 6. Resumen de comandos de gestion

    docker compose stop / start    pausar/reanudar sin recrear
    docker compose build <serv>    reconstruir un servicio
    docker compose up -d --scale backend=N   escalar replicas
    docker stats --no-stream       uso de recursos puntual
    docker system df               espacio usado por Docker
    docker system prune -f         limpiar recursos no usados
    docker system prune -a -f      limpiar tambien imagenes
                                    no usadas por ningun contenedor

