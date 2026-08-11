# 03 - Herramientas [EN](../en/03-tools.md)

## Proposito

Explicar que son las tools en MCP, como se modelan acciones externas y que criterios usar para diseñarlas de forma segura, clara y reutilizable en entornos DevOps.

## Indice

- [Vision general](#vision-general)
- [Que es una Tool](#que-es-una-tool)
  - [Como decide el modelo usar una tool](#como-decide-el-modelo-usar-una-tool)
- [Anatomia de una tool](#anatomia-de-una-tool)
  - [Nombre](#nombre)
  - [Descripcion](#descripcion)
  - [Input schema](#input-schema)
  - [Salida](#salida)
  - [Errores](#errores)
- [Tool vs script](#tool-vs-script)
- [Tool DevOps](#tools-devops)
  - [Kubernetes](#kubernetes)
  - [Terraform](#terraform)
  - [Docker](#docker)
  - [CI/CD](#cicd)
  - [Observabilidad](#observabilidad)
- [Diseno seguro de tools](#diseno-seguro-de-tools)
- [Buenas practicas](#buenas-practicas)
- [Errores comunes](#errores-comunes)
- [Idea clave](#idea-clave)

## Vision general

En MCP, una tool es una capacidad ejecutable que un servidor ofrece al host.

Una tool permite que una aplicacion de IA pueda pedir una accion concreta a un sistema externo de forma estructurada.

Por ejemplo:

- Consultar logs.
- Listar pods.
- Validar un modulo Terraform.
- Revisar el estado de un pipeline.
- Obtener informacion de un contenedor.
- Consultar alertas de observabilidad.

La idea importante es que una tool no deberia ser una puerta abierta a cualquier accion posible. Una buena tool representa una accion concreta, con entradas definidas, limites claros y una salida comprensible.

Una forma simple de verlo:

```text
Usuario pide algo
  |
  v
Host decide si necesita una tool
  |
  v
MCP Client llama a una tool del MCP server
  |
  v
MCP Server ejecuta la accion controlada
  |
  v
Resultado vuelve al host y al asistente
```

## Que es una tool

Una tool es una funcion expuesta por un servidor MCP para que el host pueda invocarla cuando sea util.

Una tool suele tener:

- Un nombre
- Una descripcion
- Un esquema de entrada
- Una salida
- Posibles errores

He aqui un ejemplo conceptual:

```text
Tool: get_pod_logs

Descripcion:
  Obtiene logs recientes de un pod de Kubernetes.

Entrada:
  namespace: string
  pod: string
  lines: number opcional

Salida:
  logs: string
  namespace: string
  pod: string
  lines: number
```

En este ejemplo, la tool no permite ejecutar cualquier comando de Kubernetes. Solo permite consultar logs de un pod, con parametros concretos.

Eso hace que la accion sea mas facil de entender, validar, auditar y reutilizar.

### Como decide el modelo usar una tool

El modelo no deberia adivinar herramientas ocultas. El host conoce las tools disponibles porque el servidor MCP las expone.

Cuando una tool esta disponible, su nombre, descripcion y esquema ayudan al modelo o al host a decidir si debe usarla.

Por eso la descripcion de una tool es importante.

Una descripcion vaga produce usos incorrectos.

Ejemplo malo:
```text
name: check
description: Checks things.
```

Ejemplo mejor:
```text
name: terraform_validate
description: Valida la sintaxis y configuracion de un proyecto Terraform sin aplicar cambios.
```

---

## Anatomia de una tool

Una tool bien diseñada tiene un contrato claro.

Ese contrato permite que el host sepa como invocarla y que el servidor pueda validar la entrada antes de ejecutar nada.

### Nombre

El nombre deberia ser corto, descriptivo y especifico.

Buenos ejemplos:

```text
get_pod_logs
list_namespaces
terraform_validate
docker_list_containers
get_pipeline_status
```

Malos ejemplos:

```text
run
execute
do_task
check
devops_tool
```

Un buen nombre ayuda al modelo a elegir la tool correcta y ayuda a las personas a entender que hace.

### Descripcion

La descripcion explica cuando usar la tool y que hace exactamente.

Debe responder:

- Que accion realiza.
- Sobre que sistema actua.
- Si modifica o no modifica estado.
- Que limitaciones importantes tiene.

Ejemplo:

```text
Obtiene los logs recientes de un pod de Kubernetes en un namespace permitido.
```

Esta descripcion es mejor que simplemente decir:

```text
Obtiene logs
```

Porque da contexto operativo y de seguridad.

### Input schema

El input schema define los parametros que aceptan la tool.

Sirve como contrato entre el host y el servidor.

Ejemplo conceptual:
```json
{
  "namespace": "string",
  "pod": "string",
  "lines": "number"
}
```

El esquema deberia ser lo mas restrictivo posible.

Por ejemplo:

- `namespace` deberia ser obligatorio.
- `pod` deberia ser obligatorio.
- `lines` podria tener un limite maximo
- No deberia aceptarse un comando arbitrario como string.

Ejemplo peligroso:
```json
{
  "command": "string"
}
```

Ejemplo mas seguro:
```json
{
  "namespace": "string",
  "pod": "string",
  "lines": "number"
}
```

En DevOps, un input schema demasiado abierto suele convertirse en un riesgo.

### Salida

La salida de una tool deberia ser clara y, cuando sea posible, estructurada.

Ejemplo simple:

```json
{
  "namespace":"staging",
  "pod": "api-7c9d9f7d4b-x2k8p",
  "lines": 100,
  "logs": "...",
  "truncated": false
}
```

Una salida estructurada permite que el asistente explique mejor el resultado y que otros sistemas puedan reutilizarlo.

Cuando la salida sea texto largo, como logs, puede ser util incluir metadatos:

- Si el resultado fue truncado.
- Cuantas lineas se devolvieron.
- De que recursos viene.
- Si hubo warnings.
- Que timestamp cubre.

### Errores

Las tools deben devolver errores comprensibles.

No basta con fallar de forma generica.

Ejemplos de errores utiles:
```text
namespace_not_allowed
pod_not_found
invalid_line_limit
command_timeout
terraform_project_not_found
pipeline_not_found
```

Un buen error deberia ayudar a entender:

- Que fallo.
- Si el usuario puede corregirlo.
- Si la accion fue parcial o no se ejecuto.
- Si hay una restriccion de seguridad.

Ejemplo:
```json
{
  "error":"namespace_not_allowed",
  "message": "El namespace production no esta permitido para esta tool.",
  "details": {
    "namespace": "production",
    "allowedNamespaces": ["dev", "staging"]
  }
}
```
Este tipo de respuesta es mucho mas util que:
```text
Error:failed
```
---

## Tool vs script

Una tool MCP no es simplemente un script expuesto al modelo.

Un script suele estar pensado para ser ejecutado por una persona o pipeline.

Una tool MCP esta pensada para ser descubierta, entendida e invocada por una aplicacion de IA a traves de un contrato claro.

Diferencias importantes:

```text
Script:
  - Puede aceptar argumentos libres.
  - Puede asumir contexto local.
  - Puede imprimir texto sin estructura.
  - Puede mezclar varias responsabilidades.

Tool MCP:
  - Tiene nombre y descripcion.
  - Tiene input schema.
  - Debe validar entradas.
  - Debe devolver una salida clara.
  - Deberia tener una responsabilidad concreta.
```

Esto no significa que una tool no pueda llamar internamente a un script.

Puede hacerlo, pero la tool deberia envolver ese script con una interfaz segura, validada y comprensible.

## Tools DevOps

Las tools DevOps deberian modelar acciones concretas y preferiblemente no destructivas al principio.

El objetivo inicial no deberia ser automatizar todo, sino exponer capacidades utiles con limites claros.

### Kubernetes

Ejemplos de tools:
```text
list_namespaces
list_pods
get_pod_logs
describe_deployment
list_events
check_namespace_health
```

Buenas ideas:

- Limitar namespaces permitidos.
- Limitar cantidad de logs.
- Evitar comandos arbitrarios.
- Separar lectura de acciones que modifican el cluster.

Tool peligrosa:
```text
kubectl_raw(command: string)
```

Tool mas segura:
```text
get_pod_logs(namespace: string, pod: string, lines: number)
```

### Terraform

Ejemplos de tools:
```text
terraform_fmt_check
terraform_validate
terraform_plan_summary
list_terraform_modules
detect_drift
```

Buenas ideas:

- Empezar con acciones de lectura o validacion.
- Evitar `apply` por defecto.
- Validar rutas de proyecto.
- Resumir planes sin exponer secretos.
- Separar validacion de ejecucion real.

Tool peligrosa:
```text
terraform_command(args: string)
```

Tool mas segura:
```text
terraform_validate(projectPath: string)
```

### Docker

Ejemplos de tools:
```text
list_containers
get_container_logs
inspect_container
inspect_image
check_compose_services
```

Buenas ideas:

- Evitar montar acceso completo al socket Docker sin limites.
- Limitar operaciones destructivas.
- Distinguir entre listar, inspeccionar, iniciar, detener y eliminar.
- Truncar logs largos.

Tool peligrosa:
```text
docker_run(command: string)
```

Tool mas segura:
```text
get_container_logs(containerName: string, lines: number)
```

### CI/CD

Ejemplos de tools:
```text
get_pipeline_status
list_recent_runs
get_failed_job_logs
compare_pipeline_runs
get_deployment_history
```

Buenas ideas:

- Consultar estado antes de ejecutar acciones.
- Evitar relanzar pipelines sin confirmacion.
- No exponer tokens o secretos de jobs.
- Resumir logs largos.

Tool peligrosa:
```text
run_pipeline(pipelineId: string)
```

Tool mas segura:
```text
get_pipeline_status(pipelineId: string)
```

### Observabilidad

Ejemplos de tools:

```text
list_alerts
get_services_metrics
query_logs
get_trace_summary
get_incident_status
```

Buenas ideas:

- Limitar rangos de tiempo.
- Evitar consultas demasiado costosas.
- Devolver resumen y metadatos.
- Separar logs, metricas y trazas en tools diferentes si ayuda a mantener claridad.

Tool mas segura:

```text
get_service_metrics(service: string, from: string, to: string)
```

---

## Diseño seguro de tools

En DevOps, una tool puede tocar sistemas sensibles.

Por eso, el diseño seguro no es opcional, sino obligatorio:

Principios recomendados:

- Preferir tools especificas antes que tools genericas.
- Validar todos los parametros.
- Limitar rutas, namespaces, proyectos o servicios permitidos.
- Usar allowlists cuando sea posible.
- Definir timeouts.
- Limitar tamaño de salida.
- Separar lectura de escritura.
- Evitar acciones destructivas por defecto.
- Requerir confirmacion humana para acciones sensibles.
- Registrar acciones importantes para auditoria.

Una buena pregunta antes de crear una tool es:

> Si el modelo usa mal esta tool, ¿cual es el peor resultado posible?

Si la respuesta incluye borrar recursos, desplegar cambios, filtrar secretos o romper produccion, la tool necesita mas limites o quizas no deberia existir todavia.


## Buenas practicas

Buenas practicas para diseñar tools MCP:

- Usar nombres claros y especificos.
- Escribir descripciones que expliquen cuando usar la tool.
- Mantener una responsabilidad por tool.
- Usar input schemas restrictivos.
- Devolver salidas estructuradas.
- Incluir metadatos utiles.
- Devolver errores accionables.
- Evitar comandos arbitrarios.
- Pensar en permisos desde el principio.
- Documentar si la tool modifica estado o solo consulta informacion.

Ejemplo de descripcion recomendable:

```text
Valida un proyecto Terraform ejecutando checks no destructivos. No aplica cambios ni modifica infraestructura.
```

---

## Errores comunes

Errores frecuentes al diseñar tools MCP:

- Crear una tool demasiado generica.
- Usar nombres ambiguos.
- No explicar si la tool modifica estado.
- Aceptar comandos libres como entrada.
- No validar parametros.
- Devolver texto sin estructura cuando podria devolverse JSON.
- Mezclar varias responsabilidades en una sola tool.
- No limitar logs o resultados grandes.
- Exponer acciones destructivas demasiado pronto.
- No pensar en auditoria.

Ejemplo de mal diseño:

```text
run_devops_task(task: string)
```

Problemas:

- No queda claro que puede hacer.
- Es dificil de validar.
- Es dificil de auditar.
- Puede terminar ejecutando acciones no previstas.
- El modelo podria usarla en contextos incorrectos.

Mejor diseño:
```text
terraform_validate(projectPath: string)
get_pod_logs(namespace: string, pod: string, lines: number)
get_pipeline_status(pipelineId: string)
```

## Idea clave

Una tool MCP no deberia ser una puerta abierta al sistema.

Una tool MCP deberia ser una accion concreta, validada y segura que el host pueda ofrecer al asistente.

En DevOps, diseñar bien las tools es la diferencia entre un asistente util y una automatizacion peligrosa.
