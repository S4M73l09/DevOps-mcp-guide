# 04 - Validation [EN](README.en.md)

## Proposito

Muestra la validacion en servidores MCP, el cual es de suma importancia para la seguridad de las diferentes herramientas y recursos.

La validacion es especialmente importante para entornos DevOps porque una entrada incorrecta podria provocar una operacion inesperada sobre una infraestructura real.

La herramienta de este ejemplo no realiza despliegues ni modifica recursos externos.
Unicamente comprueba si una petición de despliegue cumple las reglas definidas.

## Que se valida

La herramienta `validate_deployment` recibe los siguientes campos:

| Campo | Tipo | Reglas |
|---|---|---|
| `service` | `string` | Entre 2 y 50 caracteres |
| `environment` | `string` | `development`, `staging` o `production` |
| `replicas` | `integer` | Entre 1 y 10 |


## Ejemplo válido:

```json
{
    "service": "api",
    "environment": "staging",
    "replicas": 2
}
```
Respuesta esperada:

```json
{
    "valid": true,
    "service": "api",
    "environment": "staging",
    "replicas": 2
}
```

## Ejemplos de entradas rechazadas

### Número de réplicas fuera de rango

```json
{
    "service": "api",
    "environment": "staging",
    "replicas": 0
}
```
> El valor minimo permitido es `1`.

### Entorno no permitido

```json
{
    "service": "api",
    "environment": "production-old",
    "replicas": 2
}
```

> Solo se permiten los entornos definidos explicitamente por el esquema.

### Nombre de servicio demasiado corto

```json
{
    "service": "a",
    "environment": "development",
    "replicas": 1
}
```

> El nombre del servicio debe tener al menos dos caracteres.


## Validacion frente a ejecución

Este ejemplo separa dos responsabilidades:

1. Validar que la petición tiene una estructura y unos valores permitidos.  

2. Ejecutar una operacion sobre un sistema externo.

Una petición válida no implica que deba ejecutarse automáticamente. En un servidor DevOps real todavía habria que comprobar:

* La identidad del usuario.  
* Sus permisos sobre el recurso.  
* El entorno seleccionado.  
* El contexto o cuenta activa.  
* Las politica de seguridad.  
* La existencia del servicio.  
* El resultado de un plan o dry-run.  
* La confirmación explícita antes de modificar recursos.  

## Buenas practicas

### Usar listas permitidas

Cuando un campo solo admite ciertos valores, es preferible definir una lista explícita o un tipo enumerado:

```python
Literal["development", "staging", "production"]
```

### Definir límites numéricos

Los valores numéricos deben tener limites razonables:

```python
Field(ge=1, le=10)
```

Esto evita aceptar cantidades negativas, cero o valores desproporcionados.



### Validar antes de usar

la entrada debe validarse antes de:

* Construir comandos.
* Consultar APIs externas.
* Crear manifiestos.
* Acceder a recursos cloud.
* Ejecutar Terraform, Ansible o `kubectl`.
* Cambiar el estado de una infraestructura.

### Rechazar por defecto

Si una entrada no coincide con el esquema, debe rechazarse. No se deben inventar valores, corregir silenciosamente la petición ni asumir el entorno.

### No confiar únicamente en el cliente

Aunque el cliente pueda mostrar un formulario generado a partir del esquema, la validación debe existir tambien en el servidor. Un cliente puede estar mal configurado o enviar una petición manual.

### Mantener la validación separada de la autorizacion

La validación responde a esta pregunta:

> ¿La petición tiene una estructura y unos valores correctos?

La autorizacion responde a otra:

> ¿Esta identidad puede realizar esta operación sobre este recurso?

Ambas comprobaciones son necesarias y no deben confundirse.

---

## Ejecutar el ejemplo

Desde este directorio:

```bash
uv sync
```

Ejecutar los tests:
```bash
uv run pytest
```

## Probarlo con MCP Inspector
```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server validation-devops-mcp
```

En la seccion `tools` aparecerá `validate_deployment`.

Se pueden probar tanto entradas válidas como entradas que incumplan las restricciones del esquema.

---

## Que demuestran los tests

Los tests cubren:

* Una petición válida.
* Un número de réplicas fuera de rango.
* Un entorno no permitido.
* Un nombre de servicio demasiado corto.

Las entradas válidas devuelven una respuesta estructurada. Las entradas inválidas producen una respuesta marcada como error y no continúan hacia ninguna operación externa.

## Limites del ejemplo

Este ejemplo no:

* Despliega aplicaciones.
* Modifica recursos cloud.
* Ejecuta comandos del sistema.
* Consulta Kubernetes.
* Ejecuta Terraform o Ansible.
* Accede a credenciales.
* Realiza cambios irreversibles.

Su objetivo es demostrar cómo construir un limite de validación antes de conectar una tool MCP con sistemas DevOps reales.

---

## Imagenes de ejemplo

#### Captura que muestra informacion del servidor ***Validation***:

![Capture-Validation-mcp-server-info.png](Images/Capture-validation-api-error.png)


#### Captura que muestra validacion usando un entorno permitido:

```json
{
    "service": "api",
    "environment": "staging",
    "replicas": 2
}
```

![Capture-validation-api-image.png](Images/Capture-validation-api-image.png)


#### Captura que muestra el error de api usando una entrada o entorno no permitido, corto o invalido:

```json
{
    "service": "api",
    "environment": "development",
    "replicas": 1
}
```

![Capture-validation-api-error.png](Images/Capture-validation-api-error.png)