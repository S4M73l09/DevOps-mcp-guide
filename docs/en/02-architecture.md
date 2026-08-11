# 02 - Architecture [ES](../es/02-arquitectura.md)

## Purpose

Explain how MCP is organized internally: participants, layers, connection lifecycle, and the capabilities each side can expose.

## Table of Contents

- [Overview](#overview)
- [Main Participants](#main-participants)
  - [Host](#host)
  - [Client](#client)
  - [Server](#server)
- [MCP Layers](#mcp-layers)
  - [Data Layer](#data-layer)
  - [Transport Layer](#transport-layer)
- [Connection Lifecycle](#connection-lifecycle)
  - [Initialization](#initialization)
  - [Operation](#operation)
  - [Shutdown](#shutdown)
- [Capabilities](#capabilities)
  - [Server Capabilities](#server-capabilities)
  - [Client Capabilities](#client-capabilities)
- [Local vs Remote Architecture](#local-vs-remote-architecture)
- [DevOps Example](#devops-example)
- [Key Idea](#key-idea)

## Overview

MCP follows a client-server architecture, but with three important concepts: host, client, and server.

The host is the AI application. The client is the concrete MCP connection that lives inside the host. The server is the program that exposes external capabilities.

A simple way to look at it:

```text
User
  |
  v
AI Host
  |
  +-- MCP Client ---- MCP Server
```

In a real integration, the host can connect to several MCP servers at the same time. For each server, the host creates an independent MCP client.

```text
AI Host
  |
  +-- MCP Client ---- Git MCP Server
  |
  +-- MCP Client ---- Kubernetes MCP Server
  |
  +-- MCP Client ---- Terraform MCP Server
```

This separation allows each MCP server to have a concrete responsibility while the host can compose capabilities from several systems.

## Main Participants

MCP defines participants with different responsibilities. Understanding this separation is key to designing good MCP servers.

### Host

The host is the application where the AI experience happens.

It can be:

- A code editor.
- A desktop application.
- An automation tool.
- An internal company assistant.

The host coordinates the conversation, manages permissions, decides which servers are available, and presents results to the user.

The host does not need to know how Kubernetes, Terraform, or Docker work internally. It can delegate those capabilities to specialized MCP servers.

### Client

The MCP client is the component that maintains a connection with an MCP server.

As users, we usually do not interact with it directly. It lives inside the host and is responsible for:

- Initializing the connection.
- Negotiating capabilities.
- Sending requests to the server.
- Receiving responses and notifications.
- Keeping the session isolated.

The important idea is:

> A host can have many MCP clients, but each client talks to one specific MCP server.

### Server

The MCP server is the program that exposes capabilities to the host.

A server can run:

- Locally, on the same machine as the host.
- Remotely, as a network-accessible service.

An MCP server can expose, for example:

- Tools to execute actions.
- Resources to provide context.
- Prompts to reuse flows or instructions.

In DevOps, an MCP server could specialize in a concrete domain, such as Kubernetes, Terraform, Docker, observability, or CI/CD.

## MCP Layers

MCP can be understood as two main layers:

- Data layer.
- Transport layer.

This separation is useful because the protocol keeps the same message model even when the way those messages travel changes.

### Data Layer

The data layer defines which messages are exchanged between client and server.

MCP uses JSON-RPC 2.0 as the basis for structuring:

- Requests.
- Responses.
- Notifications.
- Errors.

This layer includes concepts such as:

- Connection initialization.
- Version and capability negotiation.
- Listing tools, resources, and prompts.
- Executing tools.
- Reading resources.
- Retrieving prompts.
- Notifications for changes or progress.

When we think about what an MCP server can do, we are usually thinking about the data layer.

### Transport Layer

The transport layer defines how messages travel between client and server.

MCP can use different transports, for example:

- `stdio`, for local processes that communicate through standard input and output.
- HTTP, for remote servers or network-accessible integrations.

The transport does not change the main concept of the protocol. It changes the communication channel.

A simple way to look at it:

```text
Data layer:
  "tools/list", "tools/call", "resources/read"

Transport layer:
  stdio, HTTP, or another supported mechanism
```

## Connection Lifecycle

An MCP connection has a lifecycle. It is not just about sending a command and receiving a response.

The usual lifecycle has three phases:

1. Initialization.
2. Operation.
3. Shutdown.

### Initialization

Initialization is the first phase of an MCP connection.

During this phase, client and server exchange information such as:

- Protocol version.
- Supported capabilities.
- Client information.
- Server information.

This allows both sides to know what they can and cannot use.

For example, a server might announce that it supports tools and resources, but not prompts.

```text
Client ---- initialize ----> Server
Client <--- capabilities --- Server
Client ---- initialized ---> Server
```

This negotiation prevents the host from trying to use features that the server does not offer.

### Operation

Operation is the normal usage phase.

During this phase, the client can ask the server to list or use its capabilities.

Examples:

- List available tools.
- Execute a specific tool.
- List available resources.
- Read a resource.
- Retrieve a prompt.
- Receive notifications.

A simple flow could be:

```text
Client ---- tools/list ----> Server
Client <--- tools --------- Server

Client ---- tools/call ----> Server
Client <--- result -------- Server
```

In DevOps, this could represent first discovering which tools a server offers and then executing a safe tool, such as querying logs or validating Terraform.

### Shutdown

Shutdown ends the connection in an orderly way.

Depending on the transport, shutdown can mean:

- Ending a local process.
- Closing a session.
- Terminating an HTTP connection.
- Releasing associated resources.

Although shutdown is often hidden by the SDK or the host, it is still part of the protocol lifecycle.

## Capabilities

A capability indicates what one side can do within an MCP connection.

During initialization, client and server declare the capabilities they support. Later, during operation, only negotiated capabilities should be used.

This matters because MCP does not assume every server has every feature.

### Server Capabilities

The most common capabilities exposed by an MCP server are:

- `tools`: executable functions that the model or host can invoke.
- `resources`: information or context that can be read.
- `prompts`: reusable templates for frequent tasks.
- `logging`: log messages sent to the client.

DevOps example:

```text
Kubernetes MCP Server
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

### Client Capabilities

The client can also expose capabilities.

Some client-side capabilities allow the server to ask the host or user for help.

Examples:

- `sampling`: allows the server to ask the host for a model-generated response.
- `elicitation`: allows the server to request additional information from the user.
- `roots`: allows the client to share available working directories or roots.

These capabilities are useful, but they should be treated carefully. In DevOps, human confirmation before a sensitive action can matter more than automating everything.

## Local vs Remote Architecture

An MCP server can be local or remote.

## Local Server

A local server runs on the same machine as the host.

It usually uses `stdio` as the transport.

Example:

```text
AI Host
  |
  +-- MCP Client ---- local process: devops-mcp-server
```

This approach is useful when:

- The server needs to read local files.
- We want to avoid exposing a network service.
- We are developing or testing.
- The integration depends on the user's local environment.

## Remote Server

A remote server runs as a network-accessible service.

It usually uses HTTP as the transport.

Example:

```text
AI Host
  |
  +-- MCP Client ---- https://mcp.example.com
```

This approach is useful when:

- Several users need to use the same server.
- The server connects to corporate APIs.
- We want to centralize permissions, auditing, and configuration.
- The integration does not depend on local files.

## DevOps Example

Imagine a DevOps assistant connected to several specialized MCP servers.

```text
DevOps Assistant
  |
  +-- MCP Client ---- Kubernetes MCP Server
  |                     tools: list_pods, get_pod_logs
  |
  +-- MCP Client ---- Terraform MCP Server
  |                     tools: terraform_validate, terraform_plan_summary
  |
  +-- MCP Client ---- Docker MCP Server
  |                     tools: list_containers, get_container_logs
  |
  +-- MCP Client ---- Observability MCP Server
                        resources: alerts, traces, metrics
```

If the user asks:

> Check why the API deployment failed.

The host could use several servers:

1. Query Kubernetes events.
2. Read logs from the affected pods.
3. Review metrics or alerts.
4. Query information from the latest pipeline.
5. Return a diagnosis based on real data.

The value of MCP is that each server keeps its own responsibility, while the host can combine the context.

## Key Idea

MCP architecture separates responsibilities.

The host coordinates the AI experience. The client maintains a concrete connection. The server exposes external capabilities.

Thanks to this separation, we can build small, specialized, and reusable DevOps integrations without coupling all the logic to the assistant.
