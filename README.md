# docker-toolkit

Infraestructura dockerizada para el SysAdmin Toolkit: API FastAPI,
cache Redis y proxy inverso NGINX con HTTPS, orquestados con
Docker Compose.

Proyecto - Contenedores y proxy inverso con Docker

---

## Arquitectura

    Internet
        |
        v
    NGINX (puerto 80 / 443)
        |  proxy_pass + rate limiting + SSL
        v
    FastAPI Backend (puerto 8000, solo interno)
        |  redis://redis:6379
        v
    Redis (puerto 6379, solo interno)

    Volumenes:
      toolkit-data  -> datos persistentes del backend
      redis-data    -> persistencia de Redis

    Red:
      toolkit-net (bridge) -> aisla los 3 servicios

Solo NGINX tiene puertos publicados al exterior. El backend y
Redis solo son accesibles entre contenedores de la misma red.

---

## Requisitos previos

- Docker Engine 24+
- Docker Compose v2 (incluido en Docker Desktop y en docker-ce)
- OpenSSL (para generar certificados de desarrollo)

---

## Instalacion y despliegue

### 1. Clonar el repositorio

    git clone https://github.com/Madeleine-git/docker-toolkit.git
    cd docker-toolkit

### 2. Configurar variables de entorno

    cp .env.example .env

Edita .env y cambia REDIS_PASSWORD por una contraseña propia.
El fichero .env nunca se sube a git (ver .gitignore).

### 3. Generar certificados SSL de desarrollo

NGINX necesita un certificado SSL para servir HTTPS. Genera uno
autofirmado (valido para desarrollo local, el navegador mostrara
un aviso de "no seguro" porque no esta firmado por una CA oficial):

    mkdir -p nginx/certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout nginx/certs/nginx.key \
      -out nginx/certs/nginx.crt \
      -subj "/C=ES/ST=Extremadura/L=Caceres/O=ASIR/CN=localhost"

En produccion se reemplazaria por un certificado de una CA real
(por ejemplo Let's Encrypt).

### 4. Levantar la infraestructura

    docker compose up -d

Este comando construye la imagen del backend, descarga las
imagenes de Redis y NGINX, crea la red y los volumenes, y arranca
los 3 servicios en orden segun sus healthchecks.

### 5. Verificar

    docker compose ps

    Todos los servicios deberian aparecer como "healthy" o "Up".

    curl -k https://localhost/status
    curl -k http://localhost/status   (redirige automaticamente a https)

---

## Endpoints de la API

Todos accesibles a traves de NGINX en https://localhost/<endpoint>

    GET  /status              Estado de la API y configuracion de Redis
    GET  /inventory           Informacion del sistema (hostname, OS, CPU...)
    POST /log?mensaje=texto   Escribe una entrada en el log persistente
    GET  /log                 Lee todas las entradas del log
    GET  /cache/logs          Endpoint con cache en Redis (TTL 30s)
    POST /ips/sospechosas?ip=x.x.x.x   Reporta una IP sospechosa (SET Redis)
    GET  /ips/sospechosas     Lista las IPs sospechosas reportadas

Documentacion interactiva (Swagger UI):

    https://localhost/docs   (no accesible externamente sin location en nginx.conf)

---

## Comandos utiles

    docker compose up -d           levantar toda la infraestructura
    docker compose down            parar y eliminar contenedores y red
    docker compose stop / start    pausar / reanudar sin recrear
    docker compose ps              ver estado de los servicios
    docker compose logs -f         ver logs en tiempo real
    docker compose build backend   reconstruir solo el backend
    docker compose up -d --scale backend=3   escalar el backend
    docker stats                   uso de recursos en tiempo real
    docker system prune -f         limpiar recursos no usados

---

## Estructura del proyecto

    docker-toolkit/
    ├── app/                    Codigo fuente FastAPI
    │   ├── main.py             Endpoints de la API
    │   └── requirements.txt    Dependencias Python
    ├── docs/                   Documentacion tecnica de cada paso
    ├── nginx/
    │   ├── nginx.conf          Configuracion del proxy inverso
    │   └── certs/              Certificados SSL (generados, no en git)
    ├── Dockerfile              Imagen del backend
    ├── docker-compose.yml      Orquestacion de los 3 servicios
    ├── .env.example            Plantilla de variables de entorno
    ├── .dockerignore
    └── .gitignore

---

## Seguridad

- Secretos gestionados via variables de entorno (.env, no en git)
- Redis con autenticacion por contraseña
- Redis y backend sin puertos publicados al exterior
- HTTPS con redireccion automatica desde HTTP
- Rate limiting en NGINX (10 req/s por IP) contra fuerza bruta
- Healthchecks en todos los servicios criticos
- Imagen base alpine minimalista para reducir superficie de ataque

---

## Documentacion tecnica

La carpeta docs/ contiene la documentacion detallada de cada fase
del proyecto: fundamentos de Docker, redes, volumenes, Docker
Compose, variables de entorno, NGINX como proxy inverso, Redis,
healthchecks y gestion del entorno.

