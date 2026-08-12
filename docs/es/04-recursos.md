# 04 - Recursos [EN](../en/04-resources.md)

## Proposito

Explicar como usar recursos para exponer informacion consultable desde un servidor MCP.

## Indice

- [Vision general](#vision-general)
- [Que es un recurso](#que-es-un-recurso)
- [Como funciona un recurso](#como-funciona-un-recurso)
   - [Descubrimiento](#descubrimiento)
   - [Lectura](#lectura)
   - [Contenido y metadatos](#contenido-y-metadatos)
- [Recursos vs herramientas](#recurso-vs-herramienta)
- [URIs de recursos](#uris-de-recursos)
  - [Recursos estaticos](#recursos-estaticos)
  - [Plantillas de recursos](#plantillas-de-recursos)
- [Tipos de informacion](#tipos-de-informacion)
  - [Archivos](#archivos)
  - [Configuraciones](#configuraciones)
  - [Logs](#logs)
  - [Estado de servicios](#estado-de-servicios)
  - [Esquemas y documentacion](#esquemas-y-documentacion)
- [Recursos aplicados a DevOps](#recursos-aplicados-a-devops)
  - [Kubernetes](#kubernetes)
  - [Terraform](#terraform)
  - [CI/CD](#cicd)
  - [Observabilidad](#observabilidad)
- [Actualizaciones y suscripciones](#actualizaciones-y-suscripciones)
- [Seguridad](#seguridad)
- [Errores comunes](#errores-comunes)
- [Idea clave](#idea-clave)

---

## Vision general

En MCP, un recurso es una fuente de informacion que un servidor expone para que una aplicacion pueda consultarla y utilizarla como contexto.

Un recurso puede representar:

- Un archivo.
- Una configuracion.
- Un esquema de base de datos.
- Un conjunto de logs.
- El estado de un servicio.
- Una respuesta de una API.
- Metricas o alertas.
- Documentacion tecnica.

A diferencia de una herramienta, un recurso no representa principalmente una accion que el modelo debe ejecutar.

Una forma simple de verlo:

```text
El servidor MCP expone informacion
  |
  v
El cliente descubre los recursos disponibles
  |
  v
La aplicacion selecciona un recurso
  |
  v
El client solicita su contenido
  |
  v
La aplicacion incorpora la informacion como contexto
```



## Que es un recurso

Es una fuente de datos identificada de forma unica mediante URI.

Ejemplos sencillos:
```text
file:///project/README.md
kubernetes://cluster/namespaces
terraform://projects/platform/state
ci://pipelines/api/recent-runs
observability://services/api/alerts
```

El servidor MCP puede obtener el contenido desde diferentes sistemas:

- Sistema de archivos.
- Kubernetes.
- Terraform.
- Docker.
- Plataformas CI/CD.
- Bases de datos.
- APIs internas.
- Sistemas de observabilidad.

El recurso no tiene por que ser un archivo fisico. Puede ser una representacion estructurada de informacion obtenida desde un sistema externo.

## Como funciona un recurso

Los recursos siguen normalmente este flujo:

1. El servidor expone los recursos disponibles.
2. El client descubre esos recursos.
3. La aplicacion selecciona uno o varios recursos.
4. El client solicita el contenido.
5. El servidor devuelve los datos y metadatos.
6. La aplicacion decide como utilizar esa informacion.

El protocolo define operaciones como:

```text
resources/list
resources/read
resources/templates/list
```

El host o la aplicacion puede decidir si muestra los recursos en una lista, un explorador, un buscador o cualquier otra interfaz.

### Descubrimiento

Para descubrir los recursos disponibles, el client puede solicitar su listado.

Ejemplo conceptual:

```text
Client ---- resources/list ----> Server
Client <--- resource metadata --- Server
```

El servidor podria devolver:

```json
{
    "resources": [
      {
        "uri":"kubernetes://namespaces/staging/pods",
        "name":"staging-pods",
        "description": "Pods disponibles en el namespace staging",
        "mimeType": "application/json"
      }
    ]
}
```

El listado no tiene por que incluir todo el contenido del resource: normalmente proporciona la informacion necesaria para identificarlo y decidir si debe leerse.

### Lectura

Cuando la aplicacion necesita el contenido de un recurso, el cliente solicita su lectura utilizando la URI.

```text
Client ---- resources/read ----> Server
Client <--- resource contents --- Server
```

Ejemplo:
```json
{
    "uri": "kubernetes://namespaces/staging/pods"
}
```

El servidor podria devolver:

```json
{
    "contents": [
      {
        "uri": "kubernetes://namespaces/staging/pods",
        "mimeType": "application/json",
        "text": "{\"items\":[...]}"
      }
    ]
}
```

La aplicacion puede decidir si envia todo el contenido al modelo, si selecciona una parte o si lo transforma antes de utilizarlo.

### Contenido y metadatos

Un recurso puede incluir contenido y metadatos.

Metadatos habituales:

* URI.
* Nombre.
* Descripcion.
* MIME type.
* Tamaño.
* Fecha de modificacion.
- Informacion sobre la audiencia.
- Prioridad.

Ejemplo:

```json
{
  "uri": "terraform://projects/platform/configuration",
  "name": "platform-configuration",
  "description": "Configuracion Terraform del proyecto platform",
  "mimeType": "text/plain",
  "text": "..."
}
```

Los metadatos ayudan a la aplicacion a decidir como presentar, filtrar o utilizar el recurso.

---

## Recurso vs herramienta

Recursos y herramientas pueden trabajar juntos, pero tienen responsabilidades diferentes.


| Elemento | Tool | Resource |
|---|---|---|
| Proposito | Ejecutar una accion | Proporcionar informacion |
| Control principal | Modelo o aplicacion | Aplicacion |
| Identificacion | Nombre de la tool | URI del resource |
| Entrada | Argumentos estructurados | URI o URI parametrizada |
| Resultado | Resultado de una operacion | Datos o contexto |
| Efectos | Puede modificar sistemas | Normalmente lectura |
| Ejemplo | `get_pod_logs(...)` | `kubernetes://pods/api/logs` |


Ejemplo con Kubernetes:

```text
Tool:
  get_pod_logs(namespace, pod, lines)

Resource:
  kubernetes://namespaces/staging/pods/api/logs
```

La herramienta representa una operacion que puede ejecutarse con parametros.

El recurso representa informacion que la aplicacion puede consultar y utilizar como contexto.

Una regla sencilla:

> Si la idea principal es hacer algo, probablemente sea una herramienta. Si la idea principal es consultar algo, probablemente sea un recurso.


## URIs de recursos

Cada recurso debe tener una URI que permita identificarlo de forma clara.

Una URI bien diseñada deberia ser:

- Predecible.
- Especifica.
- Estable.
- Facil de documentar.
- Segura de validar.

Ejemplos:

```text
kubernetes://clusters/dev/namespaces/api/pods
terraform://projects/platform/modules
ci://pipelines/backend/runs/latest
observability://services/api/alerts
```

La URI no deberia permitir acceder automaticamente a cualquier recurso del sistema.

### Recursos estaticos

Un recurso estatico representa una fuente concreta.

Ejemplos:

```text
file:///project/README.md
kubernetes://clusters/dev/nodes
terraform://projects/platform/configuration
```

La URI apunta siempre al mismo tipo de informacion, aunque el contenido pueda cambiar con el tiempo.

### Plantillas de recursos

Una plantilla de recursos permite definir una URI parametrizada.

Ejemplo:
```text
kubernetes://clusters/{cluster}/namespaces/{namespace}/pods
```

Una URI concreta podria ser:
```text
kubernetes://clusters/dev/namespaces/staging/pods
```

Otro ejemplo:
```text
observability://services/{service}/alerts
```

Que podria utilizarse como:
```text
observability://services/api/alerts
```

Las plantillas permiten representar multiples recursos relacionados sin tener que definir manualmente cada URI.

Los parametros deben validarse antes de utilizarse.

No deberia aceptarse una URI parametrizada que permita acceder a rutas, namespaces o proyectos no autorizados.

---

## Tipos de informacion

### Archivos

Un servidor MCP puede exponer archivos o documentos como recursos.

Ejemplos:
```text
file:///project/README.md
file:///project/docs/deployment.md
file:///projects/terraform/main.tf
```

En DevOps pueden ser utiles para:

* Consultar documentacion de despliegue.
* Leer configuraciones.
* Revisar manifests.
* Consultar runbooks.
* Analizar archivos Terraform.

### Configuraciones

Un recurso puede representar la configuracion actual de un sistema.

Ejemplos:
```text
kubernetes://clusters/dev/configuration
terraform://projects/platform/configuration
docker://compose/backend/configuration
```

Es importante separar las configuraciones que pueden exponerse de aquellas que contienen:

* Contraseñas.
* Tokens.
* Claves privadas.
* Variables sensibles.
* Informacion interna.

### Logs

Los logs pueden exponerse como recursos cuando el objetivo principal es consultar informacion.

Ejemplos:
```text
kubernetes://namespaces/staging/pods/api/logs
docker://containers/api/logs
ci://pipelines/backend/jobs/test/logs
```

Los logs deberian tener limites claros:

* Numero maximo de lineas.
* Rango temporal.
* Tamaño maximo.
* Filtros permitidos.
* Ocultacion de secretos.

Si la consulta de logs requiere muchos parametros o una operacion compleja, puede ser mas apropiado utilizar una tool.

### Estado de servicios

Un recurso puede representar el estado actual de un servicio o plataforma.

Ejemplos:
```text
kubernetes://clusters/production/health
ci://pipelines/backend/status
observability://services/api/health
```

Este tipo de informacion puede ayudar al modelo a comprender el contexto antes de utilizar una tool.

Por ejemplo, antes de reiniciar un servicio, la aplicacion podria consultar primero su estado actual.

### Esquemas y documentacion

Los recursos tambien pueden proporcionar informacion de referencia.

Ejemplos:
```text
database://schemas/production
terraform://projects/platform/modules
api://services/orders/openapi
docs://runbooks/deployment
```

Estos recursos pueden ayudar al asistente a:

* Entender la estructura de una base de datos.
* Conocer los modulos disponibles.
* Consultar contratos de APIs.
- Seguir procedimientos operativos.
* Explicar una arquitectura.

---

## Recursos aplicados a DevOps

### Kubernetes

Ejemplos:
```text
kubernetes://clusters/dev/nodes
kubernetes://clusters/dev/namespaces
kubernetes://namespaces/staging/pods
kubernetes://namespaces/production/events
```
Pueden utilizarse para consultar:

* Pods activos.
* Nodes disponibles.
* Events recientes.
* Estado de deployments.
* Configuracion de namespaces.

Buenas practicas:

* Limitar clusters y namespaces.
* No exponer secretos de Kubernetes.
* Limitar el numero de objetos devueltos.
* Filtrar informacion sensible.
* Aplicar permisos segun el entorno.

### Terraform

Ejemplos:
```text
terraform://projects/platform/configuration
terraform://projects/platform/modules
terraform://projects/platform/plan-summary
terraform://projects/platform/state
```

Los recursos de Terraform pueden proporcionar:

* Configuracion declarada.
* Modulos utilizados.
* Resumen de un plan.
* Estado de recursos.
* Informacion de drift.

El state de Terraform puede contener datos **altamente sensibles**. No deberia exponerse sin controles de acceso y filtrado.

### CI/CD

Ejemplos:
```text
ci://pipelines/backend/status
ci://pipelines/backend/recent-runs
ci://pipelines/backend/deployments
ci://pipelines/backend/jobs/test/logs
```

Estos recursos pueden ayudar a consultar:

* Estado de pipelines.
* Ejecuciones recientes.
* Historial de despliegues.
* Logs de jobs.
* Artefactos disponibles.

Los tokens, variables protegidas y secretos de los jobs nunca deberian formar parte del contenido devuelto.

### Observabilidad

Ejemplos:
```text
observability://services/api/health
observability://services/api/metrics
observability://services/api/alerts
observability://services/api/incidents
```
Pueden proporcionar:

* Estado de servicios.
* Metricas recientes.
- Alertas activas.
- Incidentes abiertos.
* Resumen de trazas.

Conviene limitar:

* Rangos temporales.
- Numero de series.
* Coste de las consultas.
* Tamaño de los resultados.
* Informacion que se envia al modelo.

---

## Actualizaciones y suscripciones

Algunos recursos pueden cambiar con el tiempo.

Por ejemplo:

- El estado de un deployment.
* Las alertas activas.
* Los pods de un namespace.
* El estado de un pipeline.
* Los logs de un contenedor.

El servidor puede notificar que la lista de recursos ha cambiado o que un recurso concreto ha sido actualizado.

Flujo conceptual:
```text
El resource cambia
  |
  v
El servidor envia una notificacion
  |
  v
El client recibe la actualizacion
  |
  v
La aplicacion decide si vuelve a leer el resource
```

Las suscripciones son utiles cuando la aplicacion necesita reaccionar a cambios, pero no siempre son necesarias.

Para una integracion sencilla, puede ser suficiente volver a leer el recurso cuando el usuario lo solicita.

## Seguridad

Los recursos pueden exponer informacion sensible.

Principios recomendados:

* Validar todas las URIs.
* Aplicar controles de acceso.
* Limitar los recursos disponibles por usuario.
* Evitar directory traversal en recursos basados en archivos.
* No devolver secretos.
* Limitar el tamaño de las respuestas.
* Filtrar logs antes de devolverlos.
* Separar entornos de desarrollo, staging y produccion.
* Auditar el acceso a informacion sensible.
* Validar todos los parametros de las plantillas de recursos.

Una buena pregunta antes de exponer un recurso es:

> Si este contenido llega al modelo, ¿cual es el peor resultado posible?


Si la respuesta incluye filtrar credenciales, revelar informacion interna o exponer datos de produccion, el recurso necesita mas controles.


## Buenas practicas

* Usar URIs claras y predecibles.
* Mantener una responsabilidad por recurso.
* Describir correctamente el contenido.
* Incluir MIME type cuando sea util.
* Limitar el volumen de datos.
* Preferir informacion de solo lectura.
* Separar datos publicos, internos y sensibles.
* Utilizar plantillas solo cuando aporten valor.
* Validar los parametros de cada plantilla.
* Documentar la frecuencia de actualizacion.
* Explicar si el contenido puede contener datos sensibles.
* Usar tools cuando exista una accion que ejecutar.

## Errores comunes

* Utilizar un recurso para ejecutar comandos.
* Exponer una URI demasiado generica.
* Permitir acceso arbitrario a rutas.
* Devolver logs ilimitados.
* Exponer secretos en configuraciones.
* Mezclar datos de varios entornos sin identificarlos.
* Confundir un recurso con una tool.
* Crear plantillas sin validar sus parametros.
* No limitar respuestas grandes.
* No controlar el acceso a datos de produccion.
* No documentar el formato del contenido.

Ejemplo de mal diseño:
```text
resource://anything/{path}
```

Problemas:

* Puede permitir acceder a rutas no previstas.
* Es dificil de auditar.
* Puede facilitar directory traversal.
* No deja claro que informacion expone.

Mejor diseño:
```text
terraform://projects/{project}/configuration
```
Con validaciones como:
```text
project:
  - platform
  - payments
  - identity
```

---

## Idea clave

Un recurso MCP proporciona contexto e informacion de forma estructurada.

No es una puerta abierta al sistema ni un sustituto de las herramientas.

Una herramienta ejecuta una accion.

Un recurso expone informacion que la aplicacion puede consultar, filtrar y utilizar para comprender mejor el contexto.

En DevOps, los recursos permiten que el asistente conozca el estado de los sistemas antes de explicar problemas o proponer acciones.


La estructura se apoya en las operaciones actuales `resources/list`, `resources/read` y `resources/templates/list`, además de las URI y las suscripciones definidas por la especificación oficial de MCP. ([Especificación oficial de Resources](https://modelcontextprotocol.io/specification/2026-07-28/server/resources))
