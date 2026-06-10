# NGINX: configuración como proxy inverso

---

## 1. Tercer servicio en Docker Compose

Se añadió el servicio proxy al docker-compose.yml:

    proxy:
        image: nginx:alpine
        container_name: toolkit-proxy
        ports:
          - "80:80"
          - "443:443"
        volumes:
          - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
          - ./nginx/certs:/etc/nginx/certs:ro
        networks:
          - toolkit-net
        depends_on:
          - backend

El backend dejó de tener ports y ahora usa expose.
Solo NGINX tiene puertos publicados al exterior.

---

## 2. Certificados SSL autofirmados

    openssl req -x509 -nodes -days 365 -newkey rsa:2048
        -keyout nginx/certs/nginx.key
        -out nginx/certs/nginx.crt
        -subj "/C=ES/ST=Extremadura/L=Caceres/O=ASIR/CN=localhost"

    nginx.crt   certificado público
    nginx.key   clave privada

Son autofirmados — válidos para desarrollo local pero
el navegador los marca como no confiables en producción.
En producción se usan certificados de Let's Encrypt.

---

## 3. Configuración nginx.conf

    events {
        worker_connections 1024;
    }

    http {
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

        upstream backend {
            server toolkit-backend:8000;
        }

        server {
            listen 80;
            server_name localhost;
            return 301 https://$host$request_uri;
        }

        server {
            listen 443 ssl;
            server_name localhost;

            ssl_certificate     /etc/nginx/certs/nginx.crt;
            ssl_certificate_key /etc/nginx/certs/nginx.key;

            location /static/ {
                root /usr/share/nginx/html;
                expires 30d;
            }

            location / {
                limit_req zone=api burst=20 nodelay;
                proxy_pass http://backend;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
    }

---

## 4. Explicación de la configuración

    events { worker_connections 1024 }
        Bloque obligatorio. Define cuántas conexiones simultáneas
        puede gestionar cada worker process de NGINX.

    limit_req_zone ... rate=10r/s
        Rate limiting: máximo 10 peticiones por segundo por IP.
        Protege la API de ataques de fuerza bruta.

    upstream backend
        Define el servidor de destino. NGINX redirige el tráfico
        al contenedor toolkit-backend en el puerto 8000.

    return 301 https://
        Redirige todo el tráfico HTTP al HTTPS automáticamente.

    ssl_certificate / ssl_certificate_key
        Rutas a los certificados montados como volumen.

    location /static/
        NGINX sirve ficheros estáticos directamente sin pasar
        por FastAPI. expires 30d activa caché en el navegador.

    proxy_set_header
        Cabeceras que NGINX añade al reenviar la petición:
        X-Real-IP        IP real del cliente original
        X-Forwarded-For  Cadena de proxies por los que pasó
        X-Forwarded-Proto protocolo original (http o https)

---

## 5. Verificación

    curl -k https://localhost/status
    {"status":"ok","service":"SysAdmin Toolkit API","version":"1.0.0"}

    curl -v http://localhost/status
    HTTP/1.1 301 Moved Permanently
    Location: https://localhost/status

    HTTP redirige a HTTPS correctamente.
    HTTPS llega al backend a través de NGINX.

---

## 6. Arquitectura de puertos final

    Internet
        |
    NGINX (80, 443)   unico punto de entrada publico
        |
    FastAPI (8000)    solo interno, no accesible desde fuera
        |
    Redis (6379)      solo interno, no accesible desde fuera

