# 02 - Arquitectura [EN](../en/02-architecture.md)

## Proposito

Explicar como se organiza MCP por dentro: participantes, capas, ciclo de vida de una conexion y capacidades que puede exponer cada parte.

## Indice

- [Vision general](#vision-general)
- [Participantes principales](#participantes-principales)
  - [Host](#host)
  - [Client](#client)
  - [Server](#server)
- [Capas de MCP](#capas-de-mcp)
  - [Data layer](#data-layer)
  - [Transport layer](#transport-layer)
- [Ciclo de vida de una conexion](#ciclo-de-vida-de-una-conexion)
  - [Inicializacion](#inicializacion)
  - [Operacion](#operacion)
  - [Cierre](#cierre)
- [Capacidades](#capacidades)
  - [Capacidades del servidor](#capacidades-del-servidor)
  - [Capacidades del cliente](#capacidades-del-cliente)
- [Arquitectura local vs remota](#arquitectura-local-vs-remota)
- [Ejemplo aplicado a DevOps](#ejemplo-aplicado-a-devops)
- [Idea clave](#idea-clave)

## Vision general

MCP sigue una arquitectura cliente-servidor, pero con tres conceptos importantes: host, client y server.

El host es la aplicacion de IA. El client es la conexion MCP concreta que vive dentro del host. El server es el programa que expone capacidades externas.

Una forma simple de verlo:

```text
Usuario
  |
  v
Host de IA
  |
  +-- MCP Client ---- MCP Server
```

En una integracion real, el host puede conectarse a varios servidores MCP al mismo tiempo. Para cada servidor, el host crea un cliente MCP independiente.

```text
Host de IA
  |
  +-- MCP Client ---- Servidor MCP Git
  |
  +-- MCP Client ---- Servidor MCP Kubernetes
  |
  +-- MCP Client ---- Servidor MCP Terraform
```

Esta separacion permite que cada servidor MCP tenga una responsabilidad concreta y que el host pueda componer capacidades de varios sistemas.

## Participantes principales

MCP define participantes con responsabilidades distintas. Entender esta separacion es clave para disenar buenos servidores MCP.

### Host

El host es la aplicacion donde ocurre la experiencia de IA.

Puede ser:

- Un editor de codigo.
- Una aplicacion de escritorio.
- Una herramienta de automatizacion.
- Un asistente interno de una empresa.

El host coordina la conversacion, gestiona permisos, decide que servidores estan disponibles y presenta los resultados al usuario.

El host no tiene por que saber como funciona Kubernetes, Terraform o Docker por dentro. Puede delegar esas capacidades en servidores MCP especializados.

### Client

El client MCP es el componente que mantiene una conexion con un servidor MCP.

Normalmente no lo usamos directamente como usuarios. Vive dentro del host y se encarga de:

- Inicializar la conexion.
- Negociar capacidades.
- Enviar requests al servidor.
- Recibir responses y notifications.
- Mantener la sesion aislada.

La idea importante es esta:

> Un host puede tener muchos clients MCP, pero cada client habla con un servidor MCP concreto.

### Server

El server MCP es el programa que expone capacidades al host.

Un servidor puede ejecutarse:

- Localmente, en la misma maquina que el host.
- Remotamente, como servicio accesible por red.

Un servidor MCP puede exponer, por ejemplo:

- Tools para ejecutar acciones.
- Resources para ofrecer contexto.
- Prompts para reutilizar flujos o instrucciones.

En DevOps, un servidor MCP podria especializarse en un dominio concreto, como Kubernetes, Terraform, Docker, observabilidad o CI/CD.

## Capas de MCP

MCP se puede entender como dos capas principales:

- Data layer.
- Transport layer.

Esta separacion es util porque el protocolo mantiene la misma idea de mensajes aunque cambie la forma en que esos mensajes viajan.

### Data layer

La data layer define que mensajes se intercambian entre client y server.

MCP usa JSON-RPC 2.0 como base para estructurar:

- Requests.
- Responses.
- Notifications.
- Errores.

Esta capa incluye conceptos como:

- Inicializacion de la conexion.
- Negociacion de version y capacidades.
- Listado de tools, resources y prompts.
- Ejecucion de tools.
- Lectura de resources.
- Obtencion de prompts.
- Notifications para cambios o progreso.

Cuando pensamos en que puede hacer un servidor MCP, normalmente estamos pensando en la data layer.

### Transport layer

La transport layer define como viajan los mensajes entre client y server.

MCP puede usar distintos transportes, por ejemplo:

- `stdio`, para procesos locales que se comunican por entrada y salida estandar.
- HTTP, para servidores remotos o integraciones accesibles por red.

El transporte no cambia el concepto principal del protocolo. Cambia el canal de comunicacion.

Una forma simple de verlo:

```text
Data layer:
  "tools/list", "tools/call", "resources/read"

Transport layer:
  stdio, HTTP u otro mecanismo soportado
```

## Ciclo de vida de una conexion

Una conexion MCP tiene ciclo de vida. No se trata solo de mandar un comando y recibir una respuesta.

El ciclo habitual tiene tres fases:

1. Inicializacion.
2. Operacion.
3. Cierre.

### Inicializacion

La inicializacion es la primera fase de una conexion MCP.

Durante esta fase, client y server intercambian informacion como:

- Version del protocolo.
- Capacidades soportadas.
- Informacion del client.
- Informacion del server.

Esto permite que ambas partes sepan que pueden usar y que no.

Por ejemplo, un servidor podria anunciar que soporta tools y resources, pero no prompts.

```text
Client ---- initialize ----> Server
Client <--- capabilities --- Server
Client ---- initialized ---> Server
```

Esta negociacion evita que el host intente usar funcionalidades que el servidor no ofrece.

### Operacion

La operacion es la fase normal de uso.

Durante esta fase, el client puede pedir al server que liste o use sus capacidades.

Ejemplos:

- Listar tools disponibles.
- Ejecutar una tool concreta.
- Listar resources disponibles.
- Leer un resource.
- Obtener un prompt.
- Recibir notifications.

Un flujo simple podria ser:

```text
Client ---- tools/list ----> Server
Client <--- tools --------- Server

Client ---- tools/call ----> Server
Client <--- result -------- Server
```

En DevOps, esto podria representar primero descubrir que herramientas ofrece un servidor y despues ejecutar una herramienta segura, como consultar logs o validar Terraform.

### Cierre

El cierre termina la conexion de forma ordenada.

Dependiendo del transporte, el cierre puede significar:

- Finalizar un proceso local.
- Cerrar una sesion.
- Terminar una conexion HTTP.
- Liberar recursos asociados.

Aunque muchas veces el cierre queda oculto por el SDK o por el host, sigue siendo parte del ciclo de vida del protocolo.

## Capacidades

Una capacidad indica que puede hacer una parte dentro de una conexion MCP.

Durante la inicializacion, client y server declaran las capacidades que soportan. Despues, durante la operacion, solo deberian usarse las capacidades negociadas.

Esto es importante porque MCP no asume que todos los servidores tengan todas las funcionalidades.

### Capacidades del servidor

Las capacidades mas comunes que expone un servidor MCP son:

- `tools`: funciones ejecutables que el modelo o el host pueden invocar.
- `resources`: informacion o contexto que se puede leer.
- `prompts`: plantillas reutilizables para tareas frecuentes.
- `logging`: mensajes de log enviados al client.

Ejemplo DevOps:

```text
Servidor MCP Kubernetes
  tools:
    - list_pods
    - get_pod_logs
    - describe_deployment

  resources:
    - cluster://namespaces
    - cluster://events

  prompts:
    - diagnose-failing-deployment
```

### Capacidades del cliente

El client tambien puede exponer capacidades.

Algunas capacidades del lado cliente permiten que el servidor pida ayuda al host o al usuario.

Ejemplos:

- `sampling`: permite al servidor pedir al host una respuesta generada por el modelo.
- `elicitation`: permite al servidor solicitar informacion adicional al usuario.
- `roots`: permite compartir directorios o raices de trabajo disponibles.

Estas capacidades son utiles, pero conviene tratarlas con cuidado. En DevOps, pedir confirmacion humana antes de una accion sensible puede ser mas importante que automatizarlo todo.

## Arquitectura local vs remota

Un servidor MCP puede ser local o remoto.

## Servidor local

Un servidor local se ejecuta en la misma maquina que el host.

Suele usar `stdio` como transporte.

Ejemplo:

```text
Host de IA
  |
  +-- MCP Client ---- proceso local: devops-mcp-server
```

Este enfoque es util cuando:

- El servidor necesita leer archivos locales.
- Queremos evitar exponer un servicio por red.
- Estamos desarrollando o probando.
- La integracion depende del entorno local del usuario.

## Servidor remoto

Un servidor remoto se ejecuta como servicio accesible por red.

Suele usar HTTP como transporte.

Ejemplo:

```text
Host de IA
  |
  +-- MCP Client ---- https://mcp.example.com
```

Este enfoque es util cuando:

- Varios usuarios necesitan usar el mismo servidor.
- El servidor se conecta a APIs corporativas.
- Queremos centralizar permisos, auditoria y configuracion.
- La integracion no depende de archivos locales.

## Ejemplo aplicado a DevOps

Imaginemos un asistente DevOps conectado a varios servidores MCP especializados.

```text
Asistente DevOps
  |
  +-- MCP Client ---- Servidor MCP Kubernetes
  |                     tools: list_pods, get_pod_logs
  |
  +-- MCP Client ---- Servidor MCP Terraform
  |                     tools: terraform_validate, terraform_plan_summary
  |
  +-- MCP Client ---- Servidor MCP Docker
  |                     tools: list_containers, get_container_logs
  |
  +-- MCP Client ---- Servidor MCP Observabilidad
                        resources: alerts, traces, metrics
```

Si el usuario pregunta:

> Revisa por que fallo el despliegue de la API.

El host podria usar varios servidores:

1. Consultar eventos de Kubernetes.
2. Leer logs de los pods afectados.
3. Revisar metricas o alertas.
4. Consultar informacion del ultimo pipeline.
5. Devolver un diagnostico con datos reales.

El valor de MCP esta en que cada servidor mantiene su propia responsabilidad, pero el host puede combinar el contexto.

## Idea clave

La arquitectura de MCP separa responsabilidades.

El host coordina la experiencia de IA. El client mantiene una conexion concreta. El server expone capacidades externas.

Gracias a esta separacion, podemos construir integraciones DevOps pequenas, especializadas y reutilizables sin acoplar toda la logica al asistente.
