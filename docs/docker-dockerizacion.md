# Dockerización del toolkit de Python

> Documento técnico — Fase 8: Paso 5
> Módulo ASIR · docker-toolkit

---

## 1. API FastAPI

Se creó el fichero app/main.py con dos endpoints:

    GET /status     devuelve el estado de la API
    GET /inventory  devuelve el inventario del sistema

La API usa FastAPI como framework y uvicorn como servidor ASGI.
Se añadieron al requirements.txt:

    fastapi==0.115.0
    uvicorn==0.30.6

---

## 2. Dockerfile

    FROM python:3.11-alpine

    WORKDIR /app

    COPY app/requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY app/ .

    EXPOSE 8000

    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

Decisiones de diseño:

    python:3.11-alpine  imagen minimalista de 50MB frente a 1GB de python:3.11
    WORKDIR /app        directorio de trabajo limpio dentro del contenedor
    COPY requirements antes que el codigo para aprovechar la cache de Docker
    --no-cache-dir      no guarda cache de pip, reduce el tamaño de la imagen
    --host 0.0.0.0      necesario para que uvicorn acepte conexiones externas

---

## 3. .dockerignore

    venv/           el entorno virtual pesa cientos de MB y no se necesita
                    dentro del contenedor, que instala sus propias dependencias
    __pycache__/    ficheros compilados de Python, se regeneran automaticamente
    *.pyc *.pyo     bytecode de Python, innecesario en produccion
    .git/           historial de git no tiene utilidad dentro del contenedor
    .env            fichero con secretos, nunca debe entrar en una imagen
    docs/           documentacion del proyecto, no necesaria en produccion
    .vscode/        configuracion del editor, no relevante para la app
    logs/           logs generados en ejecucion, no forman parte del codigo
    data/           datos generados, no forman parte del codigo fuente

Sin .dockerignore Docker copiaria todo el contenido del directorio
al contexto de build, incluyendo ficheros sensibles y pesados que
no tienen ninguna utilidad dentro del contenedor.

