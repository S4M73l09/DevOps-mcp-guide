# 06 - Terraform [EN](README.en.md)

## Propósito

Este ejemplo muestra cómo utilizar un servidor MCP para ejecutar comprobaciones seguras sobre una configuración de Terraform.

El servidor expone tools de solo lectura que permiten revisar el formato o validar la configuración sin aplicar cambios sobre la infraestructura.

## Tools incluidas

### `terraform_format_check`

Comprueba si los archivos Terraform cumplen el formato esperado:

```bash
terraform fmt -check -diff -recursive
```

Esta variante utiliza `-check`, por lo que no modifica los archivos.

Si existen diferencias de formato, el resultado incluye el detalle del diff.

### `terraform_validate`

Comprueba si la configuración de Terraform es válida:

```bash
terraform validate
```
Esta operación revisa la sintaxis y la configuración interna de los archivos Terraform, pero no crea ni modifica recursos.


## Configuración Terraform

El directorio `terraform/` contiene una configuración mínima y local:

```hcl
terraform {
    required_version = ">= 1.6.0"
}

variable "service_name" {
    type        = string
    description = "Name of the service."
    default     = "api"
}

output "service_name" {
    value = var.service_name
}
```

Esta configuración no utiliza proveedores cloud ni recursos externos. Su objetivo es proporcionar una base segura para probar las validaciones.


---


## Validacion de rutas

Antes de que se ejecute Terraform, el servidor comprueba que:

* La ruta existe.
* Es un directorio.
* Contiene al menos un archivo `.tf`.
* La ejecución se realiza dentro de la ruta validada.

Una ruta inexistente produce un error controlado y no ejecuta ningún comando.

---

## Seguridad de los comandos

El servidor ejecuta los comandos mediante una lista de argumentos:

```python
[
    "terraform",
    "fmt",
    "-check",
    "-diff",
    "-recursive",
]
```

No se utiliza `shell=True` ni se construyen comandos concatenando texto recibido del usuario.

Además:

* Se establece un tiempo máximo de ejecución.
* No se permite ejecutar comandos arbitrarios.
* No se ejecuta `terraform apply`.
* No se ejecuta `terraform destroy`.
* No se ejecuta `terraform taint`.
* No se modifican archivos Terraform.
* No se cambian workspaces.
* No se accede a proveedores cloud.
* No se utilizan credenciales reales.


## Inicializar la configuración local

Para validar una configuración Terraform, puede ser necesario inicializar el directorio sin utilizar un backend remoto:

```bash
terraform init -backend=false
```

Esta operación prepara el directorio local para las validaciones. No se conecta con un backend remoto ni aplica cambios sobre infraestructura.


## Ejecutar el ejemplo

Desde este directorio:

```bash
uv sync
```

Ejecutar los tests:
```bash
uv run pytest
```

### Probarlo con MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server terraform-devops-mcp
```

En su sección de `Tools` aparecerá:

```text
terraform_format_check
terraform_validate
```
Como una ruta de prueba se puede utilizar:
```text
terraform
```

---

## Ejemplo de respuesta válida
```json
{
    "ok": true,
    "return_code": 0,
    "stdout": "Success! The configuration is valid.\n",
    "stderr": ""
}
```

El contenido exacto de `stdout` puede variar según la versión instalada de Terraform.


## Ejemplo de respuesta con errores

Si la configuración no es válida, la respuesta puede incluir:

```json
{
    "ok": false,
    "return_code": 1,
    "stdout": "",
    "stderr": "Terraform configuration is invalid."
}
```

La tool devuelve el resultado de la comprobación, pero no intenta corregir automáticamente los archivos.

## Que demuestran los tests

Los tests muestran:

* Que una ruta de Terraform válida puede ser aceptada.
* Que una ruta inexistente produce un error.
* Que una ruta sin archivos `.tf` es rechazada.
* Que las comprobaciones se realizan sobre una ruta validada.

Los tests de ejecución de Terraform pueden utilizar mocks para no depender de que Terraform esté instalado en el entorno.

## Diferencia entre validar y aplicar

La validación solo comprueba la configuración:

```bash
terraform validate
```

La aplicación modifica la infraestructura:
```bash
terraform apply
```

Este ejemplo solo utiliza operaciones de inspección y validación. Una configuración válida no significa que esté autorizada para aplicarse ni que deba desplegarse automáticamente.

Antes de ejecutar cualquier operación con impacto habría que comprobar:

* La cuenta activa.
* El proyecto o suscripción.
* El workspace.
* El backend.
* El entorno.
* Los permisos.
* El plan generado.
* La aprobación explícita de la operación.

## Límites del ejemplo

Este servidor no:

* Ejecuta `terraform apply`.
* Ejecuta `terraform destroy`.
* Ejecuta cambios de infraestructura.
* Accede a Kubernetes.
* Accede a GCP o Azure.
* Utiliza credenciales cloud.
* Modifica archivos Terraform.
* Ejecuta comandos arbitrarios.
* Cambia el backend remoto.
* Cambia de workspace automáticamente.

El objetivo es demostrar cómo integrar comprobaciones Terraform de solo lectura dentro de una tool MCP con validación de rutas y límites de seguridad.

---

## Imágenes de ejemplo

#### Imagen que muestra el servidor MCP activado:

![Capture-server-terraform-devops-mcp](Images/Capture-server-terraform-devops-mcp.png)


#### Imagen que muestra las herramientas creadas:

![Capture-terraform-tools](Images/Capture-terraform-tools.png)


#### Imagen que muestra la herramienta `terraform_format_check`:

![Capture-of-terraform-format-check](Images/Capture-of-terraform-format-check.png)


#### Imagen que muestra el resultado esperado al poner la ruta de ***terraform*** en `terraform_format_check`:

![Capture-result-terraform_format_check](Images/Capture-result-terraform_format_check.png)


#### Imagen que muestra la herramienta `terraform_validate`:

![Capture-terraform-validate-tool](Images/Capture-terraform-validate-tool.png)


#### Imagen que muestra el resultado al poner la ruta ***terraform*** en `terraform_validate`:

![Capture-terraform-validate-result](Images/Capture-terraform-validate-result.png)
