cat > docs/docker-imagenes-capas.md << 'ENDOFFILE'
# Docker: imágenes por capas y el Dockerfile

---

## 1. Sistema de capas

Cada imagen Docker se construye como una pila de capas inmutables.
Cada instruccion del Dockerfile que modifica el sistema de ficheros
(RUN, COPY, ADD) genera una capa nueva. Las capas se apilan y Docker
las gestiona con un sistema de ficheros de union llamado overlay2.

    Imagen final
    ┌─────────────────────────┐
    │ capa 4: COPY . .        │  ← código fuente
    ├─────────────────────────┤
    │ capa 3: RUN pip install │  ← dependencias instaladas
    ├─────────────────────────┤
    │ capa 2: COPY req.txt .  │  ← fichero de dependencias
    ├─────────────────────────┤
    │ capa 1: FROM python:3.11│  ← sistema base
    └─────────────────────────┘

Cada capa tiene un hash único. Si una capa no ha cambiado, Docker
la reutiliza desde la caché en el siguiente build. Esto se llama
cache hit y hace los builds mucho más rápidos.

### Por qué el orden de las instrucciones afecta el rendimiento

Docker procesa el Dockerfile de arriba a abajo. Cuando detecta un
cambio en una capa, invalida esa capa y todas las que vienen después.
Las capas anteriores al cambio se reutilizan desde la caché.

MAL orden (lento):
    COPY . .                     ← si cambias cualquier fichero...
    RUN pip install -r req.txt   ← ...pip se reinstala desde cero

BUEN orden (rápido):
    COPY requirements.txt .      ← solo cambia si tocas requirements.txt
    RUN pip install -r req.txt   ← se cachea mientras no cambien las deps
    COPY . .                     ← el código cambia frecuentemente

Con el buen orden, cuando solo modificas codigo Python Docker reutiliza
las capas 1, 2 y 3 desde la caché y solo reconstruye la capa 4.
El build pasa de tardar minutos a tardar segundos.

---

## 2. Instrucciones del Dockerfile

### FROM
Define la imagen base sobre la que se construye todo lo demás.
Siempre es la primera instrucción del Dockerfile.

    FROM python:3.11-alpine

### WORKDIR
Establece el directorio de trabajo dentro del contenedor. Todos los
comandos siguientes (COPY, RUN, CMD) se ejecutan desde ese directorio.
Si no existe lo crea automáticamente.

    WORKDIR /app

### COPY
Copia ficheros o directorios del host al sistema de ficheros del contenedor.
Es la instrucción recomendada para copiar ficheros locales.

    COPY requirements.txt .
    COPY . .

### ADD
Similar a COPY pero con capacidades extra: puede descomprimir ficheros
.tar.gz automáticamente y descargar ficheros desde URLs. Por su
comportamiento menos predecible se prefiere COPY para casos simples.

    ADD archivo.tar.gz /app/

### RUN
Ejecuta un comando durante el build de la imagen. Cada RUN crea una
capa nueva. Se usa para instalar dependencias, compilar código, etc.

    RUN pip install --no-cache-dir -r requirements.txt

### ENV
Define variables de entorno disponibles durante el build y en tiempo
de ejecución del contenedor.

    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1

### EXPOSE
Documenta qué puerto escucha el contenedor. Es solo informativo,
no abre el puerto realmente. Para publicarlo hay que usar -p en docker run.

    EXPOSE 8000

### CMD
Define el comando por defecto que se ejecuta al arrancar el contenedor.
Puede ser sobreescrito pasando un comando al final de docker run.

    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

### ENTRYPOINT
Define el ejecutable principal del contenedor. A diferencia de CMD,
no se sobreescribe fácilmente. Los argumentos de docker run se añaden
al final del ENTRYPOINT.

    ENTRYPOINT ["uvicorn", "main:app"]

### ARG
Define variables disponibles solo durante el build, no en ejecución.
Se usan para pasar valores variables al construir la imagen.

    ARG VERSION=1.0
    RUN echo "Versión: $VERSION"

---

## 3. Diferencia entre CMD y ENTRYPOINT

Es una de las diferencias más importantes del Dockerfile.

    ENTRYPOINT define el ejecutable fijo del contenedor.
    CMD define los argumentos por defecto, reemplazables.

Ejemplo con solo CMD:
    CMD ["uvicorn", "main:app", "--port", "8000"]

    docker run mi-imagen                    ejecuta uvicorn main:app --port 8000
    docker run mi-imagen bash               ejecuta bash (reemplaza CMD completo)

Ejemplo con ENTRYPOINT + CMD:
    ENTRYPOINT ["uvicorn", "main:app"]
    CMD ["--port", "8000"]

    docker run mi-imagen                    ejecuta uvicorn main:app --port 8000
    docker run mi-imagen --port 9000        ejecuta uvicorn main:app --port 9000
    (solo se reemplazan los argumentos, no el ejecutable)

Resumen:
    CMD solo      → comando completo reemplazable
    ENTRYPOINT    → ejecutable fijo, no reemplazable fácilmente
    ENTRYPOINT+CMD → ejecutable fijo con argumentos por defecto modificables

En aplicaciones web de produccion se suele usar ENTRYPOINT para el
servidor y CMD para los argumentos por defecto.

---

## 4. Imagen base Alpine

Alpine Linux es una distribución Linux minimalista diseñada para
contenedores. Su imagen base ocupa solo 5 MB frente a los 120 MB
de ubuntu o los 130 MB de debian.

### Comparativa de tamaños

    python:3.11           →  1.0 GB  (debian completo + Python)
    python:3.11-slim      →  150 MB  (debian mínimo + Python)
    python:3.11-alpine    →   50 MB  (alpine + Python)
    alpine                →    5 MB  (solo el SO base)

### Por qué se prefiere Alpine en producción

Menos superficie de ataque: al tener menos paquetes instalados hay
menos vulnerabilidades potenciales. Un contenedor con ubuntu tiene
cientos de paquetes; alpine tiene solo los imprescindibles.

Builds más rápidos: imágenes más pequeñas se descargan y suben
al registro más rápido. En pipelines de CI/CD esto importa mucho.

Menor coste de almacenamiento: en registros como AWS ECR o Docker Hub
el almacenamiento tiene coste. Imágenes pequeñas reducen ese coste.

### Gestor de paquetes de Alpine

Alpine usa apk en lugar de apt (Ubuntu) o yum (RedHat):

    apk add curl        instalar un paquete
    apk del curl        eliminar un paquete
    apk update          actualizar índice de paquetes

### Consideraciones

Alpine usa musl libc en lugar de glibc. Algunas librerías Python
que dependen de extensiones C pueden tener problemas de compatibilidad
con alpine. En esos casos se usa python:3.11-slim como alternativa.

---

ENDOFFILE