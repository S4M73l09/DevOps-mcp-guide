# 05 - Error Handling [ES](README.md)

## Purpose

This example shows how to handle different types of errors in an MCP tool
without breaking the server or exposing sensitive information.

The `get_service_status` tool simulates a DevOps service status query and
allows different responses to be observed depending on the problem found.

## Included error types

This example distinguishes between:

1. A valid response.
2. An expected domain error.
3. An empty input.
4. An unexpected exception.

---


## Valid response

Input:

```json
{
    "service": "api"
}
```

Response:

```json
{
    "ok": true,
    "service": "api",
    "status": "healthy"
}
```

In this case, the call completes successfully and `is_error` is `false`.

## Expected domain error

When an unavailable service is queried:

```json
{
    "service": "missing-service"
}
```

The tool returns a structured response:

```json
{
    "ok": false,
    "error": "service_not_found",
    "message": "The requested service does not exist."
}
```

This type of error is part of the application's expected behavior.

For that reason, it is returned as a normal response with `ok: false`, rather
than as an internal exception.

## Empty input

When no service name is provided:

```json
{
    "service": ""
}
```

The response is:

```json
{
    "ok": false,
    "error": "service_required",
    "message": "A service name is required."
}
```

## Unexpected error

The `backend-timeout` value simulates a problem in an external system:

```json
{
    "service": "backend-timeout"
}
```

In this case, an exception is raised:

```python
raise TimeoutError(
    "The status provider did not respond within the time limit."
)
```

MCP marks the response as an error through:

```python
result.is_error is True
```

This behavior represents a failure that the tool cannot resolve as a normal
response.

---

## Difference between expected and unexpected errors

| Type | Example | Response |
|---|---|---|
| Valid result | `api` | `ok: true` |
| Domain error | `missing-service` | `ok: false` |
| Empty input | `""` | `ok: false` |
| Unexpected failure | `backend-timeout` | `is_error: true` |

Expected errors should return stable error codes and messages. Unexpected
exceptions should remain marked as tool errors.

---

## Best practices

### Use stable error codes

It is preferable to use codes that the client can interpret:

```json
{
    "error": "service_not_found"
}
```

The client can use `service_not_found` to decide which action to take, even if
the message text changes later.

### Do not expose internal traces

The following information must not be returned to the client:

* Complete Python traces.
* Internal server paths.
* Private hostnames.
* Tokens or credentials.
* Environment variables.
* Authentication details.
* Sensitive information from another resource.

The client should receive a useful but limited message.

### Separate public messages from internal details

The public message could be:

```text
The status provider did not respond within the time limit.
```

Technical details, such as the endpoint, the original exception, or the
number of retries, should be recorded internally.

### Do not hide unexpected errors

Not every error should be converted into:

```json
{
    "ok": true
}
```

A real failure must remain visible so that the client, tests, and monitoring
can detect it.

### Keep responses predictable

Tools should use a consistent structure so that clients can process their
responses without relying on ambiguous text.

### Do not retry without control

Retries against an external system should have:

* A maximum number of attempts.
* A time limit.
* A defined strategy.
* Clear behavior when the limit is reached.

### Do not make automatic changes in response to an error

A query error must not automatically trigger:

* Restarts.
* Rollbacks.
* Configuration changes.
* Scaling operations.
* Resource deletion.
* New deployments.

Any impactful action must be separated and protected by its own validations
and confirmations.

---

## Run the example

From this directory:

```bash
uv sync
```

Run the tests:

```bash
uv run pytest
```

## Test it with MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server error-handling-devops-mcp
```

The `Tools` section will show:

```text
get_service_status
```

Try the following values:

```text
api
missing-service
backend-timeout
```

You can also try an empty string to observe the `service_required` error.

## What the tests demonstrate

The tests verify:

* A valid response.
* A missing service.
* An empty input.
* An external system timeout.
* The difference between `ok: false` and `is_error: true`.

## Example limitations

This example does not:

* Query a real API.
* Access Kubernetes.
* Execute system commands.
* Perform deployments.
* Modify cloud resources.
* Restart services.
* Use real credentials.
* Implement external logging.

The timeout and special service values are local simulations used to study the
server's behavior in response to different errors.

---

## Images

#### Capture showing the server running:

![Capture-error-handling-devops-mcp](Images/Capture-error-handling-devops-mcp.png)

#### Capture showing the `api` service:

![Capture-of-service-handling](Images/Capture-of-service-handling.png)

#### Capture showing the backend error:

![Capture-error-backend](Images/Capture-error-backend.png)
