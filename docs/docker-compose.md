# Docker Compose: orquestación de servicios

---

## 1. Qué es Docker Compose

Docker Compose permite definir y gestionar múltiples contenedores
en un solo fichero docker-compose.yml. En lugar de arrancar cada
contenedor manualmente con docker run, se levanta toda la
infraestructura con un único comando:

    docker compose up -d

---

## 2. Estructura del docker-compose.yml

    services:
      backend:
        build: .
        container_name: toolkit-backend
        ports:
          - "8000:8000"
        environment:
          - REDIS_HOST=redis
          - REDIS_PORT=6379
          - REDIS_PASSWORD=secretpass
        volumes:
          - toolkit-data:/data
        networks:
          - toolkit-net
        depends_on:
          - redis

      redis:
        image: redis:7-alpine
        container_name: toolkit-redis
        command: redis-server --requirepass secretpass
        expose:
          - "6379"
        volumes:
          - redis-data:/data
        networks:
          - toolkit-net

    volumes:
      toolkit-data:
      redis-data:

    networks:
      toolkit-net:
        driver: bridge

---

## 3. Decisiones de diseño

    build: .
        Construye el backend desde el Dockerfile local.

    depends_on: redis
        El backend espera a que Redis arranque primero.

    expose vs ports
        Redis usa expose: solo accesible internamente.
        Backend usa ports: accesible desde el exterior.

    command: redis-server --requirepass secretpass
        Redis arranca con contraseña obligatoria.

    networks: toolkit-net
        Red bridge personalizada para aislar los servicios.

---

## 4. Resultado del despliegue

    Network docker-toolkit_toolkit-net   Created
    Volume  docker-toolkit_redis-data    Created
    Volume  docker-toolkit_toolkit-data  Created
    Container toolkit-redis              Started
    Container toolkit-backend            Started

    NAME              PORTS
    toolkit-backend   0.0.0.0:8000->8000/tcp  (puerto publicado)
    toolkit-redis     6379/tcp                (solo interno)

---

## 5. Verificación del service discovery

    docker exec -it toolkit-backend sh
    ping redis

    64 bytes from 172.18.0.2: seq=1 ttl=64 time=0.072ms
    1110 packets transmitted, 1110 received, 0% packet loss

Docker resuelve el nombre redis a la IP 172.18.0.2
automáticamente sin configurar ninguna IP manualmente.

---

## 6. Comandos útiles de Docker Compose

    docker compose up -d        levantar toda la infraestructura
    docker compose down         parar y eliminar contenedores y red
    docker compose ps           ver estado de los servicios
    docker compose logs -f      ver logs de todos los servicios
    docker compose restart      reiniciar todos los servicios
    docker compose build        reconstruir las imágenes

