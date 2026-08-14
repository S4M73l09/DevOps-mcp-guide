# 07 - Security [ES](../es/07-seguridad.md)

## Purpose

Define security criteria for MCP servers, especially when they execute sensitive DevOps tasks.

## Table of contents

- [Introduction](#introduction)
- [Threat model](#threat-model)
- [Security principles](#security-principles)
  - [Least privilege](#least-privilege)
  - [Consent and control](#consent-and-control)
  - [Separation of responsibilities](#separation-of-responsibilities)
- [Input validation](#input-validation)
- [Command control](#command-control)
- [Read and write tools](#read-and-write-tools)
- [Authentication and authorization](#authentication-and-authorization)
  - [stdio](#stdio)
  - [Remote HTTP](#remote-http)
  - [Per-tool permissions](#per-tool-permissions)
- [Secrets handling](#secrets-handling)
- [Transport security](#transport-security)
- [Auditing and traceability](#auditing-and-traceability)
- [Errors and failures](#errors-and-failures)
- [Security checklist](#security-checklist)
- [Example DevOps policy](#example-devops-policy)
- [Key idea](#key-idea)

---

## Introduction

MCP allows an application based on a language model to access data and execute external tools. In DevOps, those tools may inspect logs, examine resources, modify deployments, or delete infrastructure.

Therefore, an MCP server should not be treated as a simple integration layer. It should be treated as a service with operational capabilities and with the same controls applied to any system that executes actions against infrastructure.

Security must cover every layer:

```text
Host
  |
  +-- MCP Client
        |
        +-- Transport
              |
              +-- MCP Server
                    |
                    +-- Tools
                          |
                          +-- Docker, Kubernetes, Terraform, or cloud
```

MCP defines the communication protocol, but it does not automatically make a dangerous tool safe. The host, client, server, and external infrastructure must apply their own controls.

The current specification highlights three main ideas:

- The user must retain control over data and operations.
- Access to data must respect consent and the corresponding permissions.
- Tools must be treated carefully because they can represent arbitrary code execution.

## Threat model

Before implementing controls, it is useful to identify what could go wrong.

### Compromised server

An attacker could modify the MCP server to execute actions different from those documented, return sensitive data, or use credentials available in the environment.

### Client or user with excessive permissions

A correctly authenticated client is still dangerous if its credentials allow it to read every secret, modify production, or delete resources without restrictions.

### Manipulated inputs

Tool arguments may contain paths, resource names, commands, or filters controlled by a user or by external content. They must not be considered trusted merely because they come from an MCP client.

### Untrusted information in context

Logs, issues, manifests, and responses from other tools may contain instructions designed to influence the model. The server must validate operations in its own code and must not delegate security to received instructions.

### Secret exposure

Secrets can leak through:

- Tool responses.
- MCP resources.
- Error messages.
- Server logs.
- Exposed environment variables.
- Configuration files.

### Destructive operations

A tool that executes `delete`, `apply`, `destroy`, `scale`, or `rollback` may cause an outage even when the request is technically valid.

## Security principles

### Least privilege

Every process, user, token, and tool should have only the permissions required for its function.

Examples:

- A Kubernetes query server should use read-only permissions.
- A logs tool does not need access to the Docker socket.
- A Terraform tool should not automatically receive production credentials.
- A deployment tool should be limited to specific namespaces, accounts, or projects.
- The server should not run as an administrator unless strictly necessary.

A simple matrix can help review permissions:

| Component | Recommended access | Access to avoid |
|---|---|---|
| `get_pod_logs` | Read logs from authorized namespaces | Delete pods or read secrets |
| `list_workloads` | Read deployments and pods | Modify replica counts |
| `terraform_plan` | Read configuration and generate a plan | Apply changes automatically |
| `terraform_apply` | Separate permission and confirmation | Use global credentials |
| `delete_resource` | Limited resources and environments | General cluster access |

### Consent and control

Operations should be understandable to the person authorizing them. Before a sensitive action, it is useful to show:

- The tool that will be executed.
- The affected resource.
- The affected environment.
- Expected changes.
- The identity being used.
- The option to cancel.

Consent for one tool must not be interpreted as permanent consent for every future operation. High-risk actions may require a new confirmation.

### Separation of responsibilities

It is not advisable to concentrate every capability in one generic tool such as:

```text
run_shell(command: string)
```

Specific operations are preferable:

```text
get_pod_logs(namespace, pod, lines)
list_deployments(namespace)
terraform_plan(workspace)
restart_deployment(namespace, name)
```

Specific tools make it easier to validate arguments, review permissions, and audit operations.

## Input validation

Every input received by a tool must be validated before it reaches the infrastructure.

Validation should check:

- Data type.
- Maximum length.
- Allowed format.
- Valid values.
- Relationships between parameters.
- Allowed environment.
- Requester's permissions.

For example, a logs tool might accept:

```json
{
  "namespace": "staging",
  "pod": "api-123",
  "lines": 100
}
```

But it should reject:

- A negative or excessive number of lines.
- A namespace outside the authorized list.
- A pod name with disallowed characters.
- An additional parameter that changes the internal command.

Validation must happen on the server, even when an input schema already exists in `tools/list`. The schema helps the client, but it does not replace server-side validation.

## Command control

An MCP DevOps server should not accept arbitrary shell commands:

```text
run_shell("kubectl delete namespace production")
```

This design makes it difficult to:

- Limit permissions.
- Validate arguments.
- Audit the action.
- Predict the impact.
- Prevent command injection.

When executing a process is necessary, it is preferable to:

- Use a list of allowed executables.
- Pass arguments as separate values.
- Avoid building commands through string concatenation.
- Set a timeout.
- Limit output size.
- Control cancellation.
- Run with a restricted user.
- Record the result without including secrets.

A safer conceptual model would be:

```text
Specific tool
  |
  +-- Validate arguments
  |
  +-- Check permissions
  |
  +-- Build an allowed operation
  |
  +-- Execute with timeout and limits
  |
  +-- Record the result
```

## Read and write tools

Separating read tools from tools that change state reduces risk and makes authorization easier.

| Type | Example | Recommended control |
|---|---|---|
| Read | `list_pods` | Read-only permissions |
| Read | `get_pod_logs` | Limit namespace and amount of data |
| Analysis | `terraform_plan` | Do not apply changes automatically |
| Write | `scale_deployment` | Specific permission and confirmation |
| Destructive | `delete_resource` | Block by default or require stronger approval |
| Destructive | `terraform_destroy` | Separate credentials and dual control |

Write operations should clearly state their scope. For example, showing only `delete_resource` is not enough; the resource type, name, namespace, and environment should be identified.

Additional controls can be applied to destructive actions:

- Explicit human confirmation.
- Require a reason or change ticket.
- Allow only non-production environments.
- Require a preview mode.
- Apply a time window.
- Use a protected-resource list.
- Require a second approval.

## Authentication and authorization

Authentication answers:

> Who are you?

Authorization answers:

> What are you allowed to do?

An authenticated user should not automatically receive access to every tool.

The MCP `2026-07-28` specification defines authorization capabilities at the transport layer for protected HTTP servers. Authorization is optional for an MCP implementation, but HTTP implementations that use it should follow the official specification.

### stdio

With `stdio`, the server is usually a local process started by the host. The HTTP authorization specification should not be applied directly to this transport.

Common controls include:

- User starting the process.
- Operating system permissions.
- Available environment variables.
- Files it can read.
- Docker socket access.
- Selected Kubernetes context.
- Credentials available in the environment.

The fact that the server is local does not make it safe by default. A local process with access to the Docker socket may have very broad permissions over the system.

### Remote HTTP

A remote HTTP server may need authentication and authorization through OAuth. At a minimum, the following should be controlled:

- Secure token storage.
- Credential expiration and renewal.
- HTTPS usage.
- Validation of the token's intended audience.
- No tokens in URLs.
- Minimum scopes for each operation.
- Correct responses for `401` and `403` errors.

Tokens should be sent in the authorization header:

```http
Authorization: Bearer <access-token>
```

They should not be included in the query string:

```text
https://mcp.example.com/mcp?token=secret
```

The server must validate that the token was issued for that server and must not accept or forward tokens intended for another resource.

### Per-tool permissions

When possible, permissions should be divided by capability:

```text
devops:pods:read
devops:logs:read
devops:deployments:write
devops:terraform:plan
devops:terraform:apply
```

Read permissions should not imply write permissions. For a specific operation, the server must check permissions again using the received arguments.

## Secrets handling

Secrets should not appear in:

- Source code.
- Repositories.
- Versioned configuration files.
- Tool schemas.
- Prompts.
- Public MCP resources.
- Error messages.
- Logs.

It is preferable to use:

- Controlled environment variables.
- Secret managers.
- Managed identities.
- Temporary credentials.
- File system permissions.
- Automatic rotation.

It is also necessary to avoid returning secrets indirectly. For example, a tool that runs a command should not return all of its output without filtering if it may contain tokens or sensitive variables.

Before recording a request, data redaction should be applied:

```text
Before:  Authorization: Bearer eyJ...
After:   Authorization: Bearer [REDACTED]
```

## Transport security

Transport security does not replace tool security.

### stdio

With `stdio`:

- `stdout` must contain only valid MCP messages.
- Logs must be written to `stderr`.
- The process must run with limited permissions.
- Lifecycle and restarts must be controlled.
- Environment variables must be reviewed.

### Streamable HTTP

With `Streamable HTTP`:

- HTTPS should be used outside controlled local environments.
- The server must validate the `Origin` header.
- A local server should not listen on `0.0.0.0` without a specific reason.
- Request size, execution time, and connections should be limited.
- Proxies must not log credentials.
- Error responses must not reveal internal information.

The transport can protect communication, but it does not decide whether an identity may delete a production resource.

## Auditing and traceability

Sensitive operations should leave enough trace data to investigate what happened.

A record may include:

- Date and time.
- User or service identity.
- Executed tool.
- Affected resource and environment.
- Authorization result.
- Duration.
- Operation result.
- Correlation identifier.

It should not include:

- Tokens.
- Passwords.
- Private keys.
- Complete secret contents.
- Unfiltered environment variables.

Conceptual example:

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

Audit data should be protected against unauthorized modification and should have a retention policy appropriate for the environment.

## Errors and failures

An error should not turn a failed operation into an uncontrolled partially completed operation.

The server should:

- Validate before changing state.
- Use idempotent operations when possible.
- Set timeouts.
- Cancel processes that exceed their limits.
- Distinguish validation, authentication, authorization, and execution errors.
- Avoid automatic retries for destructive actions.
- Avoid revealing internal paths, tokens, or configuration.
- Record interrupted operations.

A useful error response does not need to reveal every internal detail:

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "The requested operation is not allowed for this environment."
  }
}
```

Technical details can be recorded internally with appropriate controls, but they should not be exposed automatically to the client.

## Security checklist

Before using a DevOps MCP server, check that:

- [ ] The process follows the principle of least privilege.
- [ ] Read and write tools are separated.
- [ ] There is no arbitrary shell tool without strict controls.
- [ ] All inputs are validated by the server.
- [ ] Time, size, and output limits exist.
- [ ] Secrets are not in code or versioned configuration.
- [ ] Tokens are stored and transmitted securely.
- [ ] Destructive tools require additional authorization.
- [ ] Sensitive requests are audited.
- [ ] Logs contain no credentials.
- [ ] `stdio` keeps `stdout` clean.
- [ ] HTTP uses HTTPS and validates `Origin`.
- [ ] The server does not listen publicly without need.
- [ ] Errors, cancellations, and insufficient permissions have been tested.
- [ ] There is a clear way to revoke credentials.

## Example DevOps policy

An initial policy for a learning server could be:

```text
Allowed:
  - List pods in staging.
  - Query staging logs.
  - List deployments.
  - Generate Terraform plans.

Requires confirmation:
  - Restart a deployment.
  - Change replica counts.
  - Apply a Terraform plan.

Blocked by default:
  - Read secrets.
  - Access production.
  - Execute arbitrary shell commands.
  - Delete namespaces.
  - Run terraform destroy.
```

This policy must be adapted to the real environment. It should not be copied directly to production without reviewing identities, resources, permissions, logs, and approval procedures.

## Key idea

The security of a DevOps MCP server does not depend on a single measure.

```text
Secure transport
  + least privilege
  + validated inputs
  + protected secrets
  + capability-based authorization
  + confirmation of sensitive actions
  + auditing
  = a more controllable system
```

MCP provides a protocol for connecting applications, data, and tools, but the implementation must decide what each identity can do and under which conditions.

The current specification and its concrete requirements should be reviewed before deploying a server, especially when using HTTP transports and OAuth authorization.

Main sources:

- [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP Authorization 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
