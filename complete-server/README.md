# Complete Server

## Proposito

Servidor MCP DevOps completo que servira como referencia practica dentro de esta guia.


## Estructura base

Actualmente la estructura basica de este ejemplo practico muestra una configuracion basica pero suficiente para el uso de un servidor `MCP`.

```text
10-complete-server/
├── tests
    └── test_server.py
├── tools
    ├── __init.py__
    └── diagnostics.py # Archivo para diagnostico sobre la inicializacion del servidor mcp
├── config.py
├── mcp-inspector.json
├── pyproject.toml
├── README.md
└── server.py

```
## Configuracion de prueba (***fixtures***)

Este servidor de ejemplo, usara `fixtures` en las tools DevOps criticas como `Terraform`, `Docker` y `Kubernetes`. Todo ello permite aislar funcionamiento real a funcionamiento para:

- Tests reproducibles.
- Ejemplos del README.
- Validaciones seguras.
- Pruebas sin credenciables ni infraestructura externa.

A su vez para diagnostico de prueba, se usa [`diagnostics.py`](tools/diagnostics.py) para validar el correcto funcionamiento del servidor.

## Comandos usados

Para sincronizar version y estado del servidor:
```bash
uv sync
```

Para iniciar el servidor:
```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
--config mcp-inspector.json \
--server devops-complete-server
```

Para hacer test y verificar errores de sintaxis, falta de version, o cualquier discrepancia:
```bash
uv run pytest
```

Se iran expandiendo los comandos en funcion al contexto necesario durante la construccion de este servidor.
