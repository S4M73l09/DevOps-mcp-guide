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

Aqui puedes ver la carpeta que contiene la configuracion basica usada: [terraform-fixtures](fixtures/terraform/basic/)

Y la configuracion usada para alojar sus `tools`: [terraform.py](tools/terraform.py)

## Docker

En esta `fixture` se usa imagenes dentro de un `docker-compose.yaml` en el que se aloja una base de datos utilizando `postgres`, un administrador de base de datos como `Adminer`, registro de metricas con `Prometheus` y visualizacion de metricas avanzadas con `grafana`.

En este ejemplo concreto de `docker` se usa variables de ejemplo `.env.example`. Tambien las imagenes usan versiones reproducibles usando su ***Digest + tag***.

En este ejemplo, se muestra la validacion y consulta en contenedores en su propio `docker.py` para el servidor ***MCP***, como se comento en el ejemplo de Terraform, las herramientas utilizadas para desplegar y/o actualizar el contenedor, debe tener especial cuidado aplicando politicas, arneses, validacion y confirmacion humana.

### Funcionalidades de las tools

Las `tools` creadas para el entorno Docker permiten acceder a los diferentes `compose.yaml` alojados en la ruta objetivo, inspeccionar las imagenes alojadas en los composes y visualizar de manera general el contenedor.

```text
register_docker_tools
├──docker_list_compose_files  -- Le pasas la ruta donde se aloja los diferentes compose, te muestra todos los compose.
├──docker_compose_config      -- Te permite visualizar el compose, cuando le pasas la ruta y el nombre de un compose especifico.
├──docker_compose_images      -- Muestra todas las imagenes alojadas en un compose, le pasas la ruta y el nombre de un compose especifico.
├──docker_image_inspect       -- Permite inspeccionar una imagen concreta de un compose, le pasas el nombre de imagen que da la tool anterior.
└──docker_compose_ps          -- Muestra el estado del contenedor de manera general, le pasas la ruta y el nombre de un compose especifico.
```

Puedes ver aqui la `tool`: [docker.py](tools/docker.py)

## Kubernetes

En la `fixture` de Kubernetes se ha creado un cluster de ejemplo el cual servira para mostrar las diferentes `tools` dentro del servidor ***MCP***

El cluster contiene lo basico para su funcionamiento y despliegue. Tambien contiene version ***Digest + tag*** para asegurar version inmutable. No contiene `secrets`, `Ingress`, `LoadBalancer`, permisos RBAC ni operaciones mutables debido a que depende del usuario y las politicas de seguridad a la hora de tocar infraestructura critica en servicios concretos. Todo ello corre a riesgo propio.

La estructura de este ejemplo utiliza la base para crear tres diferentes overlays.

- `development`  
- `staging`  
- `production`  

Aqui un vistazo de la estructura:

```text
fixtures/kubernetes/
├── base/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── development/
    │   └── kustomization.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── production/
        └── kustomization.yaml
```

La lista que contiene la `tool` es:

1. `kubernetes_current_context`  
    Muestra el contexto Kubernetes activo.

2. `kubernetes_list_namespace` es:
    Lista los namespaces disponibles.

3. `kubernetes_list_pods`
    Lista los pods de un namespace concreto.

4. `kubernetes_list_deployments` es:
    Lista los deployments de un namespace.

5. `kubernetes_list_services` es:
    Lista los servicios de un namespace.

6. `kubernetes_list_services` es:
    Consulta eventos recientes para detectar errores o problemas.

7. `kubernetes_validate_manifest` es:
    Valida un manifiesto YAML o un overlay de Kustomize mediante `--dry-run=client`, sin aplicar cambios.


Aqui puedes ver la `tool` concreta de kubernetes: [kubernetes.py](tools/kubernetes.py)

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
