# Docker: comandos esenciales de la CLI
---

## 1. Gestión de imágenes

    docker pull nginx:alpine
    docker images
    docker inspect nginx:alpine
    docker rmi hello-world:latest

    Campos relevantes de inspect:
    - ExposedPorts: 80/tcp
    - Architecture: amd64
    - Cmd: nginx -g daemon off
    - Layers: 8 capas

---

## 2. Contenedor NGINX en segundo plano

    docker run -d --name mi-nginx -p 8080:80 nginx:alpine

    -d          corre en segundo plano
    --name      asigna nombre al contenedor
    -p 8080:80  puerto 8080 del host al 80 del contenedor

    Verificado con curl http://localhost:8080
    Verificado en navegador http://localhost:8080

---

## 3. Gestión de contenedores

    docker ps              ver contenedores en ejecucion
    docker ps -a           ver todos incluidos detenidos
    docker stop mi-nginx   detener, STATUS pasa a Exited (0)
    docker start mi-nginx  arrancar de nuevo
    docker restart mi-nginx reiniciar
    docker rm mi-nginx     eliminar

---

## 4. docker exec y efemeralidad

    docker exec -it mi-nginx sh
    apk add vim
    exit

    docker rm -f mi-nginx
    docker run -d --name mi-nginx -p 8080:80 nginx:alpine
    docker exec -it mi-nginx sh
    vim
    Resultado: sh: vim: not found

    CONCLUSION: todo lo instalado manualmente desaparece al eliminar
    el contenedor. El nuevo arranca desde la imagen original limpia.
    En produccion todo va en el Dockerfile, nunca se instala manualmente.

---

## 5. Inspeccion en profundidad

    docker inspect mi-nginx

    Datos relevantes:
    - Status:    running
    - IPAddress: 172.17.0.2
    - Gateway:   172.17.0.1
    - Ports:     80/tcp -> 0.0.0.0:8080
    - Network:   bridge

    JSON completo relevante:

    {
        "State": {
            "Status": "running",
            "Running": true,
            "Pid": 7334
        },
        "HostConfig": {
            "PortBindings": {
                "80/tcp": [{ "HostPort": "8080" }]
            }
        },
        "Config": {
            "Hostname": "14f14dbc9e1f",
            "ExposedPorts": { "80/tcp": {} },
            "Cmd": ["nginx", "-g", "daemon off;"],
            "Image": "nginx:alpine"
        },
        "NetworkSettings": {
            "Networks": {
                "bridge": {
                    "Gateway": "172.17.0.1",
                    "IPAddress": "172.17.0.2",
                    "MacAddress": "36:69:9c:f4:b1:fb"
                }
            }
        }
    }

---

## 6. Logs en tiempo real

    docker logs -f mi-nginx

    Peticiones registradas en tiempo real:
    172.17.0.1 - [03/Jun/2026] "GET / HTTP/1.1" 200
    172.17.0.1 - [03/Jun/2026] "GET /favicon.ico" 404

    200: respuesta correcta al curl
    404: el navegador busco el favicon, no existe en nginx por defecto
    Ctrl+C para salir sin detener el contenedor

