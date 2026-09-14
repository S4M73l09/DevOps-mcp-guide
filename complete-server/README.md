# Complete Server

## Proposito

Servidor MCP DevOps completo que servira como referencia practica dentro de esta guia.


## Estructura base

Actualmente la estructura basica de este ejemplo practico muestra una configuracion basica pero suficiente para el uso de un servidor `MCP`.

```text
10-complete-server/
├── fixtures
    └── terraform
        └── basic  # Estructura basica de Terraform
├── tests
    └── test_server.py
├── tools
    ├── __init.py__
    └── diagnostics.py # Archivo para diagnostico sobre la inicializacion del servidor mcp
├── config.py
├── mcp-inspector.json
├── pyproject.toml
├── README.md
├── server.py
└── uv.lock # Generado por comandos de uv run pytest

```
## Configuracion de prueba (***fixtures***)

Este servidor de ejemplo, usara `fixtures` en las tools DevOps criticas como `Terraform`, `Docker` y `Kubernetes`. Todo ello permite aislar funcionamiento real a funcionamiento para:

- Tests reproducibles.
- Ejemplos del README.
- Validaciones seguras.
- Pruebas sin credenciables ni infraestructura externa.

A su vez para diagnostico de prueba, se usa [`diagnostics.py`](tools/diagnostics.py) para validar el correcto funcionamiento del servidor.


# Fixtures

Para mostrar como funciona el servidor, se usa el sistema de `fixtures` anteriormente explicado, este bloque usara dicho sistema para los ejemplos en las herramientas Cloud actualmente disponibles en esta guia, se extendera en el futuro.

## Basic Terraform Fixture

Esta `fixture` es usada por el servidor completo MCP para demostrar formato, validacion y plan en entornos donde se usa `IaC` como `Terraform`.

Este ejemplo usa `terraform_data`, lo que significa que no requiere de credenciales cloud de providers ni externos.

### Comandos usados.

Desde el mismo directorio donde se encuentra:

```bash
terraform fmt -check
terraform init -backend=false
terraform validate
terraform plan -var-file=terraform.tfvars.example
```

Esta `fixture` solo tiene `read-only` para validacion y planificacion.

No se usa `terraform apply` ni `terraform destroy` para el ejemplo actual, debido a seguridad en los despliegues.

Se puede agregar para desplegar cambios, pero forma parte de tu propio riesgo, asegurate de agregar politicas, aplicar seguridad, añadir guardarailes a los modelos agenticos, generar logs periodicos y agregar para mayor reproducibilidad certificados firmados.



---

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
