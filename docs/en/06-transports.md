# 06 - Transports [ES](../es/06-transportes.md)

## Purpose

Explain what MCP transports are, how they connect clients and servers, and when to use `stdio` or `Streamable HTTP`.

## Table of contents

- [Overview](#overview)
- [What is an MCP transport](#what-is-an-mcp-transport)
- [How it fits into MCP](#how-it-fits-into-mcp)
- [stdio transport](#stdio-transport)
  - [How it works](#how-it-works)
  - [Advantages](#advantages)
  - [Limitations](#limitations)
  - [Conceptual example](#conceptual-example)
- [Streamable HTTP](#streamable-http)
  - [How it works](#how-it-works-1)
  - [JSON and SSE responses](#json-and-sse-responses)
  - [Advantages](#advantages-1)
  - [Limitations](#limitations-1)
  - [Conceptual example](#conceptual-example-1)
- [stdio vs Streamable HTTP](#stdio-vs-streamable-http)
- [Transports and security](#transports-and-security)
  - [HTTPS and TLS](#https-and-tls)
  - [Authentication and authorization](#authentication-and-authorization)
  - [Local security with stdio](#local-security-with-stdio)
- [Choosing a transport](#choosing-a-transport)
- [Conceptual configuration](#conceptual-configuration)
- [Custom transports](#custom-transports)
- [Common mistakes](#common-mistakes)
- [Key idea](#key-idea)

---

## Overview

An MCP transport defines how an MCP client and server communicate.

The transport is responsible for:

- Establishing the communication channel.
- Delivering messages.
- Framing messages.
- Carrying metadata.
- Managing cancellation.
- Managing communication shutdown.

The transport does not define the meaning of MCP operations.

For example, these operations still represent the same thing:

```text
tools/list
tools/call
resources/list
resources/read
prompts/list
prompts/get
```

What changes is how those messages travel.

A simple way to see it:

```text
MCP defines the message
  |
  v
The transport defines how it travels
  |
  v
The server processes the operation
  |
  v
The transport returns the response
```

The current standard transports are:

- `stdio`.
- `Streamable HTTP`.

Custom transports can also exist as long as they respect the protocol's fundamental rules.

## What is an MCP transport

A transport is the mechanism that carries JSON-RPC messages between the client and the server.

For example:

```text
Client ---- JSON-RPC message ----> Server
Client <--- JSON-RPC response ---- Server
```

The message could represent:

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
}
```

The transport does not decide what `tools/list` means.

It only needs to deliver the message correctly to the server and return the response to the client.

The MCP protocol uses JSON-RPC to structure:

- Requests.
- Responses.
- Notifications.
- Errors.

Messages must be transported using a compatible encoding, normally UTF-8.

## How it fits into MCP

The complete architecture can be represented as follows:

```text
Host
  |
  +-- MCP Client
        |
        +-- Transport
             |
             +-- MCP Server
```

The host uses a client to communicate with a server.

The client uses a specific transport:

```text
Host
  |
  +-- MCP Client ---- stdio ---- local MCP Server
```

Or:

```text
Host
  |
  +-- MCP Client ---- HTTPS ---- remote MCP Server
```

The transport is not a tool or a resource.

```text
Tool:
  Executes an action.

Resource:
  Provides information.

Prompt:
  Structures a workflow.

Transport:
  Carries messages between the client and server.
```

## stdio transport

`stdio` uses a process's standard input and output streams:

- `stdin`.
- `stdout`.
- `stderr`.

Normally, the client starts the MCP server as a subprocess.

```text
MCP Client
  |
  +-- starts the MCP Server process
        |
        +-- stdin: messages to the server
        +-- stdout: messages from the server
        +-- stderr: server logs
```

### How it works

The client starts the server:

```text
Client ---- starts process ----> Server
```

JSON-RPC messages then travel through the streams:

```text
Client ---- stdin ----> Server
Client <--- stdout ---- Server
```

Each message must occupy one line and be delimited by a newline.

Conceptual example:

```text
stdin:

{"jsonrpc":"2.0","id":1,"method":"tools/list"}

stdout:

{"jsonrpc":"2.0","id":1,"result":{"tools":[]}}
```

The server can write logs to `stderr`:

```text
stderr:

Starting DevOps MCP server
Loaded Kubernetes configuration
```

The server must not write logs to `stdout`, because the client expects that stream to contain only valid MCP messages.

### Advantages

`stdio` is suitable when:

- The server runs locally.
- The host can start the process.
- Only one user or application needs to use it.
- There is no need to expose a network endpoint.
- A simple configuration is desired.
- The network attack surface should be reduced.

Common advantages:

- Simple configuration.
- No HTTP port required.
- No direct TLS requirement.
- Good local performance.
- Easy to test during development.
- Well suited to personal or desktop servers.

### Limitations

`stdio` may be less appropriate when:

- Several users need the same server.
- The server must run on another machine.
- A network-accessible endpoint is required.
- HTTP authentication is required.
- The server should scale as an independent service.
- It needs to integrate with a gateway or load balancer.

The following also need to be controlled correctly:

- Process lifecycle.
- Unexpected termination.
- Restarts.
- Accidental log output to `stdout`.
- Permissions of the user running the process.

### Conceptual example

A local configuration might specify:

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

The host would interpret this configuration as follows:

```text
1. Start the specified process.
2. Connect to its stdin and stdout.
3. Send MCP messages through stdin.
4. Read MCP responses from stdout.
5. Display or use the results.
```

The server does not run as a public network service.

---

## Streamable HTTP

`Streamable HTTP` uses HTTP to connect MCP clients with network-accessible servers.

The server exposes an MCP endpoint, for example:

```text
https://mcp.example.com/mcp
```

The client sends each JSON-RPC message using an HTTP `POST` request.

```text
MCP Client ---- HTTP POST ----> MCP Server
MCP Client <--- JSON or SSE ---- MCP Server
```

`Streamable HTTP` replaced the older `HTTP+SSE` transport from earlier protocol versions.

### How it works

The server exposes an endpoint:

```text
POST /mcp
```

The client sends a JSON-RPC request:

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

The server can respond with a JSON object:

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

It can also respond with an SSE stream when it needs to send notifications related to the request:

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
```

### JSON and SSE responses

A JSON response is suitable when the server can return the result directly:

```text
Request
  |
  v
POST /mcp
  |
  v
JSON response
```

An SSE stream can be used when the response needs to transmit several messages or notifications:

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

In the current specification, long-lived streams for change notifications are obtained through `subscriptions/listen`.

In the current model, the server must not use an SSE stream to send independent JSON-RPC requests to the client.

### Advantages

`Streamable HTTP` is suitable when:

- The server is remote.
- Several clients need to connect.
- The server must run as an independent service.
- Authentication and authorization are required.
- Integration with proxies or gateways is needed.
- The server will be deployed on shared infrastructure.
- Centralized observability is needed.

Common advantages:

- Network accessible.
- Compatible with HTTP infrastructure.
- Integrates with proxies and load balancers.
- Supports authentication.
- Facilitates shared use.
- Can be deployed as an independent service.

### Limitations

`Streamable HTTP` requires more components and configuration:

- HTTP endpoint.
- Authentication management.
- Origin validation.
- TLS configuration.
- Timeout control.
- Proxy management.
- Observability.
- Request limits.
- Authorization policies.

You must also avoid accidentally exposing a local server on every network interface.

For a local server, it is preferable to listen on:

```text
127.0.0.1
```

Instead of:

```text
0.0.0.0
```

Unless there is a specific reason and appropriate security controls.

### Conceptual example

A remote server might expose:

```text
https://mcp.devops.example.com/mcp
```

The client would send:

```http
POST /mcp HTTP/1.1
Host: mcp.devops.example.com
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2026-07-28
Mcp-Method: tools/call
Mcp-Name: get_pod_logs
```

With a JSON-RPC body such as:

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

The exact header and metadata names depend on the implemented specification version.

---

## stdio vs Streamable HTTP

| Feature | `stdio` | `Streamable HTTP` |
|---|---|---|
| Typical use | Local server | Remote server |
| Startup | Client starts the process | Server exposes an endpoint |
| Channel | `stdin` and `stdout` | HTTP `POST` |
| Responses | JSON-RPC per line | JSON or SSE |
| Encryption | Does not use TLS directly | HTTPS/TLS recommended |
| Authentication | Process and system permissions | HTTP authentication and authorization |
| Users | Usually one | Potentially many |
| Complexity | Low | Higher |
| Scalability | Local | Shared service |
| Example | Local Docker MCP | Remote Kubernetes MCP |

The choice mainly depends on the deployment model:

```text
Local development:
  stdio

Shared server:
  Streamable HTTP

Corporate remote server:
  Streamable HTTP + HTTPS + authentication
```

A server can implement:

- Only `stdio`.
- Only `Streamable HTTP`.
- Both transports.

The transport choice does not change the tools, resources, or prompts offered by the server.

---

## Transports and security

The transport does not automatically provide all the required security.

Security depends on several layers:

```text
MCP
  |
  +-- JSON-RPC
        |
        +-- Transport
              |
              +-- Channel security
                    |
                    +-- Authentication
                    +-- Authorization
                    +-- Input validation
```

### HTTPS and TLS

HTTPS protects the HTTP channel through TLS.

```text
MCP Client ---- HTTPS/TLS ----> MCP Server
```

TLS helps protect:

- Message confidentiality.
- Data integrity.
- Server identity through certificates.
- Credentials while in transit.

- But HTTPS does not decide:

  - Which user can use a tool.
  - Which namespaces can be queried.
  - Which operations can be executed.
  - Whether an action requires confirmation.

That is why HTTPS must be combined with authentication and authorization.

### Authentication and authorization

For a remote server, it is useful to define:

- How the client is identified.
- How credentials are validated.
- Which permissions each user has.
- Which resources can be queried.
- Which tools can be executed.
- Which actions require confirmation.

Conceptual example:

```text
User
  |
  v
MCP Client presents credentials
  |
  v
Server validates authentication
  |
  v
Server checks authorization
  |
  v
Server processes the request
```

Authentication answers:

> Who are you?

Authorization answers:

> What are you allowed to do?

A valid token should not grant unlimited access.

### Local security with stdio

Although `stdio` does not expose an HTTP endpoint, it still requires security.

You must control:

- Who can start the process.
- Which user runs it.
- Which environment variables it receives.
- Which files it can read.
- Which commands it can execute.
- Which permissions it has over Docker, Kubernetes, or Terraform.
- Which secrets are available to it.

For example, a local server with access to the Docker socket may have very broad permissions even when it uses `stdio`.

The local transport does not automatically make operations safe.

---

## Choosing a transport

A practical guide could be:

```text
Does the server run on the same machine as the host?
  |
  +-- Yes --> Can the host start the process?
                |
                +-- Yes --> stdio
                +-- No --> Local or remote Streamable HTTP

Do several clients need to access the server?
  |
  +-- Yes --> Streamable HTTP

Will the server be deployed as a corporate service?
  |
  +-- Yes --> Streamable HTTP + HTTPS + authentication

Are you building the first prototype?
  |
  +-- Yes --> Start with stdio
```

For this project's DevOps server, a reasonable progression would be:

1. Implement `stdio`.
2. Create read-only tools.
3. Test the server locally.
4. Add resources and prompts.
5. Validate permissions and errors.
6. Add `Streamable HTTP`.
7. Add authentication.
8. Test the remote deployment.

## Conceptual configuration

Local configuration with `stdio`:

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

Conceptual configuration for a remote server:

```json
{
  "mcpServers": {
    "devops-remote": {
      "url": "https://mcp.devops.example.com/mcp"
    }
  }
}
```

The actual configuration depends on the MCP host being used.

These examples show the main difference:

```text
stdio:
  The host knows how to start the process.

Streamable HTTP:
  The host knows the endpoint URL.
```

Configuration should not include secrets directly in the file.

It is preferable to use:

- Environment variables.
- Secret managers.
- System credentials.
- Managed identities.
- Secure host configuration.

## Custom transports

MCP allows custom transports to be implemented.

A custom transport could use:

- Unix domain sockets.
- TCP.
- A messaging system.
- An internal platform.
- Another compatible bidirectional channel.

However, it must preserve:

- The JSON-RPC format.
- Message rules.
- Required metadata.
- Response correlation.
- Cancellation.
- Correct shutdown.
- Interoperability between client and server.

A custom transport should not invent different semantics for `tools/call` or `resources/read`.

Its purpose is to change the channel, not the meaning of the protocol.

---

## Common mistakes

- Confusing transports with tools.
- Thinking that HTTPS is the complete MCP transport.
- Writing `stdio` logs to `stdout`.
- Exposing a local HTTP server on `0.0.0.0` without need.
- Not using HTTPS for remote servers.
- Failing to validate the `Origin` header.
- Failing to implement authentication.
- Granting excessive permissions to the local process.
- Sharing secrets inside configuration files.
- Assuming that a secure transport makes every tool safe.
- Using the old `HTTP+SSE` transport in a new implementation.
- Failing to control request cancellation.
- Failing to manage process shutdown correctly.
- Not testing the transport with the real host.

## Key idea

An MCP transport defines how messages travel between the client and server.

It does not define the tools, resources, or prompts.

```text
stdio:
  Local communication through stdin and stdout.

Streamable HTTP:
  Remote communication through HTTP POST and JSON or SSE responses.

HTTPS/TLS:
  Protects the HTTP channel but does not replace authentication or authorization.
```

To start a DevOps server, `stdio` is usually the simplest transport.

When the server needs to be remote, shared, or deployed as a service, `Streamable HTTP` is usually the appropriate option.

The structure of this chapter is based on the official MCP transport specification, which defines `stdio`, `Streamable HTTP`, cancellation, per-request metadata, and the possibility of creating custom transports.
