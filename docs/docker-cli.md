cat > docs/docker-cli.md << 'ENDOFFILE'
# Docker: comandos esenciales de la CLI

---

## 1. Gestión de imágenes

    # Descargar una imagen sin ejecutarla
    docker pull nginx:alpine

    # Listar imágenes locales
    docker images

    # Resultado:
    # nginx:alpine   8b1e78743a03   93.6MB
    # ubuntu:22.04   4f838adc7181   119MB

    # Inspeccionar detalles de una imagen
    docker inspect nginx:alpine

    # Campos relevantes encontrados:
    # ExposedPorts: 80/tcp
    # Architecture: amd64
    # Cmd: nginx -g daemon off
    # Layers: 8 capas

    # Eliminar una imagen
    docker rmi hello-world:latest

---

## 2. Contenedor NGINX en segundo plano

    docker run -d --name mi-nginx -p 8080:80 nginx:alpine

    # -d          corre en segundo plano (detached)
    # --name      asigna un nombre al contenedor
    # -p 8080:80  mapea puerto 8080 del host al 80 del contenedor

    # Verificación con curl
    curl http://localhost:8080
    # Respuesta: HTML de bienvenida de nginx

    # Verificado también en navegador: http://localhost:8080

---

## 3. Gestión de contenedores

    # Ver contenedores en ejecución
    docker ps

    # Ver todos (incluidos detenidos)
    docker ps -a

    # Detener
    docker stop mi-nginx
    # STATUS pasa a: Exited (0)

    # Arrancar de nuevo
    docker start mi-nginx

    # Reiniciar
    docker restart mi-nginx

    # El contenedor detenido sigue existiendo en docker ps -a
    # a diferencia de los creados con --rm que desaparecen al salir

---

## 4. docker exec y efemeralidad de los contenedores

    # Entrar en un contenedor en ejecución
    docker exec -it mi-nginx sh

    # Dentro del contenedor instalamos vim
    apk add vim
    exit

    # Eliminamos el contenedor y lo recreamos desde la misma imagen
    docker rm -f mi-nginx
    docker run -d --name mi-nginx -p 8080:80 nginx:alpine

    # Entramos de nuevo y comprobamos
    docker exec -it mi-nginx sh
    vim
    # Resultado: sh: vim: not found

    # CONCLUSIÓN: todo lo instalado manualmente dentro de un contenedor
    # desaparece al eliminarlo. El nuevo contenedor arranca desde la
    # imagen original limpia. Por eso nunca se instala nada manualmente
    # en produccion; todo va en el Dockerfile.

---

## 5. Inspección en profundidad

    docker inspect mi-nginx

    # Datos relevantes extraídos del JSON:
    # Status:    running
    # IPAddress: 172.17.0.2  (IP interna en la red bridge de Docker)
    # Ports:     80/tcp -> 0.0.0.0:8080
    # Gateway:   172.17.0.1  (IP del host visto desde Docker)
    # Network:   bridge

    # La IP 172.17.0.2 solo es accesible desde dentro de Docker.
    # El mapeo -p 8080:80 es lo que permite el acceso desde el exterior.

---

## 6. Logs en tiempo real

    docker logs -f mi-nginx

    # El flag -f (follow) muestra los logs en tiempo real.
    # Al hacer curl http://localhost:8080 aparecio:

    # 172.17.0.1 - - [03/Jun/2026:13:47:40] "GET / HTTP/1.1" 200 896
    # 172.17.0.1 - - [03/Jun/2026:13:47:43] "GET /favicon.ico" 404

    # Primera linea: peticion del curl, respuesta 200 OK
    # Segunda linea: el navegador busco el favicon, respuesta 404
    #   porque nginx no tiene ese fichero por defecto

    # Ctrl+C para salir de los logs sin detener el contenedor

ENDOFFILE