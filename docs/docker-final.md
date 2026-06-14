# Documentacion tecnica y entregable final

---

## 1. Correccion final: nginx.conf con nombre de servicio

Al escalar el backend en el paso 15 se elimino el container_name
fijo (toolkit-backend). Docker Compose asigna entonces nombres
como docker-toolkit-backend-1.

El nginx.conf seguia apuntando al nombre antiguo:

    upstream backend {
        server toolkit-backend:8000;   <- ya no existe
    }

Error al arrancar:

    nginx: [emerg] host not found in upstream "toolkit-backend:8000"

Correccion: usar el nombre del SERVICIO de Compose (backend),
no el container_name. Docker Compose resuelve automaticamente
el nombre del servicio a la IP de la replica activa:

    upstream backend {
        server backend:8000;
    }

Leccion: en Docker Compose el service discovery funciona por
nombre de servicio del docker-compose.yml, independientemente
del container_name que se le asigne al contenedor.

---

## 2. README profesional

Se creo README.md con:
    - Diagrama de arquitectura de los 3 servicios
    - Requisitos previos
    - Pasos de instalacion (clonar, configurar .env, generar
      certificados SSL, levantar con docker compose up -d)
    - Tabla de endpoints de la API
    - Comandos utiles de gestion
    - Estructura del proyecto
    - Resumen de medidas de seguridad
    - Indice de la documentacion tecnica

---

## 3. Gestion de certificados SSL

Los certificados (nginx/certs/*.key, *.crt) NO se suben a git
(estan en .gitignore). Se documenta en el README el comando
openssl para generarlos como parte del setup inicial:

    mkdir -p nginx/certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048
        -keyout nginx/certs/nginx.key
        -out nginx/certs/nginx.crt
        -subj "/C=ES/ST=Extremadura/L=Caceres/O=ASIR/CN=localhost"

Razon: igual que las contraseñas, las claves privadas no deben
subirse a un repositorio, ni siquiera siendo autofirmadas para
desarrollo. Cada despliegue genera sus propios certificados.

---

## 4. Verificacion del entregable

Requisito: la infraestructura debe arrancar y ser accesible en
el puerto 80 con un solo comando.

    docker compose down
    docker compose up -d

    Network docker-toolkit_toolkit-net   Created
    Container toolkit-redis              Healthy   (6.0s)
    Container docker-toolkit-backend-1   Healthy   (11.6s)
    Container toolkit-proxy              Started   (11.8s)

    docker compose ps

    NAME                       STATUS
    docker-toolkit-backend-1   Up (healthy)
    toolkit-proxy              Up
    toolkit-redis              Up (healthy)

    curl -k https://localhost/status
    {"status":"ok","service":"SysAdmin Toolkit API","version":"1.0.0",
     "redis_host":"redis","redis_port":6379}

Entregable verificado: un solo comando levanta toda la
infraestructura (Compose v2, 3 servicios, red bridge, volumenes,
healthchecks) y queda accesible via NGINX con HTTPS.

---

## 5. Resumen del proyecto completo

    Paso 1-4    Fundamentos teoricos Docker (contenedores, capas,
                Dockerfile, imagenes base)
    Paso 5-6    Dockerizacion del toolkit con FastAPI
    Paso 7-8    Redes y volumenes Docker
    Paso 9-10   Docker Compose y variables de entorno
    Paso 11-12  NGINX como proxy inverso con HTTPS y rate limiting
    Paso 13     Integracion con Redis (cache + SET)
    Paso 14     Healthchecks y dependencias
    Paso 15     Gestion avanzada (escalado, stats, limpieza)
    Paso 16     Documentacion final y entregable

Infraestructura final: 3 servicios (backend, redis, proxy),
1 red bridge personalizada, 2 volumenes nombrados, healthchecks
en todos los servicios criticos, secretos via variables de
entorno, HTTPS con redireccion automatica y rate limiting.

