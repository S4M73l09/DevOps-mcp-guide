# 03 - Tools [ES](../es/03-herramientas.md)

## Purpose

Explain what MCP tools are, how external actions are modeled, and which criteria to use to design them safely, clearly, and in a reusable way for DevOps environments.

## Table of contents

- [Overview](#overview)
- [What is a tool](#what-is-a-tool)
  - [How the model decides to use a tool](#how-the-model-decides-to-use-a-tool)
- [Anatomy of a tool](#anatomy-of-a-tool)
  - [Name](#name)
  - [Description](#description)
  - [Input schema](#input-schema)
  - [Output](#output)
  - [Errors](#errors)
- [Tool vs script](#tool-vs-script)
- [DevOps tools](#devops-tools)
  - [Kubernetes](#kubernetes)
  - [Terraform](#terraform)
  - [Docker](#docker)
  - [CI/CD](#cicd)
  - [Observability](#observability)
- [Secure tool design](#secure-tool-design)
- [Best practices](#best-practices)
- [Common mistakes](#common-mistakes)
- [Key idea](#key-idea)

## Overview

In MCP, a tool is an executable capability offered by a server to the host.

A tool allows an AI application to request a specific action from an external system in a structured way.

For example:

- Query logs.
- List pods.
- Validate a Terraform module.
- Check the status of a pipeline.
- Get information about a container.
- Query observability alerts.

The important idea is that a tool should not be an open door to every possible action. A good tool represents a specific action, with defined inputs, clear limits, and an understandable output.

A simple way to see it:

```text
User asks for something
  |
  v
Host decides whether it needs a tool
  |
  v
MCP Client calls a tool from the MCP server
  |
  v
MCP Server executes the controlled action
  |
  v
Result returns to the host and the assistant
```

## What is a tool

A tool is a function exposed by an MCP server so that the host can invoke it when useful.

A tool usually has:

- A name
- A description
- An input schema
- An output
- Possible errors

Here is a conceptual example:

```text
Tool: get_pod_logs

Description:
  Gets recent logs from a Kubernetes pod.

Input:
  namespace: string
  pod: string
  lines: optional number

Output:
  logs: string
  namespace: string
  pod: string
  lines: number
```

In this example, the tool does not allow arbitrary Kubernetes commands. It only allows logs to be queried for a pod, using specific parameters.

This makes the action easier to understand, validate, audit, and reuse.

### How the model decides to use a tool

The model should not have to guess about hidden tools. The host knows which tools are available because the MCP server exposes them.

When a tool is available, its name, description, and schema help the model or the host decide whether it should be used.

That is why a tool's description is important.

A vague description leads to incorrect usage.

Bad example:
```text
name: check
description: Checks things.
```

Better example:
```text
name: terraform_validate
description: Validates the syntax and configuration of a Terraform project without applying changes.
```

---

## Anatomy of a tool

A well-designed tool has a clear contract.

That contract allows the host to know how to invoke it and the server to validate the input before executing anything.

### Name

The name should be short, descriptive, and specific.

Good examples:

```text
get_pod_logs
list_namespaces
terraform_validate
docker_list_containers
get_pipeline_status
```

Bad examples:

```text
run
execute
do_task
check
devops_tool
```

A good name helps the model choose the right tool and helps people understand what it does.

### Description

The description explains when to use the tool and exactly what it does.

It should answer:

- What action does it perform?
- Which system does it act on?
- Does it modify state or not?
- What important limitations does it have?

Example:

```text
Gets recent logs from a Kubernetes pod in an allowed namespace.
```

This description is better than simply saying:

```text
Gets logs
```

Because it provides operational and security context.

### Input schema

The input schema defines the parameters accepted by the tool.

It serves as a contract between the host and the server.

Conceptual example:

```json
{
  "namespace": "string",
  "pod": "string",
  "lines": "number"
}
```

The schema should be as restrictive as possible.

For example:

- `namespace` should be required.
- `pod` should be required.
- `lines` could have a maximum limit.
- An arbitrary command should not be accepted as a string.

Dangerous example:

```json
{
  "command": "string"
}
```

Safer example:

```json
{
  "namespace": "string",
  "pod": "string",
  "lines": "number"
}
```

In DevOps, an overly open input schema often becomes a security risk.

### Output

The output of a tool should be clear and, whenever possible, structured.

Simple example:

```json
{
  "namespace":"staging",
  "pod": "api-7c9d9f7d4b-x2k8p",
  "lines": 100,
  "logs": "...",
  "truncated": false
}
```

A structured output allows the assistant to explain the result more effectively and lets other systems reuse it.

When the output is long text, such as logs, it can be useful to include metadata:

- Whether the result was truncated.
- How many lines were returned.
- Which resources the result came from.
- Whether there were warnings.
- Which timestamp range it covers.

### Errors

Tools should return understandable errors.

It is not enough to fail in a generic way.

Examples of useful errors:

```text
namespace_not_allowed
pod_not_found
invalid_line_limit
command_timeout
terraform_project_not_found
pipeline_not_found
```

A good error should help explain:

- What failed.
- Whether the user can fix it.
- Whether the action was partial or was not executed.
- Whether there is a security restriction.

Example:

```json
{
  "error":"namespace_not_allowed",
  "message": "The production namespace is not allowed for this tool.",
  "details": {
    "namespace": "production",
    "allowedNamespaces": ["dev", "staging"]
  }
}
```

This type of response is much more useful than:

```text
Error:failed
```

---

## Tool vs script

An MCP tool is not simply a script exposed to the model.

A script is usually intended to be run by a person or a pipeline.

An MCP tool is intended to be discovered, understood, and invoked by an AI application through a clear contract.

Important differences:

```text
Script:
  - May accept free-form arguments.
  - May assume local context.
  - May print unstructured text.
  - May mix several responsibilities.

MCP tool:
  - Has a name and description.
  - Has an input schema.
  - Must validate inputs.
  - Must return a clear output.
  - Should have a focused responsibility.
```

This does not mean that a tool cannot call a script internally.

It can, but the tool should wrap that script with a safe, validated, and understandable interface.

## DevOps tools

DevOps tools should model specific actions and preferably be non-destructive at first.

The initial goal should not be to automate everything, but to expose useful capabilities with clear limits.

### Kubernetes

Tool examples:

```text
list_namespaces
list_pods
get_pod_logs
describe_deployment
list_events
check_namespace_health
```

Good ideas:

- Limit allowed namespaces.
- Limit the number of logs.
- Avoid arbitrary commands.
- Separate read operations from actions that modify the cluster.

Dangerous tool:

```text
kubectl_raw(command: string)
```

Safer tool:

```text
get_pod_logs(namespace: string, pod: string, lines: number)
```

### Terraform

Tool examples:

```text
terraform_fmt_check
terraform_validate
terraform_plan_summary
list_terraform_modules
detect_drift
```

Good ideas:

- Start with read-only or validation actions.
- Avoid `apply` by default.
- Validate project paths.
- Summarize plans without exposing secrets.
- Separate validation from actual execution.

Dangerous tool:

```text
terraform_command(args: string)
```

Safer tool:

```text
terraform_validate(projectPath: string)
```

### Docker

Tool examples:

```text
list_containers
get_container_logs
inspect_container
inspect_image
check_compose_services
```

Good ideas:

- Avoid granting unrestricted access to the Docker socket.
- Limit destructive operations.
- Distinguish between listing, inspecting, starting, stopping, and deleting.
- Truncate long logs.

Dangerous tool:

```text
docker_run(command: string)
```

Safer tool:

```text
get_container_logs(containerName: string, lines: number)
```

### CI/CD

Tool examples:

```text
get_pipeline_status
list_recent_runs
get_failed_job_logs
compare_pipeline_runs
get_deployment_history
```

Good ideas:

- Check status before executing actions.
- Avoid rerunning pipelines without confirmation.
- Do not expose job tokens or secrets.
- Summarize long logs.

Dangerous tool:

```text
run_pipeline(pipelineId: string)
```

Safer tool:

```text
get_pipeline_status(pipelineId: string)
```

### Observability

Tool examples:

```text
list_alerts
get_services_metrics
query_logs
get_trace_summary
get_incident_status
```

Good ideas:

- Limit time ranges.
- Avoid excessively expensive queries.
- Return summaries and metadata.
- Separate logs, metrics, and traces into different tools when this helps maintain clarity.

Safer tool:

```text
get_service_metrics(service: string, from: string, to: string)
```

---

## Secure tool design

In DevOps, a tool may interact with sensitive systems.

Therefore, secure design is not optional, but mandatory:

Recommended principles:

- Prefer specific tools over generic tools.
- Validate all parameters.
- Limit allowed paths, namespaces, projects, or services.
- Use allowlists whenever possible.
- Define timeouts.
- Limit output size.
- Separate read operations from write operations.
- Avoid destructive actions by default.
- Require human confirmation for sensitive actions.
- Log important actions for auditing.

A good question to ask before creating a tool is:

> If the model misuses this tool, what is the worst possible outcome?

If the answer includes deleting resources, deploying changes, exposing secrets, or breaking production, the tool needs more limits or perhaps should not exist yet.

## Best practices

Best practices for designing MCP tools:

- Use clear and specific names.
- Write descriptions that explain when to use the tool.
- Keep one responsibility per tool.
- Use restrictive input schemas.
- Return structured outputs.
- Include useful metadata.
- Return actionable errors.
- Avoid arbitrary commands.
- Think about permissions from the beginning.
- Document whether the tool modifies state or only queries information.

Recommended description example:

```text
Validates a Terraform project by running non-destructive checks. It does not apply changes or modify infrastructure.
```

---

## Common mistakes

Frequent mistakes when designing MCP tools:

- Creating an overly generic tool.
- Using ambiguous names.
- Not explaining whether the tool modifies state.
- Accepting free-form commands as input.
- Failing to validate parameters.
- Returning unstructured text when JSON could be returned.
- Mixing several responsibilities in a single tool.
- Failing to limit logs or large results.
- Exposing destructive actions too soon.
- Failing to consider auditing.

Bad design example:

```text
run_devops_task(task: string)
```

Problems:

- It is not clear what it can do.
- It is difficult to validate.
- It is difficult to audit.
- It may end up executing unintended actions.
- The model could use it in the wrong context.

Better design:

```text
terraform_validate(projectPath: string)
get_pod_logs(namespace: string, pod: string, lines: number)
get_pipeline_status(pipelineId: string)
```

## Key idea

An MCP tool should not be an open door to the system.

An MCP tool should be a specific, validated, and safe action that the host can offer to the assistant.

In DevOps, designing tools well is the difference between a useful assistant and dangerous automation.
