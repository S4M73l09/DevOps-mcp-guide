# 01 - What Is MCP [ES](../es/01-que-es-mcp.md)

## Purpose

Explain what Model Context Protocol (MCP) is, what problem it solves, and why it is useful for integrating assistants with external tools.

## Table of Contents

- [What Is MCP](#what-is-mcp)
  - [What Problem Does It Solve](#what-problem-does-it-solve)
- [Relationship Between Host Client and Server](#relationship-between-host-client-and-server)
  - [Host](#host)
  - [Client](#client)
  - [Server](#server)
- [Conceptual Flow](#conceptual-flow)
- [DevOps Use Cases](#devops-use-cases)
  - [Kubernetes](#kubernetes)
  - [Terraform](#terraform)
  - [Docker](#docker)
  - [CI/CD](#cicd)
  - [Observability](#observability)
- [When to Use MCP](#when-to-use-mcp)
- [When Not to Use MCP](#when-not-to-use-mcp)
- [Key Idea](#key-idea)

## What Is MCP

Model Context Protocol, or MCP, is an open protocol that standardizes how an AI application connects to external systems.

Its main goal is to allow an assistant to access context, execute tools, and use predefined flows without every integration having to invent its own mechanism from scratch.

Instead of creating a different integration for every assistant and tool combination, MCP proposes a common interface between:

- AI applications.
- Servers that expose capabilities.
- Reusable tools, data, and prompts.

A simple way to look at it:

> MCP is a standard layer for connecting AI assistants with external tools and context sources.

### What Problem Does It Solve

Without MCP, integrating AI with external tools usually means building custom solutions:

- A specific connector for GitHub.
- Another connector for Kubernetes.
- Another one for Terraform.
- Another one for logs.
- Another one for CI/CD.
- Another one for internal documentation.

This creates several problems:

- Integrations that are difficult to reuse.
- Duplicated logic across projects.
- No clear contract between the AI and the tools.
- Security that is difficult to control.
- Difficulty understanding what the assistant can or cannot do.
- Tight coupling between the AI client and each external system.

MCP solves this by defining a common protocol for exposing capabilities through primitives such as:

- Tools: executable actions.
- Resources: information or context that can be queried.
- Prompts: reusable templates for frequent tasks.

## Relationship Between Host Client and Server

MCP uses a host-client-server architecture.

### Host

The host is the application where the AI experience lives.

Examples of hosts can include:

- A code editor with AI capabilities.
- A desktop application with an assistant.
- An automation environment.
- An internal company agent.

The host coordinates the overall experience, manages permissions, and decides how to use the received context.

### Client

The MCP client is the component that maintains the connection between the host and a specific MCP server.

Usually, the host creates one client for each MCP server it connects to.

For example:

- One client for a Git MCP server.
- One client for a Kubernetes MCP server.
- One client for a Terraform MCP server.

Each client maintains an isolated session with its server.

### Server

The MCP server is the program that exposes capabilities to the host through the MCP protocol.

A server can offer:

- Tools to execute actions.
- Resources to query information.
- Prompts to reuse instructions or flows.

Examples:

- An MCP server that queries logs.
- An MCP server that lists Kubernetes pods.
- An MCP server that validates Terraform.
- An MCP server that queries CI/CD pipelines.
- An MCP server that reads internal documentation.

## Conceptual Flow

1. The user asks the assistant for something.
2. The host interprets the request.
3. The host uses an MCP client to talk to an MCP server.
4. The MCP server exposes tools, resources, or prompts.
5. The host decides which capabilities to use.
6. The result goes back to the assistant.
7. The assistant responds to the user with more context or with an action that has been performed.

## DevOps Use Cases

MCP fits very well in DevOps because many tasks involve checking state, validating configurations, diagnosing problems, or executing controlled actions.

### Kubernetes

An MCP server could expose tools such as:

- `list_pods`
- `get_pod_logs`
- `describe_deployment`
- `list_events`
- `check_namespace_health`

This would make it possible to ask:

> Check why the `api` deployment is failing in staging.

The assistant could query pods, events, and logs without the user manually copying every command.

### Terraform

An MCP server could expose tools such as:

- `terraform_fmt_check`
- `terraform_validate`
- `terraform_plan_summary`
- `list_modules`
- `detect_drift`

This would make it possible to ask:

> Validate this Terraform module and tell me if there are any risks before opening the PR.

### Docker

An MCP server could expose tools such as:

- `list_containers`
- `get_container_logs`
- `inspect_image`
- `check_compose_services`

This would make it possible to ask:

> Check why the backend container is not starting.

### CI/CD

An MCP server could connect to pipeline systems and expose:

- build status
- logs from failed jobs
- generated artifacts
- deployment history
- comparisons between runs

Example:

> Summarize why the latest pipeline on main failed.

### Observability

An MCP server could query:

- metrics
- traces
- logs
- alerts
- open incidents

Example:

> Look for error signals around the 10:30 deployment.

## When to Use MCP

MCP makes sense when we want AI to interact with external tools in a structured, secure, and reusable way.

Use it when:

- You want to expose capabilities to one or more assistants.
- You need to integrate DevOps tools through a common interface.
- There are repeatable operations that can be modeled as tools.
- There is useful information that can be exposed as resources.
- You want to control permissions, inputs, and allowed actions.
- You want to separate DevOps logic from the AI client.
- You want to create an integration that can be reused by other people or teams.

## When Not to Use MCP

MCP is not always necessary.

You do not need MCP when:

- You only need a one-off script.
- The task does not involve an AI application.
- The integration will be used only once.
- You do not need to expose reusable capabilities.
- The tool already has a good enough direct integration.
- The cost of maintaining an MCP server is higher than the benefit.
- The action is too sensitive and you do not have a clear model for permissions, auditing, and human confirmation.

## Key Idea

MCP does not replace DevOps tools.

MCP creates a standard interface so an AI application can use those tools in a controlled way.

In DevOps, this means we can move from:

> Copy logs, paste errors, run commands manually, and ask the assistant for help.

To:

> The assistant queries authorized context, runs safe checks, and helps diagnose issues with real data.
