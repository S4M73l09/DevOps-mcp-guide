# 05 - Prompts [EN](../en/05-prompts.md)

## Proposito

Explicar que son los prompts MCP, como estructuran flujos reutilizables y como pueden aplicarse a tareas operativas de DevOps.

## Indice

- [Vision general](#vision-general)
- [Que es un prompt MCP](#que-es-un-prompt-mcp)
- [Como funciona un prompt](#como-funciona-un-prompt)
  - [Descubrimiento](#descubrimiento)
  - [Invocacion](#invocacion)
  - [Argumentos](#argumentos)
  - [Mensajes generados](#mensajes-generados)
- [Prompts vs tools vs resources](#prompts-vs-tools-vs-resources)
- [Prompts y comandos del dia a dia](#prompts-y-comandos-del-dia-a-dia)
- [Prompts aplicados a DevOps](#prompts-aplicados-a-devops)
  - [Diagnosticar un servicio](#diagnosticar-un-servicio)
  - [Revisar un despliegue](#revisar-un-despliegue)
  - [Analizar un fallo de CI/CD](#analizar-un-fallo-de-cicd)
  - [Revisar un plan Terraform](#revisar-un-plan-terraform)
  - [Investigar una alerta](#investigar-una-alerta)
  - [Consultar un runbook](#consultar-un-runbook)
- [Ejemplo de prompt](#ejemplo-de-prompt)
- [Diseno de prompts](#diseno-de-prompts)
- [Seguridad](#seguridad)
- [Buenas practicas](#buenas-practicas)
- [Errores comunes](#errores-comunes)
- [Idea clave](#idea-clave)

## Vision general

En MCP, un prompt es una plantilla reutilizable que un servidor expone para ayudar al usuario a iniciar una tarea concreta.

Un prompt puede orientar al modelo para:

- Consultar determinados resources.
- Utilizar tools especificas.
- Seguir un flujo de diagnostico.
- Analizar una situacion operativa.
- Aplicar un procedimiento documentado.
- Devolver una respuesta con una estructura concreta.

La idea principal es:

```text
El usuario selecciona un prompt
  |
  v
El host solicita el prompt al servidor
  |
  v
El servidor devuelve mensajes preparados
  |
  v
El modelo utiliza tools y resources
  |
  v
El asistente devuelve el resultado al usuario
```

Un prompt no deberia ser una puerta abierta para ejecutar cualquier accion.

Su funcion es estructurar una tarea y hacer mas predecible la interaccion.

## Que es un prompt MCP

Un prompt MCP es una plantilla de instrucciones que el servidor ofrece al host.

Ejemplos conceptuales:

```text
diagnose-service
review-deployment
analyze-pipeline-failure
review-terraform-plan
investigate-alert
follow-runbook
```

Un prompt puede incluir:

- Un nombre.
- Un titulo.
- Una descripcion.
- Argumentos.
- Mensajes preparados.
- Referencias a tools o resources.
- Instrucciones sobre el formato de salida.

A diferencia de una instruccion normal escrita libremente por el usuario, un prompt MCP proporciona una estructura reutilizable.

Por ejemplo, un usuario podria escribir:

```text
Revisa que esta pasando con api en produccion.
```

Un prompt definido por el servidor podria estructurar esa tarea de esta manera:

```text
Prompt: diagnose-service

Arguments:
  service: api
  environment: production
  symptom: high error rate
```

Esto permite que el modelo reciba informacion mas clara y que el flujo pueda reutilizarse en diferentes situaciones.

## Como funciona un prompt

Los prompts suelen seguir este flujo:

1. El servidor expone los prompts disponibles.
2. El host muestra esos prompts al usuario.
3. El usuario selecciona un prompt.
4. El usuario proporciona los argumentos necesarios.
5. El host solicita el prompt al servidor.
6. El servidor devuelve mensajes preparados.
7. El modelo utiliza el contexto, tools y resources disponibles.

Las operaciones principales son:

```text
prompts/list
prompts/get
```

El host puede mostrar los prompts mediante:

- Comandos con `/`.
- Una paleta de comandos.
- Botones de acciones frecuentes.
- Menus contextuales.
- Plantillas seleccionables desde la interfaz.

Los prompts son controlados por el usuario. Normalmente deben invocarse de forma explicita y no activarse automaticamente como una tool.

### Descubrimiento

Para descubrir los prompts disponibles, el client puede solicitar su listado:

```text
Client ---- prompts/list ----> Server
Client <--- prompt metadata --- Server
```

El servidor podria devolver:

```json
{
  "prompts": [
    {
      "name": "diagnose-service",
      "title": "Diagnosticar un servicio",
      "description": "Analiza un problema operativo utilizando informacion disponible."
    }
  ]
}
```

El listado proporciona la informacion necesaria para que el host pueda mostrar y describir cada prompt.

### Invocacion

Cuando el usuario selecciona un prompt, el host puede solicitarlo utilizando su nombre y sus argumentos:

```text
Client ---- prompts/get ----> Server
Client <--- prompt messages --- Server
```

Ejemplo conceptual:

```json
{
  "name": "diagnose-service",
  "arguments": {
    "service": "api",
    "environment": "production",
    "symptom": "high error rate"
  }
}
```

El servidor devuelve los mensajes que forman el prompt.

El host puede incorporar esos mensajes a la conversacion y permitir que el modelo continue el flujo.

### Argumentos

Los prompts pueden recibir argumentos para adaptar la plantilla a cada situacion.

Ejemplo:

```text
Prompt: diagnose-service

Arguments:
  service: api
  environment: production
  symptom: high error rate
```

Los argumentos deberian:

- Tener nombres claros.
- Describir su finalidad.
- Validarse cuando sea posible.
- Indicar si son obligatorios.
- Evitar aceptar datos innecesarios.
- Diferenciar correctamente entornos y recursos.

Un prompt sin argumentos puede ser util para tareas generales:

```text
Prompt: explain-cluster-health
```

Un prompt parametrizado puede adaptarse mejor a una operacion concreta:

```text
Prompt: diagnose-service
Arguments:
  service
  environment
  symptom
```

### Mensajes generados

Un prompt puede devolver uno o varios mensajes preparados.

Ejemplo conceptual:

```text
Analiza el servicio api en el entorno production.

Sintoma reportado:
high error rate

Utiliza los resources disponibles para consultar:

- Alertas activas.
- Metricas recientes.
- Logs relevantes.
- Despliegues recientes.

Devuelve:

1. Evidencias encontradas.
2. Hipotesis posibles.
3. Acciones seguras recomendadas.
4. Acciones que requieren confirmacion humana.
```

El prompt no deberia inventar datos ni asumir que todos los resources o tools existen.

Debe guiar al modelo para que descubra y utilice las capacidades realmente disponibles.


---



## Prompts vs tools vs resources

Las tres primitivas pueden trabajar juntas, pero tienen funciones distintas.

| Elemento | Tool | Resource | Prompt |
|---|---|---|---|
| Proposito | Ejecutar una accion | Proporcionar informacion | Estructurar una tarea |
| Control principal | Modelo o aplicacion | Aplicacion | Usuario |
| Identificacion | Nombre de la tool | URI del resource | Nombre del prompt |
| Entrada | Argumentos estructurados | URI o URI parametrizada | Argumentos del prompt |
| Resultado | Resultado de una operacion | Datos o contexto | Mensajes preparados |
| Ejemplo | `get_pod_logs(...)` | `kubernetes://pods/api/logs` | `diagnose-service` |

Una forma sencilla de recordarlo:

```text
Tool:
  Hace algo.

Resource:
  Proporciona algo.

Prompt:
  Guia sobre como abordar algo.
```

Ejemplo combinado:

```text
Prompt:
  diagnose-service

Resources:
  observability://services/api/alerts
  observability://services/api/metrics
  kubernetes://namespaces/production/pods

Tools:
  get_service_metrics(...)
  get_pod_logs(...)
  list_alerts(...)
```

El prompt estructura el flujo.

Los resources aportan contexto.

Las tools ejecutan operaciones concretas.

## Prompts y comandos del dia a dia

Los prompts pueden presentarse como comandos de uso frecuente dentro del host.

Ejemplos:

```text
/diagnose-service api production
/review-deployment payments staging
/analyze-pipeline-failure backend 1842
/review-terraform-plan platform staging
/investigate-alert api-high-latency api production
```

Estos comandos no tienen por que ser comandos de terminal.

Pueden ser una forma de invocar prompts desde:

- Un chat.
- Una paleta de comandos.
- Una interfaz web.
- Un editor de codigo.
- Un sistema interno de operaciones.

Por ejemplo:

```text
Usuario escribe:
/diagnose-service api production
```

El host puede resolverlo como:

```text
Prompt:
  diagnose-service

Arguments:
  service: api
  environment: production
```

Y solicitarlo al servidor:

```text
Client ---- prompts/get ----> Server
Client <--- prompt messages --- Server
```

Despues, el modelo puede utilizar las tools y resources disponibles para completar el diagnostico.

La ventaja es que las tareas frecuentes tienen una estructura comun y no dependen completamente de que cada usuario escriba instrucciones diferentes.

## Prompts aplicados a DevOps

### Diagnosticar un servicio

```text
Prompt:
  diagnose-service

Arguments:
  service
  environment
  symptom
```

Ejemplo:

```text
/diagnose-service api production "high error rate"
```

El prompt puede indicar al modelo que consulte:

- Alertas activas.
- Metricas recientes.
- Logs.
- Estado de pods.
- Despliegues recientes.
- Incidentes abiertos.

El resultado podria organizarse asi:

```text
1. Resumen del problema.
2. Evidencias encontradas.
3. Posibles causas.
4. Recursos afectados.
5. Siguientes pasos recomendados.
6. Acciones que requieren aprobacion.
```

### Revisar un despliegue

```text
Prompt:
  review-deployment

Arguments:
  service
  environment
  deployment_id
```

Ejemplo:

```text
/review-deployment payments staging deploy-1842
```

El flujo podria pedir:

- Revisar el historial del despliegue.
- Consultar el estado actual.
- Comparar con el despliegue anterior.
- Revisar errores conocidos.
- Consultar metricas posteriores al despliegue.
- Recomendar una investigacion adicional.

El prompt no deberia ejecutar un rollback automaticamente.

Una accion de rollback deberia estar representada por una tool independiente y requerir confirmacion y permisos adecuados.

### Analizar un fallo de CI/CD

```text
Prompt:
  analyze-pipeline-failure

Arguments:
  pipeline
  run_id
```

Ejemplo:

```text
/analyze-pipeline-failure backend 1842
```

El prompt podria guiar el analisis de:

- Estado del pipeline.
- Job que fallo.
- Logs del job.
- Cambios recientes.
- Historial de ejecuciones.
- Artefactos generados.
- Posibles causas.

El resultado deberia distinguir entre hechos observados e hipotesis.

### Revisar un plan Terraform

```text
Prompt:
  review-terraform-plan

Arguments:
  project
  environment
```

Ejemplo:

```text
/review-terraform-plan platform staging
```

El prompt deberia pedir:

- Resumir los cambios.
- Separar recursos añadidos, modificados y eliminados.
- Identificar posibles riesgos.
- Detectar cambios en produccion.
- Señalar recursos sensibles.
- Solicitar confirmacion antes de cualquier aplicacion.

La tool que ejecuta `terraform apply` deberia permanecer separada y disponer de controles adicionales.

### Investigar una alerta

```text
Prompt:
  investigate-alert

Arguments:
  alert
  service
  environment
```

Ejemplo:

```text
/investigate-alert api-high-latency api production
```

El prompt puede estructurar el analisis en:

1. Estado de la alerta.
2. Momento de inicio.
3. Metricas relacionadas.
4. Logs relevantes.
5. Cambios recientes.
6. Hipotesis.
7. Siguientes pasos seguros.

### Consultar un runbook

```text
Prompt:
  follow-runbook

Arguments:
  runbook
  service
  environment
```

Ejemplo:

```text
/follow-runbook high-latency api production
```

El prompt puede combinar:

```text
Resource:
  docs://runbooks/high-latency

Resources:
  observability://services/api/metrics
  observability://services/api/alerts

Tools:
  get_service_metrics(...)
  get_alert_details(...)
```

Aqui se ve el valor de combinar las tres primitivas:

- El prompt estructura el flujo.
- Los resources aportan contexto.
- Las tools ejecutan consultas o acciones concretas.


---


## Ejemplo de prompt

Ejemplo conceptual de definicion:

```json
{
  "name": "diagnose-service",
  "title": "Diagnosticar un servicio",
  "description": "Analiza un incidente utilizando metricas, alertas, logs e historial de despliegues.",
  "arguments": [
    {
      "name": "service",
      "description": "Servicio que se va a investigar",
      "required": true
    },
    {
      "name": "environment",
      "description": "Entorno objetivo",
      "required": true
    },
    {
      "name": "symptom",
      "description": "Sintoma o error observado",
      "required": true
    }
  ]
}
```

El contenido generado podria ser:

```text
Estas investigando un incidente DevOps.

Servicio: api
Entorno: production
Sintoma: high error rate

Utiliza los resources disponibles para consultar:

- Alertas actuales.
- Metricas recientes.
- Logs relevantes.
- Despliegues recientes.

Utiliza tools de solo lectura durante la investigacion.

Devuelve:

1. Evidencias encontradas.
2. Causas probables.
3. Siguientes pasos recomendados.
4. Acciones que requieren aprobacion humana.
```

Este ejemplo no ejecuta ninguna accion por si mismo.

Su objetivo es orientar el flujo y definir el formato de la respuesta.

## Diseno de prompts

Un prompt bien diseñado deberia ser concreto, predecible y facil de revisar.

Antes de crear uno, conviene definir:

- Que tarea inicia.
- Que argumentos necesita.
- Que resources deberia consultar.
- Que tools puede utilizar.
- Que informacion debe devolver.
- Que acciones quedan fuera de su alcance.

Un prompt de diagnostico y uno de remediacion no deberian mezclarse sin una razon clara.

Una estructura recomendable es:

```text
Contexto:
  Que sistema o servicio se analiza.

Objetivo:
  Que debe averiguar el modelo.

Fuentes:
  Que resources debe consultar.

Operaciones:
  Que tools puede utilizar.

Restricciones:
  Que no debe hacer.

Salida:
  Como debe presentar el resultado.
```

## Seguridad

Un prompt no es automaticamente seguro por ser una plantilla.

Puede orientar al modelo hacia operaciones sensibles y combinar tools con diferentes niveles de riesgo.

Los prompts deberian:

- Indicar claramente el entorno.
- Diferenciar desarrollo, staging y produccion.
- Priorizar tools de lectura.
- Prohibir acciones destructivas por defecto.
- Pedir confirmacion humana antes de cambios.
- No incluir secretos.
- No ocultar las tools que se pretenden utilizar.
- Evitar instrucciones ambiguas.
- Definir que hacer si faltan datos.
- Separar diagnostico de remediacion.

Una division util seria:

```text
Prompt de diagnostico:
  Consulta informacion y resume evidencias.

Prompt de remediacion:
  Propone acciones, pero necesita confirmacion.

Prompt de ejecucion:
  Requiere permisos y aprobacion explicita.
```

Una buena pregunta antes de crear un prompt es:

> Si el modelo sigue estas instrucciones de forma incorrecta, ¿cual es el peor resultado posible?

Si la respuesta incluye borrar recursos, desplegar cambios, filtrar secretos o afectar produccion, el prompt necesita mas controles.

## Buenas practicas

- Usar nombres claros y especificos.
- Mantener cada prompt centrado en una tarea.
- Definir argumentos explicitos.
- Describir que informacion debe consultar.
- Indicar que tools puede utilizar.
- Indicar que resources son relevantes.
- Separar diagnostico y ejecucion.
- Pedir confirmacion para acciones sensibles.
- Devolver resultados con una estructura predecible.
- Documentar limitaciones.
- Validar argumentos.
- Evitar prompts excesivamente genericos.
- Indicar que hacer cuando no haya datos suficientes.

## Errores comunes

- Crear un prompt que intenta resolver cualquier problema.
- Confundir un prompt con una tool.
- Ejecutar comandos destructivos desde una plantilla.
- No diferenciar el entorno.
- No solicitar argumentos importantes.
- Ocultar las acciones que el flujo puede realizar.
- Mezclar diagnostico y remediacion.
- No validar los parametros.
- Asumir que siempre habra datos disponibles.
- No incluir una salida estructurada.
- Depender de nombres concretos de tools sin documentarlo.
- Presentar hipotesis como si fueran hechos confirmados.

## Idea clave

Un prompt MCP no ejecuta por si mismo una tarea DevOps.

Su funcion es proporcionar una estructura reutilizable para que el usuario inicie un flujo claro y para que el modelo combine resources y tools de forma controlada.

En DevOps:

```text
Prompt:
  Define el flujo.

Resource:
  Aporta el contexto.

Tool:
  Ejecuta una operacion.
```

Los prompts permiten convertir procedimientos operativos frecuentes en flujos reutilizables, comprensibles y mas faciles de revisar.

La estructura de este capitulo se basa en las operaciones `prompts/list` y `prompts/get`, y en el modelo de prompts controlados explicitamente por el usuario definido por MCP.
