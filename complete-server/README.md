# Complete Server

## Proposito

Servidor MCP DevOps completo que servira como referencia practica dentro de esta guia.


## Estructura base

Actualmente la estructura basica de este ejemplo practico muestra una configuracion basica pero suficiente para el uso de un servidor `MCP`.

```text
10-complete-server/
├── fixtures
    ├── terraform
        └── basic               # Estructura basica de Terraform
    ├── docker
        └── compose             # Estructura donde esta las imagenes de docker
    ├── kubernetes
        ├── base                # Estructura del cluster base
        └── overlays            # Entornos separados para el cluster basico
            ├── development
            ├── production
            └── staging

├── security
    ├── __init__.py
    ├── receipt.py
    └── signing.py
├── tests
    ├── test_server.py
    ├── test_security.py
    └── test_tool_receipt.py 

├── tools
    ├── __init.py__
    ├── diagnostics.py          # Archivo para diagnostico sobre la inicializacion del servidor mcp
    ├── docker.py
    ├── kubernetes.py
    ├── receipt_support.py
    └── terraform.py
├── config.py
├── mcp-inspector.json
├── pyproject.toml
├── README.md
├── server.py
└── uv.lock                     # Generado por comandos de uv run pytest

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

## Signed receipts en las tools DevOps

El servidor puede generar un `signed receipt` como evidencia verificable de determinadas operaciones.

Un receipt no ejecuta acciones ni autoriza cambios. Su función es demostrar que una tool recibió una entrada concreta y produjo una salida concreta.

El flujo es:

```text
entrada de la tool
     |
validación
     |
ejecución de la operación
     |
resultado
     |
hash de entrada y salida
     |
firma digital opcional
     |
signed receipt
```

### ¿Por qué no se firma todo?

No todas las tools necesitan generar una evidencia firmada.

Las consultas sencillas, como listar pods o namespaces, normalmente solo necesitan un audit log convencional. Los receips se reservan para operaciones cuyo resultado sea especialmente importante o deba verificarse posteriormente.

En este servidor de ejemplo, pueden ser útiles para:

* `terraform_plan`;
* `docker_compose_images`;
* `docker_image_inspect`;
* `kubernetes_validate_manifest`;
* futuras operaciones de despliegue o promoción.

Actualmente los receipts firmados están disponibles en:

- `terraform_plan`;
- `docker_compose_images`;
- `kubernetes_validate_manifest`.

Estas tools aceptan:

```json
{
    "include_receipt": true,
    "actor": "local-user"
}
```

Actualmente no sustituyen:

- autorización;
- confirmación humana;
- comprobación del estado real;
- controles de acceso;
- audit logs convencionales.

Las tools de consulta como `kubernetes_list_pods`, `kubernetes_list_services` y `kubernetes_list_events`todavía utilizan respuestas normales y no generan receipts.

### Activar un receipt

Las tools compatibles incluyen el parámetro:

```json
{
    "include_receipt": true
}
```

Cuando el parámetro es `false`, la tool devuelve únicamente su resultado normal. Cuando es `true`, añade un objeto `receipt` firmado.


Ejemplo conceptual:
```json
{
  "tool": "docker_compose_images",
  "ok": true,
  "status": "images_found",
  "count": 4,
  "receipt": {
    "action": "docker_compose_images",
    "actor": "local-user",
    "environment": "development",
    "target": "fixtures/docker/compose/Db-Observ-compose.yaml",
    "input_hash": "...",
    "output_hash": "...",
    "key_id": "...",
    "signature": "..."
  }
}
```

### ¿Qué contiene el receipt?

El receipt incluye:

* la operación ejecutada;
* el actor asociado;
* el entorno;
* el recurso o ruta objetivo;
* un hash de la entrada;
* un hash de la salida;
* el identificador público de la clave;
* la firma digital;

La clave privada nunca se incluye en la respuesta.

### Proveedores de firma

El servidor de ejemplo actual utiliza tres modos:

| Modos | Clave | Uso |
|---|---|---
|`ephemeral` | Memoria | Pruebas rápidas |
| `local` | Archivo local protegido | Desarrollo e Inspector |
| `production` | KMS, HSM o gestor de secretos | Entornos reales |

El `signing_provider` se crea una sola vez al iniciar el servidor y se comparte con las tools que pueden generar receipts. Esto evita crear claves diferentes para cada operación.

La clave privada nunca se incluye en el receipt ni en la respuesta de la tool.

### Qué demuestra y qué no demuestra

Un receipt válido demuestra que:

* una entrada concreta fue procesada;
* se produjo una salida concreta;
* el contenido firmado no fue alterado;
* el servidor utilizó una clave concreta.

Sin embargo, no demuestra por sí solo que un recurso externo haya sido modificado correctamente. Para eso seguirían siendo necesarias la validación, la autorización, la confirmación humana y la comprobación posterior del estado real.

Los receipts complementan los controles de seguridad existentes; no los sustituyen.


Cuando `include_receipt` es `false`, devuelven su respuesta normal. Cuando es `true`, añaden un objeto `receipt` firmado.


Puedes ver los archivos añadidos de seguridad en este enlace: [seguridad](security/); [receipt_support.py](tools/receipt_support.py); [test_security.py](tests/test_security.py) y tambien puedes ver el archivo general de configuracion del servidor para ver la incorporacion de seguridad, [server.py - receipt](server.py).

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
