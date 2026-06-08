# Build, ejecución e inspección de la imagen

---

## 1. Construcción de la imagen

    docker build -t sys-toolkit:1.0 .

Primera build: 69 segundos
Las 5 capas se ejecutaron secuencialmente:
    [1/5] FROM python:3.11-alpine   descarga imagen base
    [2/5] WORKDIR /app              crea directorio de trabajo
    [3/5] COPY requirements.txt     copia dependencias
    [4/5] RUN pip install           instala dependencias (34s)
    [5/5] COPY app/                 copia el código fuente

---

## 2. Comportamiento de la caché

Se modificó app/main.py y se volvió a construir:

    Segunda build: 1.4 segundos

    CACHED [2/5] WORKDIR /app
    CACHED [3/5] COPY requirements.txt
    CACHED [4/5] RUN pip install      <- 34 segundos ahorrados
    [5/5] COPY app/                   <- única capa rehecha

El orden correcto en el Dockerfile (dependencias antes que código)
permitió reutilizar la caché y reducir el build de 69s a 1.4s.

---

## 3. Ejecución y prueba de endpoints

    docker run -d --name toolkit-api -p 8000:8000 sys-toolkit:1.0

Swagger UI accesible en: http://localhost:8000/docs

GET /status — respuesta:
    {
        "status": "ok",
        "service": "SysAdmin Toolkit API",
        "version": "1.0.0"
    }

GET /inventory — respuesta:
    {
        "status": "ok",
        "inventory": {
            "hostname": "100ff62ed6eb",
            "os": "Linux",
            "os_version": "6.8.0-1055-aws",
            "architecture": "x86_64",
            "python_version": "3.11.15",
            "cpu_count": 2
        }
    }

El hostname devuelto es el ID del contenedor, no el de la EC2.
Esto demuestra el aislamiento de namespaces (uts).

---

## 4. Tamaño de la imagen

    docker images sys-toolkit:1.0

    IMAGE             DISK USAGE   CONTENT SIZE
    sys-toolkit:1.0   500MB        109MB

El tamaño real es 500MB. El mayor consumidor es pip install (328MB)
debido a las dependencias pesadas del toolkit (pandas, openpyxl, faker).

Técnicas de optimización para reducir el tamaño:
    1. Usar requirements mínimo solo con fastapi y uvicorn
    2. Usar multi-stage build: compilar en una imagen y copiar
       solo el resultado a una imagen limpia
    3. Usar python:3.11-slim en lugar de alpine si hay problemas
       de compatibilidad con librerías C
    4. Combinar comandos RUN con && para reducir capas
    5. Eliminar cachés y ficheros temporales en el mismo RUN

---

## 5. Análisis de capas con docker history

    docker history sys-toolkit:1.0

    CAPA                          TAMAÑO
    CMD uvicorn...                0B      (solo metadato)
    EXPOSE 8000                   0B      (solo metadato)
    COPY app/                     119kB   (código fuente)
    RUN pip install               328MB   (dependencias)
    COPY requirements.txt         12.3kB
    WORKDIR /app                  8.19kB
    python:3.11-alpine base       ~63MB   (SO + Python)

El código fuente ocupa solo 119KB. El 95% del peso de la imagen
son las dependencias Python instaladas con pip.

