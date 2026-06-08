# Docker: fundamentos teóricos de redes
---

## 1. Tipos de red nativos de Docker

Docker tiene tres tipos de red nativos. Cada uno sirve para una
situación diferente.

### Bridge (por defecto)

Es el modo de red por defecto cuando arrancas un contenedor sin
especificar nada. Docker crea una red privada virtual (docker0)
y conecta los contenedores a ella.

    Características:
    - Los contenedores de la misma red bridge se ven entre sí
    - Están aislados del exterior por defecto
    - Para acceder desde fuera hay que publicar puertos con -p
    - Cada contenedor tiene su propia IP interna (172.17.0.x)

    Cuándo usarlo:
    - Es el modo recomendado para la mayoría de aplicaciones
    - Cuando quieres que varios contenedores se comuniquen
      entre sí de forma controlada
    - En Docker Compose se crea automáticamente una red bridge
      personalizada para cada proyecto

    Ejemplo:
    docker run -d --name mi-app -p 8000:8000 mi-imagen

### Host

Elimina el aislamiento de red del contenedor. El contenedor
comparte directamente la interfaz de red del host, como si
el proceso corriera directamente en la máquina sin Docker.

    Características:
    - El contenedor usa la IP y los puertos del host directamente
    - No hay traducción de puertos (no se usa -p)
    - Mejor rendimiento de red al eliminar la capa de traducción
    - Menos aislamiento y por tanto menos seguridad

    Cuándo usarlo:
    - Aplicaciones que necesitan máximo rendimiento de red
    - Herramientas de monitorización que necesitan ver
      el tráfico de red del host directamente
    - Solo en Linux (en macOS y Windows no funciona igual)

    Ejemplo:
    docker run -d --network host mi-imagen

### None

Desconecta el contenedor de cualquier red. Solo tiene la
interfaz de loopback (localhost interno).

    Características:
    - Sin acceso a red exterior
    - Sin comunicación con otros contenedores
    - Máximo aislamiento de red posible

    Cuándo usarlo:
    - Tareas de procesamiento que no necesitan red
      (procesar ficheros, calcular datos, etc.)
    - Entornos de máxima seguridad donde el aislamiento
      total es un requisito

    Ejemplo:
    docker run -d --network none mi-imagen

### Tabla comparativa

    Tipo    Acceso exterior   Comunicación entre contenedores   Uso típico
    bridge  Solo con -p       Sí, en la misma red               Aplicaciones web
    host    Directo           Sí, vía localhost del host        Alto rendimiento
    none    No                No                                Procesamiento aislado

---

## 2. Service discovery en Docker Compose

Cuando usas Docker Compose, todos los servicios definidos en el
docker-compose.yml se conectan automáticamente a una red bridge
personalizada. Docker actúa como servidor DNS interno y asigna
a cada servicio un nombre de host igual al nombre del servicio.

    Ejemplo: si defines estos servicios en docker-compose.yml:

    services:
      backend:
        build: .
      redis:
        image: redis:7

    El contenedor backend puede conectarse a Redis usando
    simplemente el hostname redis:

        redis://redis:6379

    Docker resuelve internamente que redis apunta a la IP
    del contenedor Redis, igual que un DNS normal resuelve
    google.com a una IP.

    Ventajas del service discovery:
    - No hay que conocer ni hardcodear IPs (que cambian cada
      vez que se recrea un contenedor)
    - La configuración es legible: redis:6379 es más claro
      que 172.18.0.3:6379
    - Si se recrea un contenedor con nueva IP, el nombre
      sigue funcionando automáticamente

---

## 3. Puerto publicado vs puerto expuesto internamente

Esta es una de las diferencias de seguridad más importantes en Docker.

### Puerto publicado (-p)

    docker run -p 8000:8000 mi-imagen

    Mapea un puerto del host al contenedor. Es accesible desde
    cualquier lugar: internet, otros contenedores, el propio host.

    Riesgo: si publicas un puerto de una base de datos, cualquiera
    en internet podría intentar conectarse a ella.

### Puerto expuesto internamente (EXPOSE)

    EXPOSE 6379  (en el Dockerfile)

    Solo documenta que el contenedor usa ese puerto. Es accesible
    únicamente desde otros contenedores en la misma red Docker,
    nunca desde el exterior.

### Regla de seguridad en producción

    Servicio       Puerto publicado   Puerto solo interno
    NGINX          80, 443            -
    FastAPI        -                  8000
    Redis          -                  6379
    PostgreSQL     -                  5432

    Solo NGINX debe tener puertos publicados al exterior.
    El resto de servicios solo deben ser accesibles internamente
    entre contenedores. Así si un atacante accede al puerto 80,
    no puede llegar directamente a Redis o a la base de datos.

    En Docker Compose esto se controla con:

    services:
      proxy:
        ports:
          - "80:80"      # publicado al exterior
      backend:
        expose:
          - "8000"       # solo interno, no accesible desde fuera
      redis:
        expose:
          - "6379"       # solo interno, no accesible desde fuera

