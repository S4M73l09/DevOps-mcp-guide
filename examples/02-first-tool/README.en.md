# 02 - First Tool [ES](README.md)

## Purpose

This example shows how to use an MCP tool. Before introducing real resources for DevOps environments, it keeps the same architecture as the previous example, where the purpose of each file and how it works are explained.

It includes the commands needed to register and test a tool.

## Commands

From the `examples/02-first-tool/` directory:

```bash
uv sync
```

Tests:

```bash
uv run pytest
```

Inspector using the `2.0.0` version tag:
```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server first-tool-devops-mcp
```

## Images

Image showing the tool inside the Inspector:

![Capture-minimal-tool.png](Images/Capture-minimal-tool.png)


Image showing the tool registration:
![Capture-minimal-registry-message](Images/Capture-minimal-registry-message.png)
