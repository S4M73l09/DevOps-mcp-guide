# 03-resources [ES](README.md)

## Purpose

This example shows how to register and read MCP resources.

A resource represents information that the server exposes so that the client can consult it. Unlike a tool, its main goal is to provide context or data, not execute an action.

## Resources included

### Static resource

URI:

```text
devops://service-catalog
```
Returns a fixed catalog of DevOps services in JSON format.

### Dynamic resource

Template:
```text
devops://services/{service_name}/status
```

Allows you to check the status of a specific service by replacing {service_name} with its name.


Template:
```text
devops://services/worker/status
```

## Commands

In this folder:

```bash
uv sync
```

Run the tests:

```bash
uv run pytest
```

Open MCP Inspector:

```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server resource-devops-mcp
```

## Example limitations.

This example does not yet query external APIs, Kubernetes, cloud, or files
of the system. The data is defined within the server to focus on
the structure and behavior of MCP resources.

---

## Sample Images

Capture showing the resource:

![Capture of resource DevOps](Images/Capture-resources.png)

Capture showing the concrete resource:

![Capture of resource DevOps Service](Images/Capture-resources-devops-service.png)