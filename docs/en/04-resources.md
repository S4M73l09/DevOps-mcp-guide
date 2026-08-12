# 04 - Resources [ES](../es/04-recursos.md)

## Purpose

Explain how to use resources to expose queryable information from an MCP server.

## Table of contents

- [Overview](#overview)
- [What is a resource](#what-is-a-resource)
- [How a resource works](#how-a-resource-works)
  - [Discovery](#discovery)
  - [Reading](#reading)
  - [Content and metadata](#content-and-metadata)
- [Resource vs tool](#resource-vs-tool)
- [Resource URIs](#resource-uris)
  - [Static resources](#static-resources)
  - [Resource templates](#resource-templates)
- [Types of information](#types-of-information)
  - [Files](#files)
  - [Configurations](#configurations)
  - [Logs](#logs)
  - [Service state](#service-state)
  - [Schemas and documentation](#schemas-and-documentation)
- [Resources applied to DevOps](#resources-applied-to-devops)
  - [Kubernetes](#kubernetes)
  - [Terraform](#terraform)
  - [CI/CD](#cicd)
  - [Observability](#observability)
- [Updates and subscriptions](#updates-and-subscriptions)
- [Security](#security)
- [Common mistakes](#common-mistakes)
- [Key idea](#key-idea)

---

## Overview

In MCP, a resource is a source of information exposed by a server so that an application can query it and use it as context.

A resource can represent:

- A file.
- A configuration.
- A database schema.
- A set of logs.
- The state of a service.
- An API response.
- Metrics or alerts.
- Technical documentation.

Unlike a tool, a resource does not primarily represent an action for the model to execute.

A simple way to see it:

```text
The MCP server exposes information
  |
  v
The client discovers the available resources
  |
  v
The application selects a resource
  |
  v
The client requests its contents
  |
  v
The application adds the information as context
```

## What is a resource

A resource is a data source uniquely identified by a URI.

Simple examples:

```text
file:///project/README.md
kubernetes://cluster/namespaces
terraform://projects/platform/state
ci://pipelines/api/recent-runs
observability://services/api/alerts
```

The MCP server can obtain the content from different systems:

- File systems.
- Kubernetes.
- Terraform.
- Docker.
- CI/CD platforms.
- Databases.
- Internal APIs.
- Observability systems.

A resource does not have to be a physical file. It can be a structured representation of information obtained from an external system.

## How a resource works

Resources usually follow this flow:

1. The server exposes the available resources.
2. The client discovers those resources.
3. The application selects one or more resources.
4. The client requests their contents.
5. The server returns the data and metadata.
6. The application decides how to use that information.

The protocol defines operations such as:

```text
resources/list
resources/read
resources/templates/list
```

The host or application can decide whether to show resources in a list, explorer, search interface, or any other UI.

### Discovery

To discover the available resources, the client can request their list.

Conceptual example:

```text
Client ---- resources/list ----> Server
Client <--- resource metadata --- Server
```

The server might return:

```json
{
    "resources": [
      {
        "uri": "kubernetes://namespaces/staging/pods",
        "name": "staging-pods",
        "description": "Pods available in the staging namespace",
        "mimeType": "application/json"
      }
    ]
}
```

The list does not have to include all resource contents. It usually provides the information needed to identify the resource and decide whether it should be read.

### Reading

When the application needs the contents of a resource, the client requests them using the URI.

```text
Client ---- resources/read ----> Server
Client <--- resource contents --- Server
```

Example:

```json
{
    "uri": "kubernetes://namespaces/staging/pods"
}
```

The server might return:

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

The application can decide whether to send all the content to the model, select part of it, or transform it before using it.

### Content and metadata

A resource can include content and metadata.

Common metadata includes:

- URI.
- Name.
- Description.
- MIME type.
- Size.
- Modification date.
- Audience information.
- Priority.

Example:

```json
{
  "uri": "terraform://projects/platform/configuration",
  "name": "platform-configuration",
  "description": "Terraform configuration for the platform project",
  "mimeType": "text/plain",
  "text": "..."
}
```

Metadata helps the application decide how to present, filter, or use the resource.

---

## Resource vs tool

Resources and tools can work together, but they have different responsibilities.

| Element | Tool | Resource |
|---|---|---|
| Purpose | Execute an action | Provide information |
| Main control | Model or application | Application |
| Identification | Tool name | Resource URI |
| Input | Structured arguments | URI or parameterized URI |
| Result | Operation result | Data or context |
| Effects | May modify systems | Usually read-only |
| Example | `get_pod_logs(...)` | `kubernetes://pods/api/logs` |

Example with Kubernetes:

```text
Tool:
  get_pod_logs(namespace, pod, lines)

Resource:
  kubernetes://namespaces/staging/pods/api/logs
```

The tool represents an operation that can be executed with parameters.

The resource represents information that the application can query and use as context.

A simple rule:

> If the main idea is to do something, it is probably a tool. If the main idea is to query something, it is probably a resource.

## Resource URIs

Each resource should have a URI that identifies it clearly.

A well-designed URI should be:

- Predictable.
- Specific.
- Stable.
- Easy to document.
- Safe to validate.

Examples:

```text
kubernetes://clusters/dev/namespaces/api/pods
terraform://projects/platform/modules
ci://pipelines/backend/runs/latest
observability://services/api/alerts
```

The URI should not automatically allow access to any resource in the system.

### Static resources

A static resource represents a specific source.

Examples:

```text
file:///project/README.md
kubernetes://clusters/dev/nodes
terraform://projects/platform/configuration
```

The URI always points to the same type of information, although the content may change over time.

### Resource templates

A resource template defines a parameterized URI.

Example:

```text
kubernetes://clusters/{cluster}/namespaces/{namespace}/pods
```

A concrete URI could be:

```text
kubernetes://clusters/dev/namespaces/staging/pods
```

Another example:

```text
observability://services/{service}/alerts
```

Which could be used as:

```text
observability://services/api/alerts
```

Templates make it possible to represent multiple related resources without manually defining every URI.

Parameters must be validated before they are used.

A parameterized URI should not be allowed to access unauthorized paths, namespaces, or projects.

---

## Types of information

### Files

An MCP server can expose files or documents as resources.

Examples:

```text
file:///project/README.md
file:///project/docs/deployment.md
file:///projects/terraform/main.tf
```

In DevOps, they can be useful for:

- Consulting deployment documentation.
- Reading configurations.
- Reviewing manifests.
- Consulting runbooks.
- Analyzing Terraform files.

### Configurations

A resource can represent the current configuration of a system.

Examples:

```text
kubernetes://clusters/dev/configuration
terraform://projects/platform/configuration
docker://compose/backend/configuration
```

It is important to separate configurations that can be exposed from those that contain:

- Passwords.
- Tokens.
- Private keys.
- Sensitive variables.
- Internal information.

### Logs

Logs can be exposed as resources when the main goal is to query information.

Examples:

```text
kubernetes://namespaces/staging/pods/api/logs
docker://containers/api/logs
ci://pipelines/backend/jobs/test/logs
```

Logs should have clear limits:

- Maximum number of lines.
- Time range.
- Maximum size.
- Allowed filters.
- Secret redaction.

If querying logs requires many parameters or a complex operation, a tool may be more appropriate.

### Service state

A resource can represent the current state of a service or platform.

Examples:

```text
kubernetes://clusters/production/health
ci://pipelines/backend/status
observability://services/api/health
```

This type of information can help the model understand the context before using a tool.

For example, before restarting a service, the application could first query its current state.

### Schemas and documentation

Resources can also provide reference information.

Examples:

```text
database://schemas/production
terraform://projects/platform/modules
api://services/orders/openapi
docs://runbooks/deployment
```

These resources can help the assistant:

- Understand the structure of a database.
- Learn which modules are available.
- Consult API contracts.
- Follow operational procedures.
- Explain an architecture.

---

## Resources applied to DevOps

### Kubernetes

Examples:

```text
kubernetes://clusters/dev/nodes
kubernetes://clusters/dev/namespaces
kubernetes://namespaces/staging/pods
kubernetes://namespaces/production/events
```

They can be used to query:

- Active pods.
- Available nodes.
- Recent events.
- Deployment status.
- Namespace configuration.

Good practices:

- Limit clusters and namespaces.
- Do not expose Kubernetes secrets.
- Limit the number of returned objects.
- Filter sensitive information.
- Apply permissions according to the environment.

### Terraform

Examples:

```text
terraform://projects/platform/configuration
terraform://projects/platform/modules
terraform://projects/platform/plan-summary
terraform://projects/platform/state
```

Terraform resources can provide:

- Declared configuration.
- Used modules.
- A plan summary.
- Resource state.
- Drift information.

Terraform state may contain **highly sensitive** data. It should not be exposed without access controls and filtering.

### CI/CD

Examples:

```text
ci://pipelines/backend/status
ci://pipelines/backend/recent-runs
ci://pipelines/backend/deployments
ci://pipelines/backend/jobs/test/logs
```

These resources can help query:

- Pipeline status.
- Recent runs.
- Deployment history.
- Job logs.
- Available artifacts.

Job tokens, protected variables, and secrets should never be part of the returned content.

### Observability

Examples:

```text
observability://services/api/health
observability://services/api/metrics
observability://services/api/alerts
observability://services/api/incidents
```

They can provide:

- Service status.
- Recent metrics.
- Active alerts.
- Open incidents.
- Trace summaries.

It is useful to limit:

- Time ranges.
- Number of series.
- Query cost.
- Result size.
- Information sent to the model.

---

## Updates and subscriptions

Some resources can change over time.

For example:

- The state of a deployment.
- Active alerts.
- The pods in a namespace.
- The state of a pipeline.
- The logs of a container.

The server can notify the client that the list of resources has changed or that a specific resource has been updated.

Conceptual flow:

```text
The resource changes
  |
  v
The server sends a notification
  |
  v
The client receives the update
  |
  v
The application decides whether to read the resource again
```

Subscriptions are useful when the application needs to react to changes, but they are not always necessary.

For a simple integration, reading the resource again when the user requests it may be enough.

## Security

Resources can expose sensitive information.

Recommended principles:

- Validate all URIs.
- Apply access controls.
- Limit the resources available to each user.
- Prevent directory traversal in file-based resources.
- Do not return secrets.
- Limit response size.
- Filter logs before returning them.
- Separate development, staging, and production environments.
- Audit access to sensitive information.
- Validate all resource template parameters.

A good question to ask before exposing a resource is:

> If this content reaches the model, what is the worst possible outcome?

If the answer includes leaking credentials, revealing internal information, or exposing production data, the resource needs stronger controls.

## Best practices

- Use clear and predictable URIs.
- Keep one responsibility per resource.
- Describe the content accurately.
- Include a MIME type when useful.
- Limit the volume of data.
- Prefer read-only information.
- Separate public, internal, and sensitive data.
- Use templates only when they add value.
- Validate the parameters of every template.
- Document the update frequency.
- Explain whether the content may contain sensitive data.
- Use tools when there is an action to execute.

## Common mistakes

- Using a resource to execute commands.
- Exposing an overly generic URI.
- Allowing arbitrary access to paths.
- Returning unlimited logs.
- Exposing secrets in configurations.
- Mixing data from different environments without identifying them.
- Confusing a resource with a tool.
- Creating templates without validating their parameters.
- Failing to limit large responses.
- Failing to control access to production data.
- Failing to document the content format.

Bad design example:

```text
resource://anything/{path}
```

Problems:

- It may allow access to unintended paths.
- It is difficult to audit.
- It may facilitate directory traversal.
- It does not make clear what information it exposes.

Better design:

```text
terraform://projects/{project}/configuration
```

With validations such as:

```text
project:
  - platform
  - payments
  - identity
```

---

## Key idea

An MCP resource provides context and information in a structured way.

It is not an open door to the system and it is not a replacement for tools.

A tool executes an action.

A resource exposes information that the application can query, filter, and use to better understand the context.

In DevOps, resources allow the assistant to understand the state of systems before explaining problems or suggesting actions.

The structure of this chapter is based on the current `resources/list`, `resources/read`, and `resources/templates/list` operations, as well as the URIs and subscriptions defined by the official MCP specification. ([Official Resources specification](https://modelcontextprotocol.io/specification/2026-07-28/server/resources))
