# NGINX: fundamentos teóricos de proxy inverso

> Documento técnico — Fase 8: Paso 11
> Módulo ASIR · docker-toolkit

---

## 1. Proxy directo vs proxy inverso

### Proxy directo

Se coloca delante del cliente. El cliente envía sus peticiones
al proxy y este las reenvía al servidor en nombre del cliente.
El servidor no sabe quién es el cliente real.

    Cliente → Proxy directo → Internet → Servidor

    Casos de uso:
    - Control de acceso a internet en empresas
    - Anonimizar el tráfico del cliente
    - Filtrar contenido no permitido

### Proxy inverso

Se coloca delante del servidor. Los clientes de internet envían
sus peticiones al proxy inverso y este las redirige al servidor
correcto internamente. El cliente no sabe qué servidor real
está respondiendo.

    Internet → Proxy inverso (NGINX) → Servidor interno (FastAPI)

    Casos de uso:
    - Proteger servidores internos del acceso directo
    - Distribuir carga entre varios servidores
    - Gestionar SSL en un punto centralizado
    - Servir contenido estático sin llegar al servidor

### Tabla comparativa

    Característica    Proxy directo         Proxy inverso
    Posición          Delante del cliente   Delante del servidor
    Oculta            La identidad cliente  La identidad servidor
    Usado por         El cliente            La empresa/servicio
    Ejemplo           VPN corporativa       NGINX en producción

### Analogía

    Proxy directo  → recepcionista que gestiona las llamadas
                     que tú haces al exterior
    Proxy inverso  → recepcionista de una empresa que recibe
                     todas las llamadas entrantes y las transfiere
                     al departamento correcto

---

## 2. Por qué NGINX se coloca delante de una aplicación

FastAPI con uvicorn es excelente procesando lógica Python pero
no está diseñado para gestionar miles de conexiones simultáneas,
servir ficheros estáticos eficientemente ni protegerse de ataques.
NGINX resuelve todo esto.

### Gestión SSL (HTTPS)

NGINX centraliza la terminación SSL. El certificado SSL se
configura una sola vez en NGINX y este descifra el tráfico
antes de pasarlo al backend. FastAPI recibe tráfico HTTP
simple internamente sin gestionar cifrado.

    Cliente → HTTPS → NGINX (descifra) → HTTP → FastAPI

    Ventaja: el backend no necesita gestionar certificados.
    Si cambia el certificado solo se cambia en NGINX.

### Rate limiting

NGINX puede limitar el número de peticiones por segundo
que acepta de una misma IP. Protege la API de:
    - Ataques de fuerza bruta
    - Bots que hacen scraping masivo
    - Ataques DDoS simples

    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

### Caché

NGINX puede cachear las respuestas del backend. Si 1000
usuarios piden el mismo recurso, NGINX responde con la
copia en caché sin llegar a FastAPI. Reduce la carga
del servidor drásticamente.

### Ficheros estáticos

NGINX sirve imágenes, CSS, JS y HTML directamente desde
disco sin pasar por Python. Es mucho más eficiente que
dejar que FastAPI sirva ficheros estáticos.

### Balanceo de carga

Si hay varios contenedores backend corriendo, NGINX
distribuye las peticiones entre ellos automáticamente.

    upstream backend {
        server backend1:8000;
        server backend2:8000;
        server backend3:8000;
    }

### Resumen de ventajas

    Ventaja              Sin NGINX         Con NGINX
    SSL                  En cada backend   Centralizado
    Rate limiting        No                Sí
    Ficheros estáticos   Python los sirve  NGINX los sirve
    Balanceo de carga    No                Sí
    Protección ataques   Limitada          Alta

---

## 3. Conceptos clave de configuración NGINX

### Upstream

Define el servidor o grupo de servidores de destino
a los que NGINX redirige el tráfico.

    upstream backend {
        server toolkit-backend:8000;
    }

    El nombre backend se usa después en el proxy_pass.
    Si hay varios servidores NGINX balancea entre ellos.

### Server block

Define cómo NGINX atiende las peticiones entrantes:
qué puerto escucha, qué dominio gestiona y qué hace
con cada petición.

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://backend;
        }
    }

    listen 80        puerto donde NGINX escucha
    server_name      dominio que gestiona este bloque
    location /       regla para peticiones a esa ruta
    proxy_pass       hacia dónde redirige la petición

### Relación entre upstream y server block

    upstream backend {
        server toolkit-backend:8000;   define el destino
    }

    server {
        listen 80;
        location / {
            proxy_pass http://backend;  usa el upstream
        }
    }

    El server block recibe la petición y el upstream
    define a quién se la pasa.

---

## 4. NGINX vs Apache bajo grandes cargas

### Modelo de Apache

Apache crea un proceso o hilo nuevo por cada conexión
entrante. Con 10000 conexiones simultáneas necesita
10000 procesos o hilos, cada uno consumiendo memoria.

    Conexión 1  → Proceso 1  (10MB RAM)
    Conexión 2  → Proceso 2  (10MB RAM)
    Conexión N  → Proceso N  (10MB RAM)
    Total: N x 10MB RAM

    Problema: con mucho tráfico el servidor se queda
    sin memoria y empieza a fallar.

### Modelo de NGINX

NGINX usa un modelo asíncrono y no bloqueante. Un solo
proceso worker gestiona miles de conexiones simultáneas
usando el sistema de eventos del kernel (epoll en Linux).

    1 worker process → 10000 conexiones simultáneas

    El proceso no espera a que una conexión termine
    para atender la siguiente. Gestiona todas a la vez
    de forma asíncrona.

### Comparativa de rendimiento

    Métrica              Apache          NGINX
    Modelo               1 hilo/conexión Asíncrono/eventos
    RAM con 1000 conex.  ~500MB          ~50MB
    Ficheros estáticos   Lento           Muy rápido
    Conexiones máx.      Miles           Decenas de miles
    Configuración        Más sencilla    Más eficiente

### Conclusión

NGINX fue diseñado específicamente para resolver el
problema de las 10000 conexiones simultáneas (C10K problem).
Para cargas altas y ficheros estáticos NGINX es
significativamente más eficiente que Apache.
Apache sigue siendo más sencillo de configurar y tiene
más módulos disponibles, por lo que sigue usándose
en entornos de baja-media carga.

