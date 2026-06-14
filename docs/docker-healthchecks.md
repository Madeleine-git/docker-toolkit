# Healthchecks y dependencias entre servicios

---

## 1. El problema de depends_on sin healthcheck

depends_on por si solo solo controla el orden de arranque del
contenedor, no si el servicio dentro esta listo para recibir
peticiones. Redis puede tardar unos segundos en aceptar conexiones
aunque el contenedor ya este "arrancado". Si el backend intenta
conectar en ese instante, falla.

---

## 2. Healthcheck en Redis

    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s

    test       comando que Docker ejecuta periodicamente
    interval   cada cuanto se comprueba
    timeout    tiempo maximo de espera por respuesta
    retries    fallos consecutivos antes de marcar unhealthy
    start_period  tiempo de gracia antes de empezar a contar fallos

    redis-cli ping responde PONG si Redis esta listo.

---

## 3. Healthcheck en el backend

Primer intento con wget fallo porque python:3.11-alpine
no incluye wget:

    test: ["CMD", "wget", "--spider", "-q", "http://localhost:8000/status"]
    Resultado: unhealthy (wget: not found)

Solucion: usar Python directamente, que si esta disponible
en la imagen:

    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/status')"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

Si la peticion HTTP a /status falla o lanza excepcion,
el comando termina con error y Docker marca el contenedor
como unhealthy.

---

## 4. depends_on con condition: service_healthy

    backend:
      depends_on:
        redis:
          condition: service_healthy

    proxy:
      depends_on:
        backend:
          condition: service_healthy

En lugar de esperar solo a que el contenedor exista, Docker
espera a que el healthcheck del servicio dependiente devuelva
healthy antes de arrancar el siguiente.

---

## 5. Resultado del arranque

    docker compose up -d

    Network docker-toolkit_toolkit-net  Created
    Container toolkit-redis             Healthy    (6.0s)
    Container toolkit-backend           Healthy    (11.6s)
    Container toolkit-proxy             Started    (11.7s)

    docker compose ps

    NAME              STATUS
    toolkit-redis     Up 11 seconds (healthy)
    toolkit-backend   Up 6 seconds (healthy)
    toolkit-proxy     Up Less than a second

Orden secuencial respetado: Redis healthy primero, despues
el backend (que dependia de Redis healthy), despues el proxy
(que dependia del backend healthy).

---

## 6. Por que los healthchecks son criticos en produccion

    1. Deteccion de contenedores colgados
       Un proceso puede seguir corriendo (PID activo) pero
       estar bloqueado o sin responder. Sin healthcheck Docker
       lo ve como "Up" aunque no funcione. Con healthcheck
       se marca como unhealthy y se puede reiniciar.

    2. Orden de arranque correcto
       En arquitecturas con dependencias (backend necesita Redis,
       proxy necesita backend) sin healthcheck el siguiente
       servicio puede arrancar antes de que el anterior este listo
       y fallar en sus primeras peticiones.

    3. Integracion con orquestadores
       Herramientas como Kubernetes o Docker Swarm usan los
       healthchecks para decidir si reiniciar un contenedor,
       si enviarle trafico o si esta listo para recibir peticiones
       durante un despliegue (rolling update).

    4. Balanceo de carga inteligente
       Si hay varias replicas de un servicio, el trafico solo
       se envia a las replicas healthy. Una replica unhealthy
       se retira temporalmente sin afectar al servicio.

    Sin healthchecks, un sistema puede parecer funcionando
    (status Up) mientras en realidad esta caido o degradado,
    lo que retrasa la deteccion de problemas en produccion.

