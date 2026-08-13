# 05 - Prompts [ES](../es/05-prompts.md)

## Purpose

Explain what MCP prompts are, how they structure reusable workflows, and how they can be applied to operational DevOps tasks.

## Table of contents

- [Overview](#overview)
- [What is an MCP prompt](#what-is-an-mcp-prompt)
- [How a prompt works](#how-a-prompt-works)
  - [Discovery](#discovery)
  - [Invocation](#invocation)
  - [Arguments](#arguments)
  - [Generated messages](#generated-messages)
- [Prompts vs tools vs resources](#prompts-vs-tools-vs-resources)
- [Prompts and day-to-day commands](#prompts-and-day-to-day-commands)
- [Prompts applied to DevOps](#prompts-applied-to-devops)
  - [Diagnosing a service](#diagnosing-a-service)
  - [Reviewing a deployment](#reviewing-a-deployment)
  - [Analyzing a CI/CD failure](#analyzing-a-cicd-failure)
  - [Reviewing a Terraform plan](#reviewing-a-terraform-plan)
  - [Investigating an alert](#investigating-an-alert)
  - [Following a runbook](#following-a-runbook)
- [Prompt example](#prompt-example)
- [Prompt design](#prompt-design)
- [Security](#security)
- [Best practices](#best-practices)
- [Common mistakes](#common-mistakes)
- [Key idea](#key-idea)

## Overview

In MCP, a prompt is a reusable template exposed by a server to help the user start a specific task.

A prompt can guide the model to:

- Query specific resources.
- Use specific tools.
- Follow a diagnostic workflow.
- Analyze an operational situation.
- Apply a documented procedure.
- Return a response with a specific structure.

The main idea is:

```text
The user selects a prompt
  |
  v
The host requests the prompt from the server
  |
  v
The server returns prepared messages
  |
  v
The model uses tools and resources
  |
  v
The assistant returns the result to the user
```

A prompt should not be an open door to execute any action.

Its purpose is to structure a task and make the interaction more predictable.

## What is an MCP prompt

An MCP prompt is an instruction template offered by the server to the host.

Conceptual examples:

```text
diagnose-service
review-deployment
analyze-pipeline-failure
review-terraform-plan
investigate-alert
follow-runbook
```

A prompt can include:

- A name.
- A title.
- A description.
- Arguments.
- Prepared messages.
- References to tools or resources.
- Instructions about the output format.

Unlike a normal instruction freely written by the user, an MCP prompt provides a reusable structure.

For example, a user might write:

```text
Review what is happening with api in production.
```

A prompt defined by the server could structure that task as follows:

```text
Prompt: diagnose-service

Arguments:
  service: api
  environment: production
  symptom: high error rate
```

This allows the model to receive clearer information and lets the workflow be reused in different situations.

## How a prompt works

Prompts usually follow this flow:

1. The server exposes the available prompts.
2. The host shows those prompts to the user.
3. The user selects a prompt.
4. The user provides the required arguments.
5. The host requests the prompt from the server.
6. The server returns prepared messages.
7. The model uses the available context, tools, and resources.

The main operations are:

```text
prompts/list
prompts/get
```

The host can show prompts through:

- Slash commands.
- A command palette.
- Buttons for frequent actions.
- Context menus.
- Selectable templates in the interface.

Prompts are user-controlled. They should normally be invoked explicitly and should not activate automatically like a tool.

### Discovery

To discover the available prompts, the client can request their list:

```text
Client ---- prompts/list ----> Server
Client <--- prompt metadata --- Server
```

The server might return:

```json
{
  "prompts": [
    {
      "name": "diagnose-service",
      "title": "Diagnose a service",
      "description": "Analyze an operational problem using available information."
    }
  ]
}
```

The list provides the information the host needs to display and describe each prompt.

### Invocation

When the user selects a prompt, the host can request it using its name and arguments:

```text
Client ---- prompts/get ----> Server
Client <--- prompt messages --- Server
```

Conceptual example:

```json
{
  "name": "diagnose-service",
  "arguments": {
    "service": "api",
    "environment": "production",
    "symptom": "high error rate"
  }
}
```

The server returns the messages that make up the prompt.

The host can add those messages to the conversation and allow the model to continue the workflow.

### Arguments

Prompts can receive arguments to adapt the template to each situation.

Example:

```text
Prompt: diagnose-service

Arguments:
  service: api
  environment: production
  symptom: high error rate
```

Arguments should:

- Have clear names.
- Describe their purpose.
- Be validated whenever possible.
- Indicate whether they are required.
- Avoid accepting unnecessary data.
- Distinguish environments and resources correctly.

A prompt without arguments can be useful for general tasks:

```text
Prompt: explain-cluster-health
```

A parameterized prompt can adapt better to a specific operation:

```text
Prompt: diagnose-service
Arguments:
  service
  environment
  symptom
```

### Generated messages

A prompt can return one or more prepared messages.

Conceptual example:

```text
Analyze the api service in the production environment.

Reported symptom:
high error rate

Use the available resources to query:

- Active alerts.
- Recent metrics.
- Relevant logs.
- Recent deployments.

Return:

1. Evidence found.
2. Possible hypotheses.
3. Safe recommended actions.
4. Actions that require human confirmation.
```

The prompt should not invent data or assume that all resources or tools exist.

It should guide the model to discover and use the capabilities that are actually available.

---

## Prompts vs tools vs resources

The three primitives can work together, but they have different purposes.

| Element | Tool | Resource | Prompt |
|---|---|---|---|
| Purpose | Execute an action | Provide information | Structure a task |
| Main control | Model or application | Application | User |
| Identification | Tool name | Resource URI | Prompt name |
| Input | Structured arguments | URI or parameterized URI | Prompt arguments |
| Result | Operation result | Data or context | Prepared messages |
| Example | `get_pod_logs(...)` | `kubernetes://pods/api/logs` | `diagnose-service` |

A simple way to remember it:

```text
Tool:
  Does something.

Resource:
  Provides something.

Prompt:
  Guides how to approach something.
```

Combined example:

```text
Prompt:
  diagnose-service

Resources:
  observability://services/api/alerts
  observability://services/api/metrics
  kubernetes://namespaces/production/pods

Tools:
  get_service_metrics(...)
  get_pod_logs(...)
  list_alerts(...)
```

The prompt structures the workflow.

Resources provide context.

Tools execute concrete operations.

## Prompts and day-to-day commands

Prompts can be presented as frequently used commands within the host.

Examples:

```text
/diagnose-service api production
/review-deployment payments staging
/analyze-pipeline-failure backend 1842
/review-terraform-plan platform staging
/investigate-alert api-high-latency api production
```

These commands do not have to be terminal commands.

They can be a way to invoke prompts from:

- A chat.
- A command palette.
- A web interface.
- A code editor.
- An internal operations system.

For example:

```text
User types:
/diagnose-service api production
```

The host can resolve it as:

```text
Prompt:
  diagnose-service

Arguments:
  service: api
  environment: production
```

And request it from the server:

```text
Client ---- prompts/get ----> Server
Client <--- prompt messages --- Server
```

The model can then use the available tools and resources to complete the diagnosis.

The advantage is that frequent tasks have a common structure and do not depend entirely on each user writing different instructions.

## Prompts applied to DevOps

### Diagnosing a service

```text
Prompt:
  diagnose-service

Arguments:
  service
  environment
  symptom
```

Example:

```text
/diagnose-service api production "high error rate"
```

The prompt can tell the model to query:

- Active alerts.
- Recent metrics.
- Logs.
- Pod status.
- Recent deployments.
- Open incidents.

The result could be organized as follows:

```text
1. Problem summary.
2. Evidence found.
3. Possible causes.
4. Affected resources.
5. Recommended next steps.
6. Actions that require approval.
```

### Reviewing a deployment

```text
Prompt:
  review-deployment

Arguments:
  service
  environment
  deployment_id
```

Example:

```text
/review-deployment payments staging deploy-1842
```

The workflow could request:

- Reviewing the deployment history.
- Checking the current state.
- Comparing it with the previous deployment.
- Reviewing known errors.
- Querying metrics after the deployment.
- Recommending further investigation.

The prompt should not execute a rollback automatically.

A rollback action should be represented by an independent tool and require appropriate confirmation and permissions.

### Analyzing a CI/CD failure

```text
Prompt:
  analyze-pipeline-failure

Arguments:
  pipeline
  run_id
```

Example:

```text
/analyze-pipeline-failure backend 1842
```

The prompt could guide analysis of:

- Pipeline status.
- The failed job.
- Job logs.
- Recent changes.
- Execution history.
- Generated artifacts.
- Possible causes.

The result should distinguish observed facts from hypotheses.

### Reviewing a Terraform plan

```text
Prompt:
  review-terraform-plan

Arguments:
  project
  environment
```

Example:

```text
/review-terraform-plan platform staging
```

The prompt should request:

- A summary of the changes.
- A separation of added, modified, and deleted resources.
- Identification of possible risks.
- Detection of changes in production.
- Identification of sensitive resources.
- Confirmation before any apply operation.

The tool that runs `terraform apply` should remain separate and have additional controls.

### Investigating an alert

```text
Prompt:
  investigate-alert

Arguments:
  alert
  service
  environment
```

Example:

```text
/investigate-alert api-high-latency api production
```

The prompt can structure the analysis around:

1. Alert status.
2. Start time.
3. Related metrics.
4. Relevant logs.
5. Recent changes.
6. Hypotheses.
7. Safe next steps.

### Following a runbook

```text
Prompt:
  follow-runbook

Arguments:
  runbook
  service
  environment
```

Example:

```text
/follow-runbook high-latency api production
```

The prompt can combine:

```text
Resource:
  docs://runbooks/high-latency

Resources:
  observability://services/api/metrics
  observability://services/api/alerts

Tools:
  get_service_metrics(...)
  get_alert_details(...)
```

This shows the value of combining the three primitives:

- The prompt structures the workflow.
- Resources provide context.
- Tools execute concrete queries or actions.

## Prompt example

Conceptual definition example:

```json
{
  "name": "diagnose-service",
  "title": "Diagnose a service",
  "description": "Analyze an incident using metrics, alerts, logs, and deployment history.",
  "arguments": [
    {
      "name": "service",
      "description": "Service to investigate",
      "required": true
    },
    {
      "name": "environment",
      "description": "Target environment",
      "required": true
    },
    {
      "name": "symptom",
      "description": "Observed symptom or error",
      "required": true
    }
  ]
}
```

The generated content could be:

```text
You are investigating a DevOps incident.

Service: api
Environment: production
Symptom: high error rate

Use the available resources to query:

- Current alerts.
- Recent metrics.
- Relevant logs.
- Recent deployments.

Use read-only tools during the investigation.

Return:

1. Evidence found.
2. Likely causes.
3. Recommended next steps.
4. Actions that require human approval.
```

This example does not execute any action by itself.

Its purpose is to guide the workflow and define the response format.

## Prompt design

A well-designed prompt should be focused, predictable, and easy to review.

Before creating one, it is useful to define:

- Which task it starts.
- Which arguments it needs.
- Which resources it should query.
- Which tools it may use.
- Which information it should return.
- Which actions are outside its scope.

A diagnostic prompt and a remediation prompt should not be mixed without a clear reason.

A recommended structure is:

```text
Context:
  Which system or service is being analyzed.

Objective:
  What the model needs to determine.

Sources:
  Which resources it should query.

Operations:
  Which tools it may use.

Restrictions:
  What it must not do.

Output:
  How it should present the result.
```

## Security

A prompt is not automatically safe just because it is a template.

It can guide the model toward sensitive operations and combine tools with different risk levels.

Prompts should:

- Clearly state the environment.
- Distinguish development, staging, and production.
- Prioritize read-only tools.
- Prohibit destructive actions by default.
- Request human confirmation before changes.
- Contain no secrets.
- Not hide the tools they intend to use.
- Avoid ambiguous instructions.
- Define what to do when data is missing.
- Separate diagnosis from remediation.

A useful distinction is:

```text
Diagnostic prompt:
  Queries information and summarizes evidence.

Remediation prompt:
  Proposes actions but requires confirmation.

Execution prompt:
  Requires permissions and explicit approval.
```

A good question to ask before creating a prompt is:

> If the model follows these instructions incorrectly, what is the worst possible outcome?

If the answer includes deleting resources, deploying changes, leaking secrets, or affecting production, the prompt needs stronger controls.

## Best practices

- Use clear and specific names.
- Keep each prompt focused on one task.
- Define explicit arguments.
- Describe which information should be queried.
- State which tools may be used.
- State which resources are relevant.
- Separate diagnosis from execution.
- Request confirmation for sensitive actions.
- Return results with a predictable structure.
- Document limitations.
- Validate arguments.
- Avoid overly generic prompts.
- State what to do when there is not enough data.

## Common mistakes

- Creating a prompt that tries to solve every problem.
- Confusing a prompt with a tool.
- Executing destructive commands from a template.
- Failing to distinguish the environment.
- Failing to request important arguments.
- Hiding the actions the workflow may perform.
- Mixing diagnosis and remediation.
- Failing to validate parameters.
- Assuming data will always be available.
- Failing to include a structured output.
- Depending on specific tool names without documenting it.
- Presenting hypotheses as confirmed facts.

## Key idea

An MCP prompt does not execute a DevOps task by itself.

Its purpose is to provide a reusable structure so that the user can start a clear workflow and the model can combine resources and tools in a controlled way.

In DevOps:

```text
Prompt:
  Defines the workflow.

Resource:
  Provides the context.

Tool:
  Executes an operation.
```

Prompts make it possible to turn frequent operational procedures into reusable, understandable, and easier-to-review workflows.

The structure of this chapter is based on the `prompts/list` and `prompts/get` operations and on MCP's model of prompts being explicitly controlled by the user.
