# 01 - Minimal Server [EN](README.en.md)

## Proposito

Crear lo minimo indispensable para hacer posible el funcionamiento del servidor MCP usando SDK oficial de Python.

Este ejemplo no expone herramientas, recursos o prompts aun. Su proposito es entender el ciclo de vida de un servidor, el transporte `stdio`, y la conexion con MCP Inspector.

## Requerimientos

- Python 3.10 o superior.
- `uv`.
- Node.js 22.19.0 o superior para MCP Inspector.

## Instalacion de dependendicas

Desde este mismo directorio:

```bash
uv sync
```

---

## Ejecutar el server con MCP Inspector
```bash
uv run mcp dev server.py
```

Inspector iniciara el servidor como un subproceso local y se conectara a traves del transporte `stdio`.

El servidor no expone un puerto HTTP en este ejemplo.

## Ejecuta el server directamente

```bash
uv run python server.py
```

El proceso espera un cliente MCP para comunicarse a traves de `stdin` y `stdout`.

## Que demuestra este ejemplo

* Creacion de `MCPServer`.
* Dandole nombre a un servidor.
* Ejecutar el server con `stdio`.
* Proteccion al entry point con `if __name__ == "__main__":`.
* Probando el servidor en memoria.

## Siguiente ejemplo

Este ejemplo no lo hace:

* Ejecutar comandos de shell.
* Accede a Docker.
* Accede a Kubernetes.
* Accede a Terraform.
* Leer archivos.
* Modificar sistemas externos.
* Utiliza credenciales o secretos.
* Exponer un Endpoint HTTP.

#### [`pyproject.toml`](pyproject.toml)

<details>

  Este archivo es la configuracion MCP.

</details>

#### [`server.py`](server.py)

<details>

  Codigo Python usado para operaciones de servidores.

</details>

#### [`test_server.py`](tests/test_server.py)

<details>

  Archivo Test para el servidor

</details>

#### [`uv.lock`](uv.lock)

<details>

  Archivo Lock, importante que fija versiones exactas de las dependencias y permite el entorno correctamente.

</details>

#### [`mcp-inspector.json`](mcp-inspector.json)

<details>
  
  Archivo .json que indica la version usada para el MCP-Inspector.

</details>

---

## Modos de configuracion de Inspector

MCP Inspector soporta dos modos de configuracion

- `--config`: Carga un archivo de configuracion en modo read-only. Los cambios ocasionados en la interfaz no se guardan.
- `--catalog`: Carga un archivo de escritura, los cambios hechos en la interfaz persisten y son escritos en dicho archivo.

Para una configuracion de un proyecto reproducible:

```bash
npx @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server minimal-devops-mcp
```

## Fijar versiones

La etiqueta del paquete sed para el inspector MCP es importante.

Evita confiar ciegamente en `latest`, porque las etiquetas pueden apuntar a diferentes líneas de lanzamiento a lo largo del tiempo. Es posible que las versiones anteriores no admitan el protocolo MCP actual o contengan errores conocidos y vulnerabilidades de seguridad.

En este ejemplo, utilice la versión de Inspector probada `2.0.0`.

Al actualizar la versión:

- Revisar las releases notes.
- Revisar el protocolo de compatibilidad.
- Revisar los avisos de seguridad.
- Ejecutar test de seguridad.
- Actualizar la documentacion y el lock file si es necesario.

Para un catálogo de Inspector editable localmente:

```bash
npx @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server mcp-inspector.json
```

La configuración del Inspector afecta la forma en que se inicia e inspecciona el servidor.
No modifica el código fuente del servidor MCP.

Tambien conviene fijar las dependencia Python del ejemplo de forma coherente:

```toml
dependecies = [
    "mcp[cli]==2.0.0",
]
```
En el archivo `pyproject.tml`.

