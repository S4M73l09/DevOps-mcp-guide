# 07 - Docker [EN](README.en.md)

## Propósito

Este ejemplo muestra cómo utilizar un servidor MCP para consultar información
de Docker mediante tools de solo lectura.

## Tools incluidas

### `docker_list_containers`

Ejecuta:

```bash
docker ps --all
```

Permite consultar los contenedores activos y detenidos.

### `docker_list_images`

Ejecuta:

```bash
docker image ls
```

Permite consultar las imágenes disponibles localmente.

### `docker_inspect_container`

Ejecuta:

```bash
docker inspect <container>
```

Recibe como entrada el nombre o identificador del contenedor y devuelve
información detallada sin modificarlo.

## Operaciones excluidas

Este ejemplo no ejecuta:

```text
docker run
docker stop
docker start
docker restart
docker rm
docker rmi
docker exec
docker build
docker push
docker system prune
```

Estas operaciones pueden crear, modificar, detener, ejecutar o eliminar
recursos.

---

## Seguridad

Los comandos se ejecutan mediante listas de argumentos y no utilizan
`shell=True`.

El servidor:

* No ejecuta comandos arbitrarios.
* No modifica contenedores.
* No elimina imágenes.
* No inicia ni detiene servicios.
* No accede a Docker mediante sockets remotos.
* Establece un tiempo máximo de ejecución.
* Rechaza nombres de contenedor vacíos.

## Ejecutar el ejemplo

```bash
uv sync
uv run pytest
```

## Probarlo con MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server docker-devops-mcp
```

En la sección `Tools` aparecerán:

```text
docker_list_containers
docker_list_images
docker_inspect_container
```

## Nota sobre los tests

Los tests utilizan mocks para no depender de Docker durante su ejecución.

Para utilizar las tools realmente, Docker debe estar instalado y el usuario
debe tener permisos para consultar el daemon local.

## Límites del ejemplo

Este servidor solo consulta información local de Docker. No administra
contenedores ni imágenes y no realiza cambios sobre el entorno.

## Images

Imagen mostrando el servidor activo:

![Capture-server-mcp-07-docker.png](Images/capture-server-mcp-07-docker.png)


Imagen mostrando las `Tools` del servidor ***mcp***:

![Capture-mcp-docker-tools](Images/Capture-mcp-docker-tools.png)


Imagen mostrando la `tool` del `list-containers`:

![Capture-docker-inspect-containers-list](Images/Capture-docker-list-containers.png)


Imagen mostrando el resultado de la `tool` anterior:

![Capture-docker-inspect-container-result](Images/Capture-docker-list-containers-result.png)


Imagen mostrando la `tool` de `list-images`:

![Capture-devops-list-images](Images/Capture-devops-list-images.png)


Imagen mostrando el resultado de la `tool` anterior:

![Capture-Devops-list-images-result](Images/Capture-Devops-list-images-result.png)


Imagen mostrando la `tool` de `docker_inspect_container`:

![Capture-docker-inspect-container](Images/Capture-docker-inspect-container.png)


Imagen mostrando un error, cuando no se encuentra ningun contenedor, este error es didactico:

![Capture-docker-inspect-container-error-result](Images/Capture-docker-inspect-container-error-result.png)




