# 06 - Transportes [EN](../en/06-transports.md)

## Proposito

Explicar que son los transportes MCP, como permiten comunicar clientes y servidores y cuando utilizar `stdio` o `Streamable HTTP`.

## Indice

- [Vision general](#vision-general)
- [Que es un transporte MCP](#que-es-un-transporte-mcp)
- [Como encaja en MCP](#como-encaja-en-mcp)
- [Transporte stdio](#transporte-stdio)
  - [Como funciona](#como-funciona)
  - [Ventajas](#ventajas)
  - [Limitaciones](#limitaciones)
  - [Ejemplo conceptual](#ejemplo-conceptual)
- [Streamable HTTP](#streamable-http)
  - [Como funciona](#como-funciona-1)
  - [Respuestas JSON y SSE](#respuestas-json-y-sse)
  - [Ventajas](#ventajas-1)
  - [Limitaciones](#limitaciones-1)
  - [Ejemplo conceptual](#ejemplo-conceptual-1)
- [stdio vs Streamable HTTP](#stdio-vs-streamable-http)
- [Transportes y seguridad](#transportes-y-seguridad)
  - [HTTPS y TLS](#https-y-tls)
  - [Autenticacion y autorizacion](#autenticacion-y-autorizacion)
  - [Seguridad local con stdio](#seguridad-local-con-stdio)
- [Eleccion del transporte](#eleccion-del-transporte)
- [Configuracion conceptual](#configuracion-conceptual)
- [Transportes personalizados](#transportes-personalizados)
- [Errores comunes](#errores-comunes)
- [Idea clave](#idea-clave)

---

## Vision general

Un transporte MCP define como se comunican un cliente y un servidor MCP.

El transporte se encarga de:

- Establecer el canal de comunicacion.
- Entregar los mensajes.
- Delimitar los mensajes.
- Transportar metadatos.
- Gestionar la cancelacion.
- Gestionar el cierre de la comunicacion.

El transporte no define el significado de las operaciones MCP.

Por ejemplo, estas operaciones siguen representando lo mismo:

```text
tools/list
tools/call
resources/list
resources/read
prompts/list
prompts/get
```

Lo que cambia es la forma en que esos mensajes viajan.

Una forma simple de verlo:

```text
MCP define el mensaje
  |
  v
El transporte define como viaja
  |
  v
El servidor procesa la operacion
  |
  v
El transporte devuelve la respuesta
```

Los transportes estandar actuales son:

- `stdio`.
- `Streamable HTTP`.

Tambien pueden existir transportes personalizados siempre que respeten las reglas fundamentales del protocolo.

## Que es un transporte MCP

Un transporte es el mecanismo que lleva los mensajes JSON-RPC entre el cliente y el servidor.

Por ejemplo:

```text
Client ---- mensaje JSON-RPC ----> Server
Client <--- respuesta JSON-RPC ---- Server
```

El mensaje podria representar:

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
}
```

El transporte no decide que significa `tools/list`.

Solo debe entregar correctamente ese mensaje al servidor y devolver la respuesta al cliente.

El protocolo MCP utiliza JSON-RPC para estructurar:

- Requests.
- Responses.
- Notifications.
- Errores.

Los mensajes deben transportarse utilizando una codificacion compatible, normalmente UTF-8.

## Como encaja en MCP

La arquitectura completa puede verse asi:

```text
Host
  |
  +-- MCP Client
        |
        +-- Transport
             |
             +-- MCP Server
```

El host utiliza un client para comunicarse con un servidor.

El client utiliza un transporte concreto:

```text
Host
  |
  +-- MCP Client ---- stdio ---- MCP Server local
```

O:

```text
Host
  |
  +-- MCP Client ---- HTTPS ---- MCP Server remoto
```

El transporte no es una tool ni un recurso.

```text
Tool:
  Ejecuta una accion.

Resource:
  Proporciona informacion.

Prompt:
  Estructura un flujo.

Transport:
  Lleva los mensajes entre client y server.
```

## Transporte stdio

`stdio` utiliza los streams estandar de entrada y salida de un proceso:

- `stdin`.
- `stdout`.
- `stderr`.

Normalmente, el client inicia el servidor MCP como un subproceso.

```text
MCP Client
  |
  +-- inicia el proceso MCP Server
        |
        +-- stdin: mensajes hacia el servidor
        +-- stdout: mensajes desde el servidor
        +-- stderr: logs del servidor
```

### Como funciona

El cliente inicia el servidor:

```text
Client ---- inicia proceso ----> Server
```

Despues, los mensajes JSON-RPC viajan por los streams:

```text
Client ---- stdin ----> Server
Client <--- stdout ---- Server
```

Cada mensaje debe ocupar una linea y estar delimitado por un salto de linea.

Ejemplo conceptual:

```text
stdin:

{"jsonrpc":"2.0","id":1,"method":"tools/list"}

stdout:

{"jsonrpc":"2.0","id":1,"result":{"tools":[]}}
```

El servidor puede escribir logs en `stderr`:

```text
stderr:

Starting DevOps MCP server
Loaded Kubernetes configuration
```

El servidor no debe escribir logs en `stdout`, porque el cliente espera encontrar unicamente mensajes MCP validos.

### Ventajas

`stdio` es adecuado cuando:

- El servidor se ejecuta localmente.
- El host puede iniciar el proceso.
- Solo un usuario o aplicacion necesita utilizarlo.
- No es necesario exponer un endpoint de red.
- Se busca una configuracion sencilla.
- Se quiere reducir la superficie de red.

Ventajas habituales:

- Configuracion sencilla.
- No requiere un puerto HTTP.
- No necesita TLS directamente.
- Buen rendimiento local.
- Facil de probar durante el desarrollo.
- Encaja bien con servidores personales o de escritorio.

### Limitaciones

`stdio` puede ser menos apropiado cuando:

- Varios usuarios necesitan el mismo servidor.
- El servidor debe ejecutarse en otra maquina.
- Se necesita un endpoint accesible por red.
- Se requiere autenticacion HTTP.
- Se quiere escalar el servidor como servicio independiente.
- Se necesita integrarlo con un gateway o balanceador.

Tambien hay que controlar correctamente:

- El ciclo de vida del proceso.
- La finalizacion inesperada.
- Los reinicios.
- La escritura accidental de logs en `stdout`.
- Los permisos del usuario que ejecuta el proceso.

### Ejemplo conceptual

Una configuracion local podria indicar:

```json
{
  "mcpServers": {
    "devops-local": {
      "command": "python",
      "args": [
        "/absolute/path/devops_server.py"
      ]
    }
  }
}
```

El host interpretaria esta configuracion de la siguiente manera:

```text
1. Iniciar el proceso indicado.
2. Conectarse a sus stdin y stdout.
3. Enviar mensajes MCP por stdin.
4. Leer respuestas MCP desde stdout.
5. Mostrar o utilizar los resultados.
```

El servidor no se ejecuta como un servicio de red publico.

---

## Streamable HTTP

`Streamable HTTP` utiliza HTTP para conectar clientes MCP con servidores accesibles por red.

El servidor expone un endpoint MCP, por ejemplo:

```text
https://mcp.example.com/mcp
```

El cliente envia cada mensaje JSON-RPC mediante una peticion `POST`.

```text
MCP Client ---- HTTP POST ----> MCP Server
MCP Client <--- JSON o SSE ----- MCP Server
```

`Streamable HTTP` sustituyo al antiguo transporte `HTTP+SSE` de versiones anteriores del protocolo.

### Como funciona

El servidor expone un endpoint:

```text
POST /mcp
```

El cliente envia una peticion JSON-RPC:

```http
POST /mcp HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2026-07-28
Mcp-Method: tools/list

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

El servidor puede responder con un objeto JSON:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": []
  }
}
```

Tambien puede responder con un flujo SSE cuando necesita enviar notificaciones relacionadas con la peticion:

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
```

### Respuestas JSON y SSE

Una respuesta JSON es adecuada cuando el servidor puede devolver el resultado directamente:

```text
Request
  |
  v
POST /mcp
  |
  v
JSON response
```

Un flujo SSE puede utilizarse cuando la respuesta necesita transmitir varios mensajes o notificaciones:

```text
Request
  |
  v
POST /mcp
  |
  v
SSE stream
  |
  +-- notification
  +-- progress
  +-- final response
```

En la especificacion actual, los flujos prolongados para notificaciones de cambios se obtienen mediante `subscriptions/listen`.

El servidor no debe utilizar un flujo SSE para enviar peticiones JSON-RPC independientes al cliente en el modelo actual.

### Ventajas

`Streamable HTTP` es adecuado cuando:

- El servidor es remoto.
- Varios clientes necesitan conectarse.
- El servidor debe funcionar como un servicio independiente.
- Se necesita autenticacion y autorizacion.
- Se requiere integracion con proxies o gateways.
- Se quiere desplegar el servidor en una infraestructura compartida.
- Se necesita observabilidad centralizada.

Ventajas habituales:

- Accesible por red.
- Compatible con infraestructura HTTP.
- Integrable con proxies y balanceadores.
- Permite aplicar autenticacion.
- Facilita el uso compartido.
- Puede desplegarse como servicio independiente.

### Limitaciones

`Streamable HTTP` requiere mas componentes y configuracion:

- Endpoint HTTP.
- Gestion de autenticacion.
- Validacion de origen.
- Configuracion de TLS.
- Control de timeouts.
- Gestion de proxies.
- Observabilidad.
- Limites de peticiones.
- Politicas de autorizacion.

Tambien hay que evitar exponer accidentalmente un servidor local en todas las interfaces de red.

Para un servidor local, es preferible escuchar en:

```text
127.0.0.1
```

En lugar de:

```text
0.0.0.0
```

Salvo que exista una razon concreta y controles de seguridad adecuados.

### Ejemplo conceptual

Un servidor remoto podria exponer:

```text
https://mcp.devops.example.com/mcp
```

El cliente enviaria:

```http
POST /mcp HTTP/1.1
Host: mcp.devops.example.com
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2026-07-28
Mcp-Method: tools/call
Mcp-Name: get_pod_logs
```
Con un cuerpo JSON-RPC como:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_pod_logs",
    "arguments": {
      "namespace": "staging",
      "pod": "api-123",
      "lines": 100
    },
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

Los nombres exactos de headers y metadatos dependen de la version de la especificacion implementada.

---

## stdio vs Streamable HTTP

| Caracteristica | `stdio` | `Streamable HTTP` |
|---|---|---|
| Uso habitual | Servidor local | Servidor remoto |
| Inicio | El client inicia el proceso | El servidor expone un endpoint |
| Canal | `stdin` y `stdout` | HTTP `POST` |
| Respuestas | JSON-RPC por linea | JSON o SSE |
| Cifrado | No utiliza TLS directamente | HTTPS/TLS recomendado |
| Autenticacion | Permisos del proceso y del sistema | Autenticacion y autorizacion HTTP |
| Usuarios | Normalmente uno | Varios posibles |
| Complejidad | Baja | Mayor |
| Escalabilidad | Local | Servicio compartido |
| Ejemplo | MCP local para Docker | MCP remoto para Kubernetes |

La eleccion depende principalmente del despliegue:

```text
Desarrollo local:
  stdio

Servidor compartido:
  Streamable HTTP

Servidor remoto corporativo:
  Streamable HTTP + HTTPS + autenticacion
```

Un servidor puede implementar:

- Solo `stdio`.
- Solo `Streamable HTTP`.
- Ambos transportes.

La eleccion del transporte no cambia las herramientas, recursos o prompts que el servidor ofrece.

---

## Transportes y seguridad

El transporte no proporciona automaticamente toda la seguridad necesaria.

La seguridad depende de varias capas:

```text
MCP
  |
  +-- JSON-RPC
        |
        +-- Transporte
              |
              +-- Seguridad del canal
                    |
                    +-- Autenticacion
                    +-- Autorizacion
                    +-- Validacion de entradas
```

### HTTPS y TLS

HTTPS protege el canal HTTP mediante TLS.

```text
MCP Client ---- HTTPS/TLS ----> MCP Server
```

TLS ayuda a proteger:

- La confidencialidad de los mensajes.
- La integridad de los datos.
- La identidad del servidor mediante certificados.
- Las credenciales durante el transporte.

- Pero HTTPS no decide:

  - Que usuario puede utilizar una herramienta.
  - Que namespaces puede consultar.
  - Que operaciones puede ejecutar.
  - Si una accion requiere confirmacion.

Por eso HTTPS debe combinarse con autenticacion y autorizacion.

### Autenticacion y autorizacion

En un servidor remoto, conviene definir:

- Como se identifica el cliente.
- Como se validan las credenciales.
- Que permisos tiene cada usuario.
- Que recursos puede consultar.
- Que herramientas puede ejecutar.
- Que acciones necesitan confirmacion.

Ejemplo conceptual:

```text
Usuario
  |
  v
Cliente MCP presenta credenciales
  |
  v
Servidor valida autenticacion
  |
  v
Servidor comprueba autorizacion
  |
  v
Servidor procesa la peticion
```

La autenticacion responde:

> ¿Quien eres?

La autorizacion responde:

> ¿Que puedes hacer?

Un token valido no deberia conceder acceso ilimitado.

### Seguridad local con stdio

Aunque `stdio` no exponga un endpoint HTTP, sigue necesitando seguridad.

Hay que controlar:

- Quien puede iniciar el proceso.
- Con que usuario se ejecuta.
- Que variables de entorno recibe.
- Que archivos puede leer.
- Que comandos puede ejecutar.
- Que permisos tiene sobre Docker, Kubernetes o Terraform.
- Que secretos estan disponibles.

Por ejemplo, un servidor local que recibe acceso al socket Docker puede tener permisos muy amplios aunque utilice `stdio`.

El transporte local no convierte automaticamente las operaciones en seguras.

---

## Eleccion del transporte

Una guia practica podria ser:

```text
¿El servidor se ejecuta en la misma maquina que el host?
  |
  +-- Si --> ¿El host puede iniciar el proceso?
                |
                +-- Si --> stdio
                +-- No --> Streamable HTTP local o remoto

¿Varios clientes necesitan acceder al servidor?
  |
  +-- Si --> Streamable HTTP

¿El servidor se despliega como servicio corporativo?
  |
  +-- Si --> Streamable HTTP + HTTPS + autenticacion

¿Estas construyendo el primer prototipo?
  |
  +-- Si --> Empieza con stdio
```

Para el servidor DevOps de este proyecto, una progresion razonable seria:

1. Implementar `stdio`.
2. Crear herramientas de lectura.
3. Probar el servidor localmente.
4. Añadir recursos y prompts.
5. Validar permisos y errores.
6. Añadir `Streamable HTTP`.
7. Incorporar autenticacion.
8. Probar el despliegue remoto.

## Configuracion conceptual

Configuracion local con `stdio`:

```json
{
  "mcpServers": {
    "devops-local": {
      "command": "python",
      "args": [
        "/absolute/path/devops-mcp-server.py"
      ]
    }
  }
}
```

Configuracion conceptual para un servidor remoto:

```json
{
  "mcpServers": {
    "devops-remote": {
      "url": "https://mcp.devops.example.com/mcp"
    }
  }
}
```

La configuracion real depende del host MCP utilizado.

Estos ejemplos muestran la diferencia principal:

```text
stdio:
  El host conoce como iniciar el proceso.

Streamable HTTP:
  El host conoce la URL del endpoint.
```

La configuracion no deberia incluir secretos directamente dentro del archivo.

Es preferible utilizar:

- Variables de entorno.
- Gestores de secretos.
- Credenciales del sistema.
- Identidades gestionadas.
- Configuracion segura del host.

## Transportes personalizados

MCP permite implementar transportes personalizados.

Un transporte personalizado podria utilizar:

- Unix domain sockets.
- TCP.
- Un sistema de mensajeria.
- Una plataforma interna.
- Otro canal bidireccional compatible.

Sin embargo, debe conservar:

- El formato JSON-RPC.
- Las reglas de mensajes.
- Los metadatos requeridos.
- La correlacion de respuestas.
- La cancelacion.
- El cierre correcto.
- La interoperabilidad entre el client y server.

Un transporte personalizado no deberia inventar una semantica diferente para `tools/call` o `resources/read`.

Su funcion es cambiar el canal, no cambiar el significado del protocolo.

---

## Errores comunes

- Confundir transportes con tools.
- Pensar que HTTPS es el transporte MCP completo.
- Escribir logs de `stdio` en `stdout`.
- Exponer un servidor HTTP local en `0.0.0.0` sin necesidad.
- No utilizar HTTPS en servidores remotos.
- No validar el header `Origin`.
- No implementar autenticacion.
- Conceder permisos excesivos al proceso local.
- Compartir secretos dentro de configuraciones.
- Suponer que un transporte seguro hace segura cualquier tool.
- Utilizar el transporte antiguo `HTTP+SSE` en una implementacion nueva.
- No controlar la cancelacion de peticiones.
- No gestionar correctamente el cierre del proceso.
- No probar el transporte con el host real.

## Idea clave

Un transporte MCP define como viajan los mensajes entre el client y el server.

No define las tools, resources o prompts.

```text
stdio:
  Comunicacion local mediante stdin y stdout.

Streamable HTTP:
  Comunicacion remota mediante HTTP POST y respuestas JSON o SSE.

HTTPS/TLS:
  Protege el canal HTTP, pero no sustituye la autenticacion ni la autorizacion.
```

Para comenzar un servidor DevOps, `stdio` suele ser el transporte mas sencillo.

Cuando el servidor necesita ser remoto, compartido o desplegado como servicio, `Streamable HTTP` es normalmente la opcion adecuada.

La estructura de este capitulo se basa en la especificacion oficial de transportes MCP, que define `stdio`, `Streamable HTTP`, la cancelacion, los metadatos por peticion y la posibilidad de crear transportes personalizados.
