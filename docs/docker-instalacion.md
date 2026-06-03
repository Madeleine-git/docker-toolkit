cat > docs/docker-instalacion.md << 'ENDOFFILE'
# Docker: instalación y primer contacto

## 1. Instalación en Ubuntu (EC2)

Se usó el script oficial de Docker Inc:

    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh

El script detecta el sistema operativo, añade el repositorio oficial de Docker
y instala: docker-ce, docker-ce-cli, containerd.io, docker-compose-plugin y docker-buildx-plugin.

## 2. Añadir usuario al grupo docker

Para usar Docker sin sudo en cada comando:

    sudo usermod -aG docker ubuntu
    newgrp docker

Sin este paso, cada comando Docker requeriría sudo. Al añadir el usuario
al grupo docker, el sistema operativo le concede permiso para comunicarse
con el socket de Docker (/var/run/docker.sock).

## 3. Verificación: docker version

    Client: Docker Engine - Community
     Version:           29.5.2
     API version:       1.54
     Go version:        go1.26.3
     OS/Arch:           linux/amd64

    Server: Docker Engine - Community
     Engine Version:    29.5.2
     containerd:        v2.2.4
     runc:              v1.3.5

## 4. Verificación: docker info

    Containers: 0
      Running: 0
      Paused: 0
      Stopped: 0
    Images: 0
    Storage Driver: overlayfs
    Cgroup Driver: systemd
    Cgroup Version: 2
    Kernel Version: 6.8.0-1055-aws
    Operating System: Ubuntu 22.04.5 LTS
    CPUs: 2
    Total Memory: 914MiB
    Docker Root Dir: /var/lib/docker

## 5. Primer contenedor: hello-world

    docker run --rm hello-world

Docker realizó los siguientes pasos internamente:

1. Buscó la imagen hello-world localmente — no la encontró.
2. La descargó automáticamente desde Docker Hub (library/hello-world).
3. Creó un contenedor con esa imagen.
4. El contenedor ejecutó su proceso, imprimió el mensaje y terminó.
5. Al usar --rm, el contenedor se eliminó automáticamente al terminar.

Salida obtenida:

    Hello from Docker!
    This message shows that your installation appears to be working correctly.

## 6. Contenedor interactivo efímero

    docker run --rm -it ubuntu:22.04 bash

Flags utilizados:
- --rm   elimina el contenedor automáticamente al salir
- -i     mantiene stdin abierto (interactivo)
- -t     asigna una pseudoterminal (TTY)

Dentro del contenedor se comprobó el aislamiento con namespaces:

    whoami    → root
              El contenedor corre como root dentro de su namespace de usuario.

    hostname  → 99f471386174
              Hostname propio generado por Docker, distinto al del host real.

    ps aux    → solo 2 procesos:
                PID 1  bash
                PID 13 ps aux
              El host real tiene decenas de procesos corriendo, pero el
              namespace pid los oculta completamente al contenedor.

Al ejecutar exit y comprobar con docker ps -a la lista estaba vacía:
el contenedor se eliminó automáticamente gracias al flag --rm.

## Conclusión

El aislamiento de namespaces funciona correctamente: el contenedor
ve solo sus propios procesos, tiene su propio hostname y su propio
sistema de ficheros, aunque comparte el kernel Linux del host.
Los datos escritos dentro del contenedor desaparecen al eliminarlo
porque no se usó ningún volumen.
ENDOFFILE