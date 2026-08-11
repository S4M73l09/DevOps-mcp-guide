# 01 - Que es MCP [EN](../en/01-what-is-mcp.md)

## Proposito

Explicar que es Model Context Protocol (MCP), que problema resuelve y por que es util para integrar asistentes con herramientas externas.

## Indice

- [Que es MCP](#que-es-mcp)
  - [Que problema resuelve](#que-problema-resuelve)
- [Relacion entre Host Client y Server](#relacion-entre-host-client-y-server)
  - [Host](#host)
  - [Client](#client)
  - [Server](#server)
- [Flujo conceptual](#flujo-conceptual)
- [Ejemplos de uso en DevOps](#ejemplos-de-uso-en-devops)
  - [Kubernetes](#kubernetes)
  - [Terraform](#terraform)
  - [Docker](#docker)
  - [CI/CD](#cicd)
  - [Observabilidad](#observabilidad)
- [Cuando usar MCP](#cuando-usar-mcp)
- [Cuando no usar MCP](#cuando-no-usar-mcp)
- [Idea Clave](#idea-clave)

## Que es MCP

Model Context Protocol, o MCP, es un protocolo abierto que estandariza la forma en que una aplicacion de IA se conecta con sistemas externos.

Su objetivo principal es permitir que un asistente pueda acceder a contexto, ejecutar herramientas y usar flujos predefinidos sin que cada integracion tenga que inventar su propio mecanismo desde cero.

En lugar de crear una integracion distinta para cada combinacion de asistente y herramienta, MCP propone una interfaz comun entre:

- Aplicaciones de IA.
- Servidores que exponen capacidades.
- Herramientas, datos y prompts reutilizables.

Una forma simple de verlo:

> MCP es una capa estandar para conectar asistentes de IA con herramientas y fuentes de contexto externas.

### Que problema resuelve

Sin MCP, integrar una IA con herramientas externas suele implicar soluciones a medida:

- Un conector especifico para GitHub.
- Otro conector distinto para Kubernetes.
- Otro para Terraform.
- Otro para logs.
- Otro para CI/CD.
- Otro para documentacion interna.

Esto genera varios problemas:

- Integraciones dificiles de reutilizar.
- Logica duplicada entre proyectos.
- Falta de un contrato claro entre la IA y las herramientas.
- Seguridad dificil de controlar.
- Dificultad para saber que puede o no puede hacer el asistente.
- Acoplamiento fuerte entre el cliente de IA y cada sistema externo.

MCP resuelve esto definiendo un protocolo comun para exponer capacidades mediante primitivas como:

- Tools: acciones ejecutables.
- Resources: informacion o contexto consultable.
- Prompts: plantillas reutilizables para tareas frecuentes.

## Relacion entre Host Client y Server

MCP usa una arquitectura host-client-server.

### Host

El host es la aplicacion donde vive la experiencia de IA.

Ejemplos de host pueden ser:

- Un editor de codigo con capacidades de IA.
- Una aplicacion de escritorio con un asistente.
- Un entorno de automatizacion.
- Un agente interno de una empresa.

El host coordina la experiencia general, gestiona permisos y decide como usar el contexto recibido.

### Client

El cliente MCP es el componente que gestiona la comunicacion entre el host y un servidor MCP concreto.

Normalmente, el host crea un cliente por cada servidor MCP al que se conecta.

Por ejemplo:

- Un cliente para un servidor MCP de Git.
- Un cliente para un servidor MCP de Kubernetes.
- Un cliente para un servidor MCP de Terraform.

Cada cliente mantiene aislada la integracion con su servidor.

### Server

El servidor MCP es el programa que expone capacidades al host a traves del protocolo MCP.

Un servidor puede ofrecer:

- Tools para ejecutar acciones.
- Resources para consultar informacion.
- Prompts para reutilizar instrucciones o flujos.

Ejemplos:

- Un servidor MCP que consulta logs.
- Un servidor MCP que lista pods de Kubernetes.
- Un servidor MCP que valida Terraform.
- Un servidor MCP que consulta pipelines de CI/CD.
- Un servidor MCP que lee documentacion interna.

## Flujo conceptual

1. El usuario pide algo al asistente.
2. El host interpreta la peticion.
3. El host usa un cliente MCP para hablar con un servidor MCP.
4. El servidor MCP expone tools, resources o prompts.
5. El host decide que capacidades usar.
6. El resultado vuelve al asistente.
7. El asistente responde al usuario con mas contexto o con una accion realizada.

## Ejemplos de uso en DevOps

MCP encaja muy bien en DevOps porque muchas tareas consisten en consultar estado, validar configuraciones, diagnosticar problemas o ejecutar acciones controladas.

### Kubernetes

Un servidor MCP podria exponer tools como:

- `list_pods`
- `get_pod_logs`
- `describe_deployment`
- `list_events`
- `check_namespace_health`

Esto permitiria pedir:

> Revisa por que el deployment `api` esta fallando en staging.

El asistente podria consultar pods, eventos y logs sin que el usuario copie manualmente todos los comandos.

### Terraform

Un servidor MCP podria exponer tools como:

- `terraform_fmt_check`
- `terraform_validate`
- `terraform_plan_summary`
- `list_modules`
- `detect_drift`

Esto permitiria pedir:

> Valida este modulo Terraform y dime si hay riesgos antes de abrir el PR.

### Docker

Un servidor MCP podria exponer tools como:

- `list_containers`
- `get_container_logs`
- `inspect_image`
- `check_compose_services`

Esto permitiria pedir:

> Mira por que el contenedor de backend no arranca.

### CI/CD

Un servidor MCP podria conectarse a sistemas de pipelines y exponer:

- estado de builds
- logs de jobs fallidos
- artefactos generados
- historial de despliegues
- comparacion entre ejecuciones

Ejemplo:

> Resume por que fallo el ultimo pipeline de main.

### Observabilidad

Un servidor MCP podria consultar:

- metricas
- trazas
- logs
- alertas
- incidencias abiertas

Ejemplo:

> Busca señales de error alrededor del despliegue de las 10:30.

## Cuando usar MCP

MCP tiene sentido cuando queremos que una IA interactue con herramientas externas de forma estructurada, segura y reutilizable.

Se usa cuando:

- Quieres exponer capacidades a uno o varios asistentes.
- Necesitas integrar herramientas DevOps con una interfaz comun.
- Hay operaciones repetibles que pueden modelarse como tools.
- Hay informacion util que puede exponerse como resources.
- Quieres controlar permisos, entradas y acciones permitidas.
- Quieres separar la logica DevOps del cliente de IA.
- Quieres crear una integracion reutilizable por otras personas o equipos.

## Cuando no usar MCP

MCP no siempre es necesario.

No hace falta usar MCP cuando:

- Solo necesitas un script puntual.
- La tarea no involucra una aplicacion de IA.
- La integracion sera usada una sola vez.
- No necesitas exponer capacidades reutilizables.
- La herramienta ya esta integrada directamente de forma suficiente.
- El coste de mantener un servidor MCP supera el beneficio.
- La accion es demasiado sensible y no tienes un modelo claro de permisos, auditoria y confirmacion humana.

## Idea clave

MCP no reemplaza las herramientas DevOps.

MCP crea una interfaz estandar para que una aplicacion de IA pueda usar esas herramientas de forma controlada.

En DevOps, esto significa que podemos pasar de:

> Copia logs, pega errores, ejecuta comandos manualmente y pide ayuda al asistente.

A:

> El asistente consulta contexto autorizado, ejecuta checks seguros y ayuda a diagnosticar con datos reales.
