# 07 - Seguridad [EN](../en/07-security.md)

## Proposito

Definir criterios de seguridad para servidores MCP, especialmente cuando ejecutan tareas DevOps sensibles.

## Indice

- [Introduccion](#introduccion)
- [Modelo de amenazas](#modelo-de-amenazas)
- [Principios de seguridad](#principios-de-seguridad)
  - [Menor privilegio](#menor-privilegio)
  - [Consentimiento y control](#consentimiento-y-control)
  - [Separacion de responsabilidades](#separacion-de-responsabilidades)
- [Validacion de entradas](#validacion-de-entradas)
- [Control de comandos](#control-de-comandos)
- [Herramientas de lectura y escritura](#herramientas-de-lectura-y-escritura)
- [Autenticacion y autorizacion](#autenticacion-y-autorizacion)
  - [stdio](#stdio)
  - [HTTP remoto](#http-remoto)
  - [Permisos por herramienta](#permisos-por-herramienta)
- [Manejo de secretos](#manejo-de-secretos)
- [Seguridad de los transportes](#seguridad-de-los-transportes)
- [Auditoria y trazabilidad](#auditoria-y-trazabilidad)
- [Errores y fallos](#errores-y-fallos)
- [Checklist de seguridad](#checklist-de-seguridad)
- [Ejemplo de politica para DevOps](#ejemplo-de-politica-para-devops)
- [Idea clave](#idea-clave)

---

## Introduccion

MCP permite que una aplicacion basada en un modelo de lenguaje acceda a datos y ejecute herramientas externas. En DevOps, esas herramientas pueden consultar logs, inspeccionar recursos, modificar despliegues o eliminar infraestructura.

Por tanto, un servidor MCP no debe tratarse como una simple capa de integracion. Debe tratarse como un servicio con capacidad operativa y con los mismos controles que aplicariamos a cualquier sistema que ejecuta acciones sobre infraestructura.

La seguridad debe contemplar todas las capas:

```text
Host
  |
  +-- MCP Client
        |
        +-- Transporte
              |
              +-- MCP Server
                    |
                    +-- Herramientas
                          |
                          +-- Docker, Kubernetes, Terraform o cloud
```

MCP define el protocolo de comunicacion, pero no convierte automaticamente una herramienta peligrosa en una herramienta segura. El host, el cliente, el servidor y la infraestructura externa deben aplicar sus propios controles.

La especificacion actual destaca tres ideas principales:

- El usuario debe conservar el control sobre los datos y las operaciones.
- El acceso a datos debe respetar el consentimiento y los permisos correspondientes.
- Las herramientas deben tratarse con precaucion porque pueden representar ejecucion arbitraria de codigo.

## Modelo de amenazas

Antes de implementar controles, conviene identificar que puede salir mal.

### Servidor comprometido

Un atacante podria modificar el servidor MCP para ejecutar acciones distintas de las documentadas, devolver datos sensibles o usar las credenciales disponibles en el entorno.

### Cliente o usuario con permisos excesivos

Un cliente correctamente autenticado sigue siendo peligroso si sus credenciales permiten leer todos los secretos, modificar produccion o eliminar recursos sin restricciones.

### Entradas manipuladas

Los argumentos de una herramienta pueden contener rutas, nombres de recursos, comandos o filtros controlados por un usuario o por contenido externo. No deben considerarse confiables solo porque procedan de un cliente MCP.

### Informacion no confiable en el contexto

Logs, issues, manifests y respuestas de otras herramientas pueden contener instrucciones diseñadas para influir en el modelo. El servidor debe validar las operaciones en su propio codigo y no delegar la seguridad en las instrucciones recibidas.

### Exposicion de secretos

Los secretos pueden filtrarse mediante:

- Respuestas de herramientas.
- Recursos MCP.
- Mensajes de error.
- Logs del servidor.
- Variables de entorno expuestas.
- Ficheros de configuracion.

### Operaciones destructivas

Una herramienta que ejecuta `delete`, `apply`, `destroy`, `scale` o `rollback` puede causar una interrupcion aunque la peticion sea tecnicamente valida.

## Principios de seguridad

### Menor privilegio

Cada proceso, usuario, token y herramienta debe tener unicamente los permisos necesarios para su funcion.

Ejemplos:

- Un servidor de consulta de Kubernetes deberia usar permisos de solo lectura.
- Una herramienta de logs no necesita acceso al socket de Docker.
- Una herramienta de Terraform no deberia recibir automaticamente credenciales de produccion.
- Una herramienta de despliegue deberia limitarse a namespaces, cuentas o proyectos concretos.
- El servidor no deberia ejecutarse como administrador salvo que sea estrictamente necesario.

Una matriz sencilla puede ayudar a revisar los permisos:

| Componente | Acceso recomendado | Acceso que debe evitarse |
|---|---|---|
| `get_pod_logs` | Leer logs de namespaces autorizados | Eliminar pods o leer secretos |
| `list_workloads` | Leer deployments y pods | Modificar replicas |
| `terraform_plan` | Leer configuracion y generar un plan | Aplicar cambios automaticamente |
| `terraform_apply` | Permiso separado y confirmacion | Usar credenciales globales |
| `delete_resource` | Recursos y entornos limitados | Acceso general al cluster |

### Consentimiento y control

Las operaciones deben ser comprensibles para la persona que las autoriza. Antes de una accion sensible conviene mostrar:

- Herramienta que se ejecutara.
- Recurso afectado.
- Entorno afectado.
- Cambios esperados.
- Identidad utilizada.
- Posibilidad de cancelar.

El consentimiento de una herramienta no debe interpretarse como consentimiento permanente para cualquier operacion futura. Las acciones de alto riesgo pueden requerir una confirmacion nueva.

### Separacion de responsabilidades

No conviene concentrar todas las capacidades en una unica herramienta generica como:

```text
run_shell(command: string)
```

Es preferible exponer operaciones concretas:

```text
get_pod_logs(namespace, pod, lines)
list_deployments(namespace)
terraform_plan(workspace)
restart_deployment(namespace, name)
```

Las herramientas concretas permiten validar mejor los argumentos, revisar permisos y auditar las operaciones.

## Validacion de entradas

Toda entrada recibida por una herramienta debe validarse antes de llegar a la infraestructura.

La validacion deberia comprobar:

- Tipo de dato.
- Longitud maxima.
- Formato permitido.
- Valores validos.
- Relaciones entre parametros.
- Entorno permitido.
- Permisos del solicitante.

Por ejemplo, una herramienta para consultar logs podria aceptar:

```json
{
  "namespace": "staging",
  "pod": "api-123",
  "lines": 100
}
```

Pero deberia rechazar:

- Un numero de lineas negativo o excesivo.
- Un namespace fuera de la lista autorizada.
- Un nombre de pod con caracteres no permitidos.
- Un parametro adicional que cambie el comando interno.

La validacion debe realizarse en el servidor, aunque el esquema de entrada ya exista en `tools/list`. El esquema ayuda al cliente, pero no sustituye la validacion del servidor.

## Control de comandos

Un servidor MCP de DevOps no deberia aceptar comandos de shell arbitrarios:

```text
run_shell("kubectl delete namespace production")
```

Este diseño dificulta:

- Limitar permisos.
- Validar argumentos.
- Auditar la accion.
- Predecir el impacto.
- Evitar inyecciones de comandos.

Cuando sea necesario ejecutar un proceso, conviene:

- Usar una lista de ejecutables permitidos.
- Pasar los argumentos como valores separados.
- No construir comandos mediante concatenacion de strings.
- Establecer un timeout.
- Limitar el tamaño de la salida.
- Controlar la cancelacion.
- Ejecutar con un usuario restringido.
- Registrar el resultado sin incluir secretos.

Un modelo conceptual mas seguro seria:

```text
Herramienta especifica
  |
  +-- Valida argumentos
  |
  +-- Comprueba permisos
  |
  +-- Construye una operacion permitida
  |
  +-- Ejecuta con timeout y limites
  |
  +-- Registra el resultado
```

## Herramientas de lectura y escritura

Separar las herramientas de lectura de las herramientas que cambian el estado reduce el riesgo y facilita la autorizacion.

| Tipo | Ejemplo | Control recomendado |
|---|---|---|
| Lectura | `list_pods` | Permisos de solo lectura |
| Lectura | `get_pod_logs` | Limitar namespace y cantidad de datos |
| Analisis | `terraform_plan` | No aplicar cambios automaticamente |
| Escritura | `scale_deployment` | Permiso especifico y confirmacion |
| Destructiva | `delete_resource` | Bloqueo por defecto o aprobacion reforzada |
| Destructiva | `terraform_destroy` | Separacion de credenciales y doble control |

Las operaciones de escritura deberian indicar claramente su alcance. Por ejemplo, no es suficiente mostrar `delete_resource`; deberia quedar identificado el tipo de recurso, el nombre, el namespace y el entorno.

Para acciones destructivas pueden aplicarse controles adicionales:

- Confirmacion humana explicita.
- Requerir una razon o ticket de cambio.
- Permitir solo entornos no productivos.
- Exigir un modo de previsualizacion.
- Aplicar una ventana temporal.
- Usar una lista de recursos protegidos.
- Requerir una segunda aprobacion.

## Autenticacion y autorizacion

La autenticacion responde a la pregunta:

> Quien eres?

La autorizacion responde a:

> Que puedes hacer?

Un usuario autenticado no debe recibir automaticamente acceso a todas las herramientas.

La especificacion MCP `2026-07-28` define capacidades de autorizacion en la capa de transporte para servidores HTTP protegidos. La autorizacion es opcional para una implementacion MCP, pero las implementaciones HTTP que la utilicen deberian seguir la especificacion oficial.

### stdio

En `stdio`, el servidor suele ser un proceso local iniciado por el host. La especificacion de autorizacion HTTP no debe aplicarse directamente a este transporte.

Los controles habituales son:

- Usuario que inicia el proceso.
- Permisos del sistema operativo.
- Variables de entorno disponibles.
- Ficheros que puede leer.
- Socket de Docker al que puede acceder.
- Contexto de Kubernetes seleccionado.
- Credenciales disponibles en el entorno.

El hecho de que el servidor sea local no significa que sea seguro por defecto. Un proceso local con acceso al socket de Docker puede tener capacidad equivalente a privilegios muy amplios sobre el sistema.

### HTTP remoto

Un servidor HTTP remoto puede necesitar autenticacion y autorizacion mediante OAuth. En ese caso, deben controlarse como minimo:

- Almacenamiento seguro de tokens.
- Expiracion y renovacion de credenciales.
- Uso de HTTPS.
- Validacion del destinatario del token.
- No incluir tokens en la URL.
- Scopes minimos para cada operacion.
- Respuestas correctas para errores `401` y `403`.

Los tokens deben enviarse en la cabecera de autorizacion:

```http
Authorization: Bearer <access-token>
```

No deben incluirse en la query string:

```text
https://mcp.example.com/mcp?token=secret
```

El servidor debe validar que el token fue emitido para ese servidor y no aceptar ni reenviar tokens destinados a otro recurso.

### Permisos por herramienta

Cuando sea posible, los permisos deben dividirse por capacidad:

```text
devops:pods:read
devops:logs:read
devops:deployments:write
devops:terraform:plan
devops:terraform:apply
```

Los permisos de lectura no deberian implicar permisos de escritura. Para una operacion concreta, el servidor debe volver a comprobar los permisos usando los argumentos recibidos.

## Manejo de secretos

Los secretos no deben aparecer en:

- Codigo fuente.
- Repositorios.
- Ficheros de configuracion versionados.
- Esquemas de herramientas.
- Prompts.
- Recursos MCP publicos.
- Mensajes de error.
- Logs.

Es preferible utilizar:

- Variables de entorno controladas.
- Gestores de secretos.
- Identidades administradas.
- Credenciales temporales.
- Permisos de sistema de archivos.
- Rotacion automatica.

Tambien es necesario evitar devolver secretos indirectamente. Por ejemplo, una herramienta que ejecuta un comando no deberia devolver sin filtrar toda su salida si puede contener tokens o variables sensibles.

Antes de registrar una peticion, conviene aplicar redaccion de datos:

```text
Antes:  Authorization: Bearer eyJ...
Despues: Authorization: Bearer [REDACTED]
```

## Seguridad de los transportes

La seguridad del transporte no sustituye a la seguridad de las herramientas.

### stdio

En `stdio`:

- `stdout` debe contener unicamente mensajes MCP validos.
- Los logs deben escribirse en `stderr`.
- El proceso debe ejecutarse con permisos limitados.
- El ciclo de vida y los reinicios deben estar controlados.
- Las variables de entorno deben revisarse.

### Streamable HTTP

En `Streamable HTTP`:

- Debe utilizarse HTTPS fuera de entornos locales controlados.
- El servidor debe validar el encabezado `Origin`.
- Un servidor local no deberia escuchar en `0.0.0.0` sin una razon concreta.
- Deben limitarse tamaño de peticiones, tiempo de ejecucion y conexiones.
- Los proxies no deben registrar credenciales.
- Las respuestas de error no deben revelar informacion interna.

El transporte puede proteger la comunicacion, pero no decide si una identidad puede eliminar un recurso de produccion.

## Auditoria y trazabilidad

Las operaciones sensibles deben dejar una traza suficiente para investigar lo ocurrido.

Un registro puede incluir:

- Fecha y hora.
- Identidad del usuario o servicio.
- Herramienta ejecutada.
- Recurso y entorno afectados.
- Resultado de la autorizacion.
- Duracion.
- Resultado de la operacion.
- Identificador de correlacion.

No deberia incluir:

- Tokens.
- Contraseñas.
- Claves privadas.
- Contenido completo de secretos.
- Variables de entorno sin filtrar.

Ejemplo conceptual:

```json
{
  "request_id": "req-123",
  "actor": "operator@example.com",
  "tool": "scale_deployment",
  "environment": "staging",
  "resource": "api",
  "authorized": true,
  "result": "success"
}
```

La auditoria debe protegerse contra modificaciones no autorizadas y debe tener una politica de retencion coherente con el entorno.

## Errores y fallos

Un error no debe convertir una operacion fallida en una operacion parcialmente ejecutada sin control.

El servidor deberia:

- Validar antes de modificar el estado.
- Usar operaciones idempotentes cuando sea posible.
- Establecer timeouts.
- Cancelar procesos que superen sus limites.
- Diferenciar errores de validacion, autenticacion, autorizacion y ejecucion.
- Evitar reintentos automaticos de acciones destructivas.
- No revelar rutas, tokens o configuraciones internas.
- Dejar constancia de las operaciones interrumpidas.

Una respuesta de error util no necesita revelar todos los detalles internos:

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "The requested operation is not allowed for this environment."
  }
}
```

Los detalles tecnicos pueden registrarse internamente con controles adecuados, pero no deben exponerse automaticamente al cliente.

## Checklist de seguridad

Antes de utilizar un servidor MCP DevOps, conviene comprobar:

- [ ] El proceso usa el principio de menor privilegio.
- [ ] Las herramientas de lectura y escritura estan separadas.
- [ ] No existe una herramienta de shell arbitrario sin controles estrictos.
- [ ] Todas las entradas se validan en el servidor.
- [ ] Hay limites de tiempo, tamaño y salida.
- [ ] Los secretos no estan en el codigo ni en la configuracion versionada.
- [ ] Los tokens se almacenan y transmiten de forma segura.
- [ ] Las herramientas destructivas requieren autorizacion adicional.
- [ ] Las peticiones sensibles quedan auditadas.
- [ ] Los logs no contienen credenciales.
- [ ] `stdio` mantiene `stdout` limpio.
- [ ] HTTP utiliza HTTPS y valida `Origin`.
- [ ] El servidor no escucha publicamente sin necesidad.
- [ ] Se han probado errores, cancelaciones y permisos insuficientes.
- [ ] Existe una forma clara de revocar credenciales.

## Ejemplo de politica para DevOps

Una politica inicial para un servidor de aprendizaje podria ser:

```text
Permitido:
  - Listar pods en staging.
  - Consultar logs de staging.
  - Listar deployments.
  - Generar planes de Terraform.

Requiere confirmacion:
  - Reiniciar un deployment.
  - Modificar replicas.
  - Aplicar un plan de Terraform.

Bloqueado por defecto:
  - Leer secretos.
  - Acceder a produccion.
  - Ejecutar shell arbitrario.
  - Eliminar namespaces.
  - Ejecutar terraform destroy.
```

Esta politica debe adaptarse al entorno real. No se debe copiar directamente a produccion sin revisar identidades, recursos, permisos, registros y procedimientos de aprobacion.

## Idea clave

La seguridad de un servidor MCP DevOps no depende de una unica medida.

```text
Transporte seguro
  + permisos minimos
  + entradas validadas
  + secretos protegidos
  + autorizacion por capacidad
  + confirmacion de acciones sensibles
  + auditoria
  = sistema mas controlable
```

MCP proporciona un protocolo para conectar aplicaciones, datos y herramientas, pero la implementacion debe decidir que puede hacer cada identidad y bajo que condiciones.

La especificacion actual y sus requisitos concretos deben revisarse antes de desplegar un servidor, especialmente cuando se utilizan transportes HTTP y autorizacion OAuth.

Fuentes principales:

- [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP Authorization 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
