# 08 - Testing [ES](../es/08-testing.md)

## Purpose

Explain how to test MCP servers and their tools before using them in real environments.

Testing does not depend only on the MCP protocol. It also depends on the tools, resources, prompts, transports, and external systems exposed by the server.

## Table of contents

- [Introduction](#introduction)
- [Testing layers](#testing-layers)
- [Unit tests](#unit-tests)
- [MCP contract tests](#mcp-contract-tests)
- [Testing with MCP Inspector](#testing-with-mcp-inspector)
- [Integration tests](#integration-tests)
- [Mocks and controlled environments](#mocks-and-controlled-environments)
- [DevOps-specific tests](#devops-specific-tests)
- [Negative and security tests](#negative-and-security-tests)
- [Transport tests](#transport-tests)
- [Performance and concurrency tests](#performance-and-concurrency-tests)
- [End-to-end tests](#end-to-end-tests)
- [CI/CD automation](#cicd-automation)
- [Testing matrix](#testing-matrix)
- [Final checklist](#final-checklist)
- [Key idea](#key-idea)

---

## Introduction

An MCP server may appear correct because it starts and displays its tools, but that does not prove that it is secure, compatible, or suitable for a real environment.

A complete test strategy should validate:

- Internal code.
- The MCP contract.
- Exposed tools.
- Resources and prompts.
- The transport in use.
- Permissions.
- External integrations.
- Behavior during errors.

Not every test needs Kubernetes, Docker, Terraform, or real credentials. A good strategy separates the server's own logic from external dependencies and uses mocks, fixtures, and isolated environments whenever possible.

## Testing layers

Tests can be organized from the smallest to the broadest scope:

```text
Unit tests
  |
  +-- MCP contracts and schemas
        |
        +-- Server integration
              |
              +-- stdio or HTTP transport
                    |
                    +-- External DevOps systems
                          |
                          +-- Real MCP host
```

Each layer finds different problems:

| Layer | What it checks | Typical cost |
|---|---|---:|
| Unit | Isolated logic | Low |
| Contract | MCP compatibility | Low |
| Integration | Server and client | Medium |
| Transport | Real communication | Medium |
| External | Kubernetes, Docker, or cloud | High |
| End-to-end | Complete workflow | High |

Most tests should be in the fast layers. External and end-to-end tests should be reserved for workflows that genuinely need to validate a complete integration.

## Unit tests

Unit tests check server logic without necessarily starting the complete MCP process.

They can cover:

- Argument validation.
- Data conversion.
- Log filtering.
- Pagination limits.
- Response construction.
- Error handling.
- Secret redaction.
- Mapping external states to MCP errors.

Conceptual example:

```text
Input:
  namespace = staging
  lines = 100

Expected result:
  namespace is valid
  lines are within the limit
  query is allowed
```

Invalid cases should also be tested:

```text
lines = -1       -> reject
lines = 1000000  -> reject
namespace = prod -> reject if not authorized
```

These tests should be fast, deterministic, and independent of a network, cluster, or real credentials.

## MCP contract tests

Contract tests check that the server fulfills what it announces through MCP.

It is useful to validate:

- `initialize`.
- `tools/list`.
- `tools/call`.
- `resources/list`.
- `resources/read`.
- `prompts/list`.
- `prompts/get`.
- JSON schemas.
- Required fields.
- Input and output types.
- Declared capabilities.

A server should not announce a capability that it cannot execute correctly. Similarly, a tool must declare a schema consistent with the arguments it actually accepts.

Example validation flow:

```text
tools/list
  |
  +-- Tool exists
  +-- Name is unique
  +-- Description exists
  +-- inputSchema is valid
  +-- Required fields match the implementation
```

This layer checks that the server speaks MCP correctly, even if it does not yet perform real operations against Kubernetes or Terraform.

## Testing with MCP Inspector

MCP Inspector is an official interactive tool for testing and debugging MCP servers. It can be used as the first manual check during development.

Inspector can be used to review:

- Connections through `stdio`.
- Connections through `Streamable HTTP`.
- Initial negotiation.
- Available tools.
- Schemas and arguments.
- Resources and subscriptions.
- Prompts and their arguments.
- Execution results.
- Logs and notifications.

Recommended workflow:

```text
1. Start the server with Inspector.
2. Check the connection.
3. Review initialize and the capabilities.
4. List tools, resources, and prompts.
5. Execute valid cases.
6. Execute invalid cases.
7. Review results, errors, and logs.
```

Inspector is very useful during development, but it does not replace automated tests. A manual test may discover a problem; an automated test helps prevent it from returning.

Conceptual execution example:

```bash
npx @modelcontextprotocol/inspector <server-command> <arguments>
```

The exact command depends on the language and package manager used by the server.

## Integration tests

Integration tests check the complete server together with an MCP client or test client.

They can validate:

- Real process startup.
- Communication through `stdio`.
- HTTP endpoint.
- Capability negotiation.
- Real tool calls.
- Responses and errors.
- Cancellation and timeouts.
- Server restarts.
- Resource cleanup on shutdown.

A typical integration test could follow this flow:

```text
Start server
  |
  +-- Connect MCP client
  +-- Run initialize
  +-- List tools
  +-- Call a read-only tool
  +-- Verify result
  +-- Close connection
  +-- Check clean shutdown
```

This layer tests communication between components, but a controlled environment should still be used for external systems.

## Mocks and controlled environments

External dependencies should be simulated when checking the real system is not necessary.

Examples:

- Simulated Kubernetes API.
- Mock Docker client.
- Terraform in plan mode.
- Simulated cloud API.
- Log fixtures.
- Temporary directories.
- Predefined HTTP responses.

The separation can be summarized as:

```text
Own logic:
  Fast and deterministic tests.

External integrations:
  Mocks or sandbox.

Production:
  Never use it as a normal testing environment.
```

A mock should represent relevant failure cases too. Simulating only successful responses creates a false sense of security.

It is useful to cover:

- Missing resource.
- Insufficient permission.
- Timeout.
- Incomplete response.
- Authentication error.
- Unavailable external service.
- Malformed data.

## DevOps-specific tests

The exact tests depend on the tools exposed by the server.

### Kubernetes

Possible tests include:

- Authorized namespaces.
- Missing resources.
- Pods without logs.
- Insufficient permissions.
- Log quantity limits.
- Incorrect cluster context.
- Blocked production actions.

### Docker

Possible tests include:

- Missing container.
- Stopped container.
- Output limits.
- Socket access.
- Disallowed image.
- Blocked deletion operations.

### Terraform

Possible tests include:

- Plan with no changes.
- Expected changes.
- Locked state.
- Unauthorized workspace.
- Credential error.
- Blocked `destroy`.
- Separation between `plan` and `apply`.

### Cloud

Possible tests include:

- Allowed regions.
- Authorized accounts.
- Out-of-scope resources.
- Cost limits.
- Expired credentials.
- Write operations without approval.

## Negative and security tests

Negative tests check that the server correctly rejects what it should not accept.

Recommended cases:

- Malformed arguments.
- Missing fields.
- Out-of-range values.
- Command injection.
- Unauthorized paths.
- Disallowed namespaces.
- Expired credentials.
- Tokens intended for another server.
- Destructive operations without confirmation.
- Secrets in responses or logs.
- HTTP requests with an invalid `Origin`.
- Access without permissions.

A security test should not only check that the operation fails. It should also check that:

- External state is not changed.
- Sensitive data is not leaked.
- The error is understandable.
- The operation is recorded when appropriate.
- A dangerous action is not retried automatically.

Example:

```text
Request: delete_resource(production_namespace)
Expected result:
  - Operation rejected
  - Cluster unchanged
  - No secrets in the response
  - Event recorded
```

## Transport tests

### stdio

`stdio` tests should check that:

- `stdout` contains only valid MCP messages.
- Logs are written to `stderr`.
- The process terminates correctly.
- The client detects unexpected shutdowns.
- Timeouts and cancellations are controlled.
- Configuration paths work outside the development directory.

Accidental output on `stdout` can break communication:

```text
Correct stdout:
  Valid JSON-RPC

Incorrect stdout:
  Starting server...
  Valid JSON-RPC
```

### Streamable HTTP

`Streamable HTTP` tests should cover:

- HTTPS.
- Required headers.
- `Origin` validation.
- JSON responses.
- SSE responses.
- HTTP errors `400`, `401`, `403`, and `500`.
- Size limits.
- Timeouts.
- Concurrent connections.
- Operation cancellation.

The goal is not only to prove that an endpoint exists, but also to check that it responds predictably and securely to valid and invalid requests.

## Performance and concurrency tests

Not every server needs a complete benchmark, but workflows that may affect user experience or infrastructure should be measured.

Possible measurements include:

- Tool latency.
- Response size.
- Many simultaneous calls.
- Long-running operations.
- Cancellation.
- Memory usage.
- Connection limits.
- External system saturation.

Long-running operations should have defined behavior:

```text
Start
  |
  +-- Observable progress
  +-- Controlled timeout
  +-- Cancellation available
  +-- Final result or clear error
```

Load tests should not be run against production without authorization and well-defined limits.

## End-to-end tests

End-to-end tests check the complete workflow:

```text
User
  |
  v
MCP Host
  |
  v
MCP Client
  |
  v
MCP Server
  |
  v
Kubernetes, Docker, Terraform, or cloud
```

They are valuable, but also slower, more fragile, and more expensive. They should run in a controlled environment with test data.

An end-to-end workflow can verify that:

- The host discovers the server.
- Tools appear correctly.
- The user authorizes an operation.
- The server validates arguments.
- The external system performs the change.
- The result returns to the host.
- The audit record is created.

Production should not be used as the normal end-to-end environment.

## CI/CD automation

A reasonable sequence for every pull request would be:

```text
Pull request
  |
  +-- Lint and types
  +-- Unit tests
  +-- Contract tests
  +-- Security tests
  +-- Integration tests
  +-- Build the server
  +-- Controlled publication or deployment
```

Tests that need real credentials, expensive services, or special environments should be separated and protected.

A simple policy could be:

- Every change runs unit and contract tests.
- Every transport change runs transport integration tests.
- Every tool change runs its valid and invalid cases.
- Permission changes run security tests.
- Sandbox tests run before publishing a version.
- Destructive tests require a manual and controlled execution.

## Testing matrix

| Area | Unit | Integration | End-to-end |
|---|---:|---:|---:|
| Argument validation | Yes | Yes | Optional |
| `tools/list` | No | Yes | Yes |
| Kubernetes | Mock | Sandbox | Optional |
| Secrets | Yes | Yes | Do not use production |
| `stdio` | No | Yes | Yes |
| Streamable HTTP | No | Yes | Yes |
| Permissions | Yes | Yes | Yes |
| Resource destruction | Mock | Sandbox | Controlled only |

This matrix is not a universal rule. It helps decide where to place each test and prevents everything from depending on a single end-to-end test.

## Final checklist

Before using an MCP server in a real environment:

- [ ] The server starts correctly.
- [ ] `initialize` works.
- [ ] Declared capabilities are correct.
- [ ] Tools have valid schemas.
- [ ] Valid and invalid inputs are tested.
- [ ] Errors and insufficient permissions are tested.
- [ ] Secrets are not leaked.
- [ ] `stdio` keeps `stdout` clean.
- [ ] HTTP validates authentication and transport.
- [ ] Destructive operations are protected.
- [ ] Automated tests exist in CI.
- [ ] Real integrations use a sandbox or controlled environments.
- [ ] Timeouts and cancellations have been tested.
- [ ] Logs are useful and contain no credentials.
- [ ] There is a way to reproduce failures.

## Key idea

Testing an MCP server does not simply mean checking that it starts.

```text
Server starts
  + valid MCP contract
  + correct tools
  + validated inputs
  + controlled errors
  + checked permissions
  + tested transport
  + isolated integrations
  + automated regressions
  = more reliable server
```

The strategy should grow with the server. A server with one local read-only tool may mainly need unit, contract, and integration tests. A server that modifies Kubernetes, Terraform, or cloud infrastructure also needs a sandbox, negative tests, authorization, auditing, and controls for destructive operations.

Main sources:

- [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)
- [MCP Debugging Guide](https://modelcontextprotocol.io/docs/tools/debugging)
- [MCP Python SDK](https://py.sdk.modelcontextprotocol.io/get-started/)
