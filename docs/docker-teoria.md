# Docker: fundamentos teóricos

> Documento técnico — Fase 8: Contenedores y proxy inverso con Docker  

## 1. Máquina virtual vs contenedor Docker

### Máquina virtual (VM)

Una máquina virtual emula un ordenador completo por software. Sobre el hardware físico corre un **hipervisor** (por ejemplo VirtualBox, VMware o KVM) que abstrae los recursos físicos y permite ejecutar encima uno o varios sistemas operativos completos, cada uno con su propio kernel, sus propios drivers y su propio espacio de usuario.

```
┌──────────────────────────────────────┐
│  App A          App B                │
│  SO completo    SO completo          │
│  (kernel + libs)(kernel + libs)      │
├──────────────────────────────────────┤
│          Hipervisor                  │
├──────────────────────────────────────┤
│          Hardware físico             │
└──────────────────────────────────────┘
```

**Consecuencias prácticas:**
- Cada VM ocupa varios GB (el SO invitado completo).
- El arranque tarda minutos (boot completo del SO).
- El aislamiento es total: cada VM tiene su propio kernel.

### Contenedor Docker

Un contenedor **no emula hardware ni arranca un SO completo**. En cambio, usa características del kernel Linux del host (`namespaces` y `cgroups`) para crear un entorno aislado dentro del mismo sistema operativo.

```
┌──────────────────────────────────────┐
│  App A          App B                │
│  libs propias   libs propias         │
├──────────────────────────────────────┤
│          Docker Engine               │
├──────────────────────────────────────┤
│     Kernel Linux del host            │
├──────────────────────────────────────┤
│          Hardware físico             │
└──────────────────────────────────────┘
```

**Consecuencias prácticas:**
- Un contenedor ocupa solo lo que necesita la app (decenas de MB).
- El arranque es en segundos (no hay boot, solo inicia el proceso).
- El aislamiento es a nivel de proceso, no de kernel.

### Tabla comparativa

| Característica       | Máquina virtual         | Contenedor Docker          |
|----------------------|-------------------------|----------------------------|
| SO propio            | Sí (kernel completo)    | No (comparte el del host)  |
| Tamaño típico        | 2–20 GB                 | 50–500 MB                  |
| Tiempo de arranque   | 1–5 minutos             | 1–5 segundos               |
| Aislamiento          | Total (hypervisor)      | Proceso (namespaces)       |
| Portabilidad         | Limitada (imagen pesada)| Alta (imagen ligera)       |
| Rendimiento          | Overhead significativo  | Casi nativo                |

---

## 2. Qué comparte el contenedor con el host y qué aísla

### Comparte con el host

- **Kernel del sistema operativo**: todos los contenedores usan el mismo kernel Linux del host. Por eso Docker en Windows y macOS necesita una VM ligera con Linux (Docker Desktop la gestiona de forma transparente).
- **Hardware físico**: CPU, memoria RAM y disco se comparten; Docker Engine los asigna según los límites configurados.
- **Red del host** (opcionalmente): si se usa el modo `--network host`, el contenedor comparte la interfaz de red del host directamente.

### Aísla del host y de otros contenedores

Docker usa dos mecanismos del kernel para el aislamiento:

**`namespaces`** — crean vistas privadas de los recursos del sistema:

| Namespace  | Qué aísla                                      |
|------------|------------------------------------------------|
| `pid`      | Árbol de procesos (el contenedor ve solo los suyos) |
| `net`      | Interfaces de red, tablas de rutas, puertos    |
| `mnt`      | Sistema de ficheros (punto de montaje propio)  |
| `uts`      | Nombre del host (hostname independiente)       |
| `ipc`      | Comunicación entre procesos                    |
| `user`     | Mapeo de UIDs (root dentro ≠ root fuera)       |

**`cgroups`** (control groups) — limitan el consumo de recursos:
- CPU: máximo de núcleos o porcentaje.
- RAM: límite de memoria; si se supera, el proceso se mata.
- I/O de disco: límite de lectura/escritura.
- Red: límite de ancho de banda.

---

## 3. Conceptos clave

### Imagen

Una imagen Docker es una **plantilla inmutable** que contiene el sistema de ficheros con todo lo necesario para ejecutar una aplicación: código, intérprete, librerías y configuración. Las imágenes se construyen en capas apiladas (ver sección siguiente) y no cambian una vez creadas.

Analogía: la imagen es el **molde** o la **receta**; a partir de ella se instancian los contenedores.

### Contenedor

Un contenedor es una **instancia en ejecución** de una imagen. Es un proceso (o grupo de procesos) que corre en el host de forma aislada usando namespaces y cgroups. Se puede arrancar, pausar, detener y eliminar. Varios contenedores pueden derivar de la misma imagen.

Analogía: si la imagen es la receta, el contenedor es el **plato ya cocinado y servido**.

### Dockerfile

Un `Dockerfile` es un **fichero de texto con instrucciones** que Docker sigue para construir una imagen. Cada instrucción genera una capa nueva en la imagen.

Ejemplo mínimo para una app Python:

```dockerfile
# Capa base: imagen oficial de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias e instalarlas (capa separada para aprovechar caché)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Comando que se ejecuta al arrancar el contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Hub

Docker Hub es el **registro público oficial** de imágenes Docker, accesible en [hub.docker.com](https://hub.docker.com). Funciona como un repositorio (similar a GitHub pero para imágenes). Desde él se descargan las imágenes base (`python:3.11`, `nginx:alpine`, `redis:7`, etc.) y se pueden publicar imágenes propias.

Otros registros: GitHub Container Registry (ghcr.io), AWS ECR, Google Artifact Registry.

### Capa (layer)

Cada instrucción de un `Dockerfile` que modifica el sistema de ficheros (`RUN`, `COPY`, `ADD`) crea una **capa inmutable**. Las capas se apilan y Docker las gestiona con un sistema de ficheros de unión (`overlay2`).

**Ventajas del sistema de capas:**
- **Caché**: si una capa no ha cambiado, Docker la reutiliza en la siguiente build. Por eso se ponen las dependencias antes que el código fuente.
- **Compartición**: si dos imágenes usan la misma capa base (`python:3.11`), esa capa se almacena una sola vez en disco.
- **Eficiencia de red**: al hacer `docker push` o `docker pull` solo se transfieren las capas que han cambiado.

```
┌─────────────────────────────┐  ← capa 4: CMD (metadato, no modifica FS)
├─────────────────────────────┤  ← capa 3: COPY . .  (código fuente)
├─────────────────────────────┤  ← capa 2: RUN pip install  (librerías)
├─────────────────────────────┤  ← capa 1: FROM python:3.11-slim (SO base)
└─────────────────────────────┘
         Imagen final
```

### Registro (registry)

Un registro es un **servidor que almacena y distribuye imágenes Docker**. Docker Hub es el registro por defecto, pero cualquier organización puede desplegar su propio registro privado (`docker run registry:2`). El flujo habitual es:

```
docker build  →  imagen local
docker push   →  imagen en el registro
docker pull   →  imagen descargada desde el registro
docker run    →  contenedor en ejecución
```

---

## 4. Ciclo de vida de un contenedor

Un contenedor pasa por los siguientes estados a lo largo de su vida:

```
            docker create
  [IMAGEN] ─────────────────► [CREADO]
                                  │
                          docker start
                                  │
                                  ▼
                            [EN EJECUCIÓN] ◄──── docker unpause
                            /     |     \              │
               docker pause/      │      \docker stop  │
                          /       │       \             │
                    [PAUSADO]     │     [DETENIDO] ──── docker pause
                                  │       │
                          docker kill     │ docker start
                                  │       │
                                  ▼       │
                            [ELIMINADO] ◄─┘
                           docker rm
```

### Descripción de cada estado

| Estado          | Descripción                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| **Creado**      | El contenedor existe (se ha reservado su configuración y sistema de ficheros) pero el proceso principal aún no ha arrancado. |
| **En ejecución**| El proceso principal (`CMD` o `ENTRYPOINT`) está corriendo. El contenedor consume CPU y memoria. |
| **Pausado**     | Los procesos están suspendidos mediante `SIGSTOP`. El contenedor sigue en memoria pero no consume CPU. |
| **Detenido**    | El proceso principal ha terminado (por sí solo o por `docker stop`). El contenedor sigue existiendo en disco pero no consume recursos. |
| **Eliminado**   | El contenedor ha sido borrado con `docker rm`. Ya no existe. |

### ¿Qué ocurre con los datos cuando un contenedor se elimina?

> **Respuesta corta: los datos se pierden**, a menos que se usen volúmenes.

Cuando Docker crea un contenedor, añade sobre las capas inmutables de la imagen una **capa de escritura** (writable layer) que es exclusiva de ese contenedor. Todo lo que el proceso escribe en el sistema de ficheros (logs, ficheros temporales, datos de base de datos) va a esa capa.

Al ejecutar `docker rm`, esa capa de escritura **se destruye permanentemente**.

Para persistir datos existen tres mecanismos:

| Mecanismo       | Descripción                                                    | Uso típico               |
|-----------------|----------------------------------------------------------------|--------------------------|
| **Volumen**     | Directorio gestionado por Docker en el host (`/var/lib/docker/volumes/`). Sobrevive al contenedor. | Bases de datos, uploads  |
| **Bind mount**  | Monta un directorio del host dentro del contenedor.            | Desarrollo (hot reload)  |
| **tmpfs mount** | Solo en memoria RAM, nunca toca disco.                         | Datos sensibles temporales|

---

## 5. Diagrama: relación entre kernel del host, Docker Engine y los contenedores

```
┌─────────────────────────────────────────────────────────────────┐
│                        HARDWARE FÍSICO                          │
│                 (CPU · RAM · Disco · Red)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    KERNEL LINUX DEL HOST                        │
│                                                                 │
│   namespaces (pid, net, mnt, uts, ipc, user)                   │
│   cgroups    (límites de CPU, RAM, I/O)                         │
│   overlay2   (sistema de ficheros en capas)                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      DOCKER ENGINE                              │
│                                                                 │
│   dockerd   ←──── API REST ────►   docker CLI / Compose        │
│   containerd (gestiona el ciclo de vida)                        │
│   runc       (crea y ejecuta contenedores usando kernel API)    │
└──────────┬────────────────┬────────────────┬────────────────────┘
           │                │                │
┌──────────▼────┐  ┌────────▼──────┐  ┌──────▼──────────┐
│ Contenedor 1  │  │ Contenedor 2  │  │  Contenedor 3   │
│               │  │               │  │                 │
│  nginx:alpine │  │  python:3.11  │  │   redis:7       │
│  proceso:     │  │  proceso:     │  │  proceso:       │
│  nginx -g ... │  │  uvicorn ...  │  │  redis-server   │
│               │  │               │  │                 │
│  net: bridge  │  │  net: bridge  │  │  net: bridge    │
│  pid ns propio│  │  pid ns propio│  │  pid ns propio  │
└───────────────┘  └───────────────┘  └─────────────────┘
        │                  │                   │
        └──────────────────┴───────────────────┘
                           │
                    Red virtual Docker
                  (docker network: bridge)
```

### Explicación del diagrama

**Hardware físico**: la capa más baja; proporciona los recursos reales.

**Kernel Linux del host**: es el único kernel del sistema. Todos los contenedores lo comparten. Ofrece `namespaces` para aislar visibilidad y `cgroups` para limitar recursos.

**Docker Engine**: es el demonio (`dockerd`) que escucha peticiones (vía CLI o API REST) y las traduce en llamadas al kernel. Internamente usa `containerd` como gestor de ciclo de vida y `runc` como motor de ejecución de contenedores (el que realmente invoca los syscalls del kernel).

**Contenedores**: cada uno corre como un proceso aislado. Desde dentro, el contenedor cree que es el único proceso en la máquina — ve su propio árbol de PIDs, su propia interfaz de red, su propio sistema de ficheros. Pero desde el host, son simplemente procesos con restricciones.

**Red virtual Docker**: por defecto Docker crea una red bridge (`docker0`) que interconecta los contenedores entre sí. Los contenedores se comunican por nombre de servicio (`redis`, `fastapi`, `nginx`) sin necesidad de conocer IPs.

---
