# Variables de entorno y archivos de entorno

---

## 1. El problema: secretos en texto plano

En el paso anterior el docker-compose.yml tenía esto:

    command: redis-server --requirepass secretpass
    environment:
      - REDIS_PASSWORD=secretpass

Cualquiera que vea el repositorio en GitHub puede leer
la contraseña. Esto es un grave error de seguridad.

---

## 2. Fichero .env

Contiene los valores reales de las variables sensibles.
Vive solo en el servidor, nunca se sube a GitHub.
Está incluido en .gitignore.

    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_PASSWORD=secretpass123
    APP_VERSION=1.0.0

---

## 3. Fichero .env.example

Plantilla pública que sí se sube a GitHub.
Muestra qué variables hay que configurar sin revelar valores.

    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_PASSWORD=tu_contraseña_aqui
    APP_VERSION=1.0.0

Cuando alguien clona el repositorio copia este fichero,
lo renombra a .env y pone sus propios valores.

---

## 4. Docker Compose con variables

En lugar de valores hardcodeados se usan referencias:

    environment:
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
      - REDIS_PASSWORD=${REDIS_PASSWORD}

    command: redis-server --requirepass ${REDIS_PASSWORD}

Docker Compose lee automáticamente el fichero .env del
mismo directorio y sustituye las variables al arrancar.

---

## 5. Código Python leyendo variables de entorno

    import os

    REDIS_HOST     = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT     = os.getenv("REDIS_PORT", "6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    APP_VERSION    = os.getenv("APP_VERSION", "1.0.0")

os.getenv("VARIABLE", "valor_por_defecto") lee la variable
del entorno. Si no existe usa el valor por defecto.
Nunca se hardcodea ningún secreto en el código.

---

## 6. Por qué nunca incluir secretos en Dockerfile o Compose

    1. El repositorio es público o puede llegar a serlo.
       Una contraseña subida a GitHub es una contraseña
       comprometida, aunque se borre después — git guarda
       el historial completo.

    2. Las imágenes Docker se comparten. Si construyes una
       imagen con un secreto dentro y la subes a Docker Hub,
       cualquiera puede extraer ese secreto con docker inspect.

    3. Los logs de CI/CD pueden exponer variables.
       Si el valor está hardcodeado aparecerá en los logs
       de construcción visibles para todo el equipo.

    4. Rotación de credenciales. Si necesitas cambiar una
       contraseña con variables de entorno solo cambias el
       .env y reinicias. Con valores hardcodeados tienes que
       modificar el código, hacer commit y redesplegar.

    Regla: todo lo que cambia entre entornos (dev, staging,
    produccion) o es sensible (contraseñas, tokens, claves API)
    va en variables de entorno, nunca en el código.

