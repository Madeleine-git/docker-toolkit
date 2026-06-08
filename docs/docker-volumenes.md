# Docker: gestión de datos persistentes con volúmenes
---

## 1. El problema: los contenedores son efímeros

Todo lo que se escribe dentro de un contenedor desaparece al eliminarlo.
Para persistir datos se usan volúmenes, que viven fuera del contenedor.

---

## 2. Modificación de la API

Se añadieron dos endpoints al fichero app/main.py:

    POST /log?mensaje=texto   escribe una línea en /data/entradas.log
    GET  /log                 lee y devuelve todas las entradas del fichero

El fichero se guarda en /data/entradas.log dentro del contenedor.
Esa carpeta /data se conecta al volumen externo al arrancar.

---

## 3. Arranque con volumen nombrado

    docker run -d --name toolkit-api -p 8000:8000 -v toolkit-data:/data sys-toolkit:1.0

    -v toolkit-data:/data
        toolkit-data  nombre del volumen gestionado por Docker
        /data         carpeta dentro del contenedor donde se monta

---

## 4. Experimento de persistencia

Paso 1 - Escribir datos en el contenedor original:

    curl -X POST "http://localhost:8000/log?mensaje=primera-entrada"
    curl -X POST "http://localhost:8000/log?mensaje=segunda-entrada"
    curl -X POST "http://localhost:8000/log?mensaje=tercera-entrada"

    Respuesta: {"status":"ok","mensaje":"primera-entrada"}

Paso 2 - Verificar que se guardaron:

    curl http://localhost:8000/log
    Respuesta:
    {
        "entradas": [
            "2026-06-08 14:12:24 - primera-entrada",
            "2026-06-08 14:12:24 - segunda-entrada",
            "2026-06-08 14:12:24 - tercera-entrada"
        ]
    }

Paso 3 - Eliminar el contenedor completamente:

    docker rm -f toolkit-api

Paso 4 - Crear un contenedor nuevo con el mismo volumen:

    docker run -d --name toolkit-api -p 8000:8000 -v toolkit-data:/data sys-toolkit:1.0

Paso 5 - Verificar que los datos siguen ahí:

    curl http://localhost:8000/log
    Resultado: las tres entradas seguían presentes

Paso 6 - Verificar el fichero físico en el host:

    sudo cat /var/lib/docker/volumes/toolkit-data/_data/entradas.log
    2026-06-08 14:12:24.484944 - primera-entrada
    2026-06-08 14:12:24.501028 - segunda-entrada
    2026-06-08 14:12:24.511225 - tercera-entrada

CONCLUSION: los datos sobrevivieron al contenedor porque estaban
guardados en el volumen, no dentro del contenedor. Docker almacena
los volúmenes en /var/lib/docker/volumes/ en el host.

---

## 5. Gestión de volúmenes con la CLI

    docker volume ls              listar todos los volúmenes
    docker volume inspect nombre  ver detalles de un volumen
    docker volume rm nombre       eliminar un volumen
    docker volume prune           eliminar todos los volúmenes no usados

Resultado de docker volume inspect toolkit-data:

    {
        "Name": "toolkit-data",
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/toolkit-data/_data",
        "Scope": "local"
    }

---

## 6. Volumen nombrado vs bind mount

### Volumen nombrado

    docker run -v toolkit-data:/data mi-imagen

    - Docker gestiona dónde se guarda en disco
    - Portable entre sistemas
    - Recomendado para producción
    - Ideal para bases de datos y datos generados por la app

### Bind mount

    docker run -v /home/ubuntu/mi-app:/app mi-imagen

    - Tú decides qué carpeta del host se monta
    - El contenedor ve los cambios del host en tiempo real
    - Ideal para desarrollo: editas el código en tu máquina
      y el contenedor lo ve sin necesidad de rebuild
    - No recomendado en producción por depender de rutas del host

### Tabla comparativa

    Característica        Volumen nombrado     Bind mount
    Gestión               Docker               El usuario
    Portabilidad          Alta                 Baja (depende de rutas)
    Uso recomendado       Producción           Desarrollo
    Visibilidad           docker volume ls     Solo en el host
    Casos de uso          BD, logs, uploads    Código en desarrollo

