# 09 - DevOps Use Cases [ES](../es/09-casos-de-uso-devops.md)

## Purpose

Show real use cases where MCP can provide value in DevOps operations.

MCP does not replace Kubernetes, Docker, Terraform, cloud systems, or CI/CD platforms. It provides a controlled interface for querying those systems and, when appropriate, executing operations against them.

The goal of this chapter is to relate MCP capabilities to concrete operational problems and define a safe progression for building a DevOps MCP server.

## Table of contents

- [Introduction](#introduction)
- [How to analyze a use case](#how-to-analyze-a-use-case)
- [Service diagnostics](#service-diagnostics)
- [Log reading and analysis](#log-reading-and-analysis)
- [Kubernetes queries](#kubernetes-queries)
- [Controlled Kubernetes operations](#controlled-kubernetes-operations)
- [Docker operations](#docker-operations)
- [Terraform](#terraform)
- [CI/CD integration](#cicd-integration)
- [Runbook automation](#runbook-automation)
- [Observability and incidents](#observability-and-incidents)
- [Relationship between tools, resources, and prompts](#relationship-between-tools-resources-and-prompts)
- [What the first server should not do](#what-the-first-server-should-not-do)
- [Recommended evolution](#recommended-evolution)
- [Risk matrix](#risk-matrix)
- [Key idea](#key-idea)

---

## Introduction

DevOps includes many repetitive tasks that require querying different systems:

- Kubernetes.
- Docker.
- Terraform.
- Cloud platforms.
- CI/CD systems.
- Observability tools.
- Code repositories.
- Ticket and incident systems.

MCP can provide a common interface for querying those systems and, in a controlled way, executing actions.

An MCP DevOps server could provide:

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
DevOps MCP Server
  |
  +-- Kubernetes
  +-- Docker
  +-- Terraform
  +-- CI/CD
  +-- Observability
```

The ability to execute operations does not mean that every action should be automatic. Each tool must have a defined scope, specific permissions, and a known risk level.

## How to analyze a use case

Each use case should be documented using a common structure:

```text
Objective
  |
  +-- External system
  +-- MCP tools
  +-- MCP resources
  +-- Optional prompts
  +-- Required permissions
  +-- Risks
  +-- Tests
  +-- Automation level
```

For each case, answer:

- What problem does it solve?
- What data does it need?
- Which MCP tools does it expose?
- Which operations are read-only?
- Which operations modify state?
- What confirmations are required?
- What errors can occur?
- What permissions are needed?
- How can it be tested?
- What risk level does it have?

A tool should represent a specific action:

```text
get_pod_logs(namespace, pod, lines)
```

Rather than an overly general tool:

```text
run_shell(command)
```

Specific tools are easier to validate, authorize, test, and audit.

## Service diagnostics

Service diagnostics are one of the first recommended use cases because they can provide value without modifying infrastructure.

A user might ask:

```text
Why is the api service failing?
```

The MCP server could follow this flow:

```text
1. Check the deployment status.
2. Check the associated pods.
3. Read recent events.
4. Read recent logs.
5. Compare expected and available replicas.
6. Identify frequent errors.
7. Return a diagnostic summary.
```

Possible tools:

```text
get_service_status
list_service_pods
get_recent_events
get_pod_logs
```

A result could include:

```text
Service: api
Environment: staging

Status:
  - Desired replicas: 3
  - Available replicas: 1
  - Pods with errors: 2

Indicators:
  - ImagePullBackOff
  - Frequent restarts
  - Database connection error

Suggested next step:
  - Review the credentials and database status.
```

This use case should start with read-only tools.

## Log reading and analysis

Reading logs is a common operations and support task.

A tool could be defined as:

```text
get_pod_logs(namespace, pod, lines, since)
```

It should apply limits such as:

- Allowed namespaces.
- Maximum number of lines.
- Maximum query duration.
- Maximum response size.
- Secret redaction.
- Controlled text filters.

Example input:

```json
{
  "namespace": "staging",
  "pod": "api-123",
  "lines": 100,
  "since": "15m"
}
```

It is important to distinguish between reading and interpreting logs:

```text
Read logs:
  Query operation.

Analyze logs:
  Analysis operation.

Modify the system because of a detected error:
  Separate operation requiring confirmation.
```

The server should not automatically execute a remediation action simply because a log contains an instruction or a known error.

## Kubernetes queries

Kubernetes provides many resources that can be queried through MCP:

- Pods.
- Deployments.
- Services.
- Ingresses.
- Jobs.
- Events.
- Namespaces.
- Non-sensitive ConfigMaps.
- Node status.

Possible read-only tools:

```text
list_pods(namespace)
get_deployment(namespace, name)
list_services(namespace)
get_ingress(namespace, name)
get_recent_events(namespace)
```

The server should limit:

- Cluster context.
- Namespaces.
- Resource types.
- Result count.
- Access to sensitive data.
- Identities allowed to perform queries.

The contents of every Kubernetes Secret should not be exposed automatically. The fact that an identity can query a cluster does not mean that it should read all of its secrets.

## Controlled Kubernetes operations

Operations that modify Kubernetes should be separated from queries.

```text
Read:
  list_pods
  get_deployment
  get_pod_logs

Write:
  restart_deployment
  scale_deployment
  apply_manifest

Destructive:
  delete_resource
  delete_namespace
```

Write operations should clearly state:

- Affected cluster.
- Environment.
- Namespace.
- Resource.
- Change to be performed.
- Identity being used.
- Rollback possibility.
- Confirmation requirements.

Conceptual example:

```text
Tool: scale_deployment
Namespace: staging
Deployment: api
Current replicas: 3
New replicas: 5
Confirmation required: yes
```

Destructive operations should have additional controls:

- Blocked by default.
- Limited to non-production environments.
- Protected by human confirmation.
- Limited to a resource allowlist.
- Recorded in audit logs.
- Subject to specific permissions.

## Docker operations

Docker can be used for local tasks or to manage containers on a host.

Possible use cases:

- List containers.
- Check container status.
- Read logs.
- Inspect images.
- Check resource consumption.
- Restart an authorized container.

Possible tools:

```text
list_containers
get_container_status
get_container_logs
inspect_image
restart_container
```

Access to the Docker socket requires special care. Depending on the configuration, anyone who can use it may obtain very broad permissions over the host system.

Therefore, a Docker MCP server should:

- Limit accessible containers.
- Avoid arbitrary commands.
- Restrict images and volumes.
- Avoid exposing secrets.
- Separate queries from write operations.
- Run with minimum permissions.

## Terraform

Terraform is an important use case because it combines configuration reading, change analysis, and potentially destructive modifications.

The recommended progression would be:

```text
terraform fmt
  |
  v
terraform validate
  |
  v
terraform plan
  |
  v
Human review
  |
  v
Authorized terraform apply
```

Possible tools:

```text
terraform_format
terraform_validate
terraform_plan
terraform_apply
```

Each tool should have a specific responsibility:

```text
terraform_validate:
  Validate the configuration.

terraform_plan:
  Show the expected changes.

terraform_apply:
  Execute authorized changes.

terraform_destroy:
  Must be blocked or protected by stronger controls.
```

A plan result should summarize:

- Resources to be created.
- Resources to be modified.
- Resources to be deleted.
- Potential risks.
- Workspace used.
- Affected environment.

The server should not automatically apply a plan just because the model requested it. The plan must be reviewable, and applying it must require appropriate authorization.

## CI/CD integration

MCP can be used to query and control CI/CD platforms.

Read-only use cases:

- Query executions.
- Get pipeline status.
- Read job logs.
- Find the deployed commit.
- Query artifacts.
- Identify the step that failed.

Write use cases:

- Retry a job.
- Cancel an execution.
- Create an execution.
- Promote a version.
- Deploy to an environment.

The risk difference can be summarized as follows:

```text
Query pipeline:
  Low risk.

Read execution logs:
  Low or medium risk.

Retry pipeline:
  Medium risk.

Promote a version:
  High risk.

Deploy to production:
  Very high risk.
```

Possible tools:

```text
get_pipeline_status
get_job_logs
get_deployment_commit
retry_pipeline
promote_release
```

Deployment operations should require:

- Explicit environment.
- Specific version or commit.
- Appropriate permissions.
- Confirmation.
- Auditing.
- Ability to stop the process.

## Runbook automation

MCP can help structure and execute operational runbooks.

Example runbook for an unavailable service:

```text
1. Check service status.
2. Check pods.
3. Read events.
4. Read logs.
5. Check dependencies.
6. Propose possible causes.
7. Wait for confirmation.
8. Execute an allowed action.
9. Verify recovery.
10. Record the result.
```

Prompts can help guide this flow:

```text
diagnose-service-failure
```

Tools would provide the operations:

```text
get_service_status
get_pod_logs
get_recent_events
restart_deployment
```

Resources could expose:

```text
runbook://services/api/recovery
```

The runbook must not become a global authorization. Each action still needs its own controls.

## Observability and incidents

Another use case is bringing information together from different systems to investigate an incident.

The server could:

- Query metrics.
- Correlate logs and events.
- Compare current and previous state.
- Identify recent errors.
- Prepare a timeline.
- Generate an incident summary.
- Prepare information for a postmortem.

Conceptual flow:

```text
Incident detected
  |
  +-- Query metrics
  +-- Query logs
  +-- Query recent changes
  +-- Query deployments
  +-- Correlate information
  +-- Prepare summary
  +-- Wait for operational decision
```

This use case can provide significant value while using mainly read-only permissions.

## Relationship between tools, resources, and prompts

DevOps use cases can be divided among MCP's three main building blocks:

| MCP element | DevOps use |
|---|---|
| Tool | Execute a query or action |
| Resource | Expose logs, states, documentation, or configuration |
| Prompt | Guide repeatable diagnostics and runbooks |

Example:

```text
Tool:
  get_pod_logs

Resource:
  kubernetes://clusters/staging/namespaces/api

Prompt:
  diagnose-service-failure
```

The choice depends on the nature of the content:

- If an action must be executed, it is probably a tool.
- If queryable information is exposed, it may be a resource.
- If a workflow is structured, it may be a prompt.

Not everything should become a tool. Exposing operational documentation as a resource may be more appropriate than creating a tool that returns static text.

## What the first server should not do

The first DevOps server should have a small and controlled scope.

It should not begin with:

- Arbitrary shell access.
- Access to every cluster.
- Global administrator credentials.
- Automatic production modifications.
- General access to secrets.
- Unbounded or unfiltered logs.
- A tool that combines diagnosis and destruction.
- Simultaneous access to every system in the organization.

A more reasonable starting point would be:

```text
Local server
  |
  +-- stdio
  +-- Read-only tools
  +-- Development or staging environment
  +-- Limited permissions
  +-- Automated tests
  +-- Basic auditing
```

## Recommended evolution

A possible progression for the future DevOps server would be:

```text
Phase 1:
  Local diagnostics with stdio.

Phase 2:
  Read-only tools for Docker or Kubernetes.

Phase 3:
  Resources for logs, states, and documentation.

Phase 4:
  Prompts for runbooks.

Phase 5:
  Terraform plan and change analysis.

Phase 6:
  Confirmed write operations.

Phase 7:
  Streamable HTTP and authorization.

Phase 8:
  CI/CD integration and shared environments.
```

Each phase should be completed with:

- Tests.
- Permission review.
- Documentation.
- Logs.
- Error handling.
- Risk review.

## Risk matrix

| Use case | Read | Write | Initial risk |
|---|---|---|---|
| List pods | Yes | No | Low |
| Read logs | Yes | No | Low/medium |
| Restart deployment | No | Yes | Medium |
| Scale service | No | Yes | Medium/high |
| Terraform plan | Yes | No | Medium |
| Terraform apply | No | Yes | High |
| Delete resources | No | Yes | Very high |
| Deploy to production | No | Yes | Very high |

The actual risk depends on:

- Permissions.
- Environment.
- Resource type.
- Rollback possibility.
- Human confirmation.
- Credential scope.
- Test quality.
- Available auditing.

## Key idea

The first DevOps server should start as a diagnostic and query tool, not as a complete automation system.

```text
Read
  |
  +-- Diagnose
        |
        +-- Propose action
              |
              +-- Confirmation
                    |
                    +-- Controlled write
                          |
                          +-- Verification
                                |
                                +-- Auditing
```

MCP can provide a common interface for interacting with DevOps tools, but every operation must have clear permissions, validation, and limits.

The recommended strategy is to start with read-only capabilities and gradually expand the server when it has:

- Appropriate permissions.
- Sufficient tests.
- Confirmations.
- Auditing.
- Rollback or recovery.
- Clear environment limits.

This approach prepares the way to build a reusable DevOps MCP server template without mixing every technology and risk from the beginning.

Main sources:

- [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
- [MCP Resources](https://modelcontextprotocol.io/specification/2026-07-28/server/resources)
- [MCP Prompts](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
