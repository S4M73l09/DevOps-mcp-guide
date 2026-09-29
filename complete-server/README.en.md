# Complete Server [ES](README.md)

## Purpose

Complete DevOps MCP server intended to be used as a practical reference within this guide.

## Base structure

The current structure of this practical example provides a basic but sufficient configuration for an `MCP` server.

```text
complete-server/
├── fixtures/
│   ├── terraform/
│   │   └── basic               # Basic Terraform structure.
│   ├── docker/
│   │   └── compose             # Docker Compose files and images.
│   └── kubernetes/
│       ├── base                # Base cluster structure.
│       └── overlays             # Separate environments for the cluster.
│           ├── development/
│           ├── production/
│           └── staging/
├── integrations/
│   ├── github_client.py        # GitHub Actions CI/CD integration.
│   ├── gitlab_client.py        # GitLab CI/CD integration.
│   └── jenkins_client.py       # Jenkins CI/CD integration.
├── security/
│   ├── __init__.py
│   ├── receipt.py
│   └── signing.py
├── tests/
│   ├── test_gitlab_ci.py
│   ├── test_jenkins_ci.py
│   ├── test_server.py
│   ├── test_security.py
│   └── test_tool_receipts.py
├── tools/
│   ├── __init__.py
│   ├── diagnostics.py          # Diagnostics for server initialization.
│   ├── docker.py
│   ├── github_actions.py
│   ├── gitlab_ci.py
│   ├── jenkins_ci.py
│   ├── kubernetes.py
│   ├── receipt_support.py
│   └── terraform.py
├── .env.example                # Example environment variables.
├── .python-version             # Required Python version, currently 3.13.
├── config.py
├── mcp-inspector.json
├── pyproject.toml
├── README.md
├── README.en.md
├── server.py
└── uv.lock                     # Generated and maintained by uv.
```

> Note: Python 3.13 is recommended in this example because of blocking issues observed in the tests with the current MCP and AnyIO combination.

> Because of compatibility issues with some synchronous tools, this example uses an earlier supported Python version. A newer Python version can still be used, but all existing tools may need to be converted to `async def`.

`uv` can install and manage its own Python interpreter without replacing the system Python installation.

## Test configuration (`fixtures`)

This example server uses `fixtures` for critical DevOps tools such as `Terraform`, `Docker`, and `Kubernetes`. This keeps real operations isolated from reproducible examples and allows:

- Reproducible tests.
- README examples.
- Safer validations.
- Tests without credentials or external infrastructure.

The [`diagnostics.py`](tools/diagnostics.py) tool is also used to verify that the server initialized correctly.

# Fixtures

The server uses the fixture system described above to demonstrate the available DevOps tools. This system can be extended as the server grows.

## Basic Terraform fixture

This fixture is used by the complete MCP server to demonstrate formatting, validation, and planning for `IaC` environments using `Terraform`.

The example uses `terraform_data`, so it does not require cloud provider credentials or external infrastructure.

### Commands used

Run these commands from the fixture directory:

```bash
terraform fmt -check
terraform init -backend=false
terraform validate
terraform plan -var-file=terraform.tfvars.example
```

This fixture only supports `read-only` validation and planning.

The current example does not use `terraform apply` or `terraform destroy` because of deployment safety concerns.

Those operations can be added for your own use, but they become your responsibility. Add policies, security controls, guardrails for agentic models, periodic logs, and signed receipts where stronger reproducibility is required.

The basic configuration is available here: [terraform-fixtures](fixtures/terraform/basic/)

The tools for this fixture are implemented here: [terraform.py](tools/terraform.py)

## Docker

This fixture uses images in a `docker-compose.yaml` file containing a PostgreSQL database, the `Adminer` database administrator, `Prometheus` metrics collection, and `Grafana` metrics visualization.

The example includes `.env.example` variables. Images also use reproducible `digest + tag` references.

The Docker tools validate and inspect containers. As with Terraform, tools that deploy or update containers require additional policies, guardrails, validation, and human confirmation.

### Tool functionality

The Docker tools can discover Compose files, inspect images declared in a Compose file, and show the general status of its containers.

```text
register_docker_tools
├── docker_list_compose_files  -- Lists Compose files in a target directory.
├── docker_compose_config      -- Shows a specific Compose configuration.
├── docker_compose_images      -- Lists images declared in a Compose file.
├── docker_image_inspect       -- Inspects a specific image from the previous result.
└── docker_compose_ps          -- Shows the general container status.
```

The implementation is available here: [docker.py](tools/docker.py)

## Kubernetes

The Kubernetes fixture contains an example cluster configuration for demonstrating Kubernetes tools inside the `MCP` server.

It contains the basic resources required for the example. Images use immutable `digest + tag` references. It does not include secrets, Ingress, LoadBalancer, RBAC permissions, or mutating operations because those depend on the user's infrastructure and security policies.

This example uses a base and three overlays:

- `development`
- `staging`
- `production`

```text
fixtures/kubernetes/
├── base/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── development/
    │   └── kustomization.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── production/
        └── kustomization.yaml
```

The Kubernetes tools are:

1. `kubernetes_current_context`: Shows the active Kubernetes context.
2. `kubernetes_list_namespaces`: Lists available namespaces.
3. `kubernetes_list_pods`: Lists pods in a namespace.
4. `kubernetes_list_deployments`: Lists deployments in a namespace.
5. `kubernetes_list_services`: Lists services in a namespace.
6. `kubernetes_list_events`: Queries recent events to detect problems.
7. `kubernetes_validate_manifest`: Validates a YAML manifest or Kustomize overlay using client-side dry-run without applying changes.
8. `kubernetes_validate_cluster`: Validates against the context or API of an existing cluster without applying changes.

Both validation tools can generate a `signed receipt` when they receive `"include_receipt": true`.

Offline and online validation serve different purposes. Offline validation checks the local construction of overlays. Online validation can detect issues related to the real cluster version, policies, and admission controllers.

The implementation is available here: [kubernetes.py](tools/kubernetes.py)

## CI/CD

This section describes tools for current CI/CD platforms: `GitHub Actions`, `GitLab`, and `Jenkins`.

### GitHub Actions

The GitHub Actions integration provides:

1. `github_list_workflows`: Lists workflows.
2. `github_list_workflow_runs`: Lists workflow runs.
3. `github_get_workflow_run`: Gets a specific workflow run.
4. `github_list_run_jobs`: Lists jobs belonging to a workflow run.

These tools use GitHub's API through `GET` requests and require:

```text
owner
repo
```

The required variables are available in [`.env.example`](.env.example).

They can be exported before starting the server:

```bash
set -a
source .env
set +a
uv run mcp run server.py
```

They can also be configured directly in `mcp-inspector.json`:

```json
{
  "mcpServers": {
    "devops-complete-server": {
      "command": "uv",
      "args": ["run", "mcp", "run", "server.py"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_API_URL": "https://api.github.com",
        "GITHUB_API_VERSION": "2026-03-10"
      }
    }
  }
}
```

> Important: `.env.example` only documents the required variables. Configure the values before starting the server. Never include a real token in `.env.example` or commit it to the repository.

The server does not load `.env` automatically. Variables must be exported manually or configured in MCP Inspector.

### GitLab

The GitLab integration follows the same general structure as GitHub Actions, while using GitLab terminology, endpoints, and authentication.

The tools are:

1. `gitlab_list_pipelines`
2. `gitlab_get_pipeline`
3. `gitlab_list_pipeline_jobs`

These tools use the GitLab API. The required variables are available in [`.env.example`](.env.example):

```env
GITLAB_TOKEN=replace-with-a-read-only-token
GITLAB_API_URL=https://gitlab.com/api/v4
```

The variables can also be configured in `mcp-inspector.json`:

```json
{
  "mcpServers": {
    "devops-complete-server": {
      "command": "uv",
      "args": ["run", "mcp", "run", "server.py"],
      "env": {
        "GITLAB_TOKEN": "${GITLAB_TOKEN}",
        "GITLAB_API_URL": "https://gitlab.com/api/v4"
      }
    }
  }
}
```

As with GitHub Actions, variables must be exported manually or configured in MCP Inspector. Never include a real token in `.env.example` or commit it to the repository.

### Jenkins

Jenkins requires a more careful design. The `controller` decides where jobs run, while `agents` provide executors. Each executor represents a unit of concurrent execution.

Jenkins recommends avoiding direct job execution on the built-in controller node for security and isolation reasons.

The initial Jenkins integration is read-only and provides:

1. `jenkins_server_info`
2. `jenkins_list_jobs`
3. `jenkins_get_job`
4. `jenkins_list_builds`
5. `jenkins_get_build`
6. `jenkins_get_build_console`
7. `jenkins_get_queue`
8. `jenkins_list_agents`

These tools can:

- Query the controller version and status.
- List jobs and pipelines.
- Query the latest or a specific build.
- Read build states such as `SUCCESS`, `FAILURE`, `ABORTED`, and `UNSTABLE`.
- Read queue information.
- Show connected and offline agents and their executors.
- Read console logs for a specific build.

Jenkins provides a REST-like remote API through `/api/` endpoints with JSON responses for querying jobs, builds, and the queue. Build triggering is possible, but it is intentionally excluded from this initial read-only integration because it changes external state.

## Signed receipts in DevOps tools

The server can generate a `signed receipt` as verifiable evidence for selected operations.

A receipt does not execute an action or authorize a change. It demonstrates that a tool received specific input and produced specific output.

The flow is:

```text
tool input
     |
validation
     |
operation execution
     |
result
     |
input and output hashes
     |
optional digital signature
     |
signed receipt
```

### Why is everything not signed?

Not every tool needs signed evidence. Simple queries such as listing pods or namespaces usually only need a conventional audit log. Receipts are reserved for results that are especially important or may need later verification.

In this example server, receipts can be useful for:

- `terraform_plan`;
- `docker_compose_images`;
- `docker_image_inspect`;
- `kubernetes_validate_manifest`;
- future deployment or promotion operations.

Signed receipts are currently available in:

- `terraform_plan`;
- `docker_compose_images`;
- `kubernetes_validate_manifest`.

These tools accept:

```json
{
  "include_receipt": true,
  "actor": "local-user"
}
```

Receipts do not replace:

- authorization;
- human confirmation;
- checking the real state;
- access controls;
- conventional audit logs.

Query tools such as `kubernetes_list_pods`, `kubernetes_list_services`, and `kubernetes_list_events` return normal responses and do not currently generate receipts.

### Enabling a receipt

Compatible tools include:

```json
{
  "include_receipt": true
}
```

When the parameter is `false`, the tool returns only its normal result. When it is `true`, it adds a signed `receipt` object.

Conceptual example:

```json
{
  "tool": "docker_compose_images",
  "ok": true,
  "status": "images_found",
  "count": 4,
  "receipt": {
    "action": "docker_compose_images",
    "actor": "local-user",
    "environment": "development",
    "target": "fixtures/docker/compose/Db-Observ-compose.yaml",
    "input_hash": "...",
    "output_hash": "...",
    "key_id": "...",
    "signature": "..."
  }
}
```

### What does a receipt contain?

A receipt includes:

- the operation performed;
- the associated actor;
- the environment;
- the target resource or path;
- an input hash;
- an output hash;
- the public key identifier;
- the digital signature.

The private key is never included in the response.

### Signing providers

The current example server supports three modes:

| Mode | Key storage | Use case |
|---|---|---|
| `ephemeral` | Memory | Quick tests |
| `local` | Protected local file | Development and Inspector |
| `production` | KMS, HSM, or secret manager | Real environments |

The `signing_provider` is created once when the server starts and shared with tools that can generate receipts. This prevents a different key from being created for every operation.

The private key is never included in a receipt or tool response.

### What a receipt does and does not prove

A valid receipt proves that:

- specific input was processed;
- specific output was produced;
- the signed content was not altered;
- the server used a specific key.

It does not, by itself, prove that an external resource was successfully modified. That still requires validation, authorization, human confirmation, and a later check of the real state.

Receipts complement existing security controls; they do not replace them.

The security files are available here: [security](security/), [receipt_support.py](tools/receipt_support.py), [test_security.py](tests/test_security.py), and the server security integration in [server.py](server.py).

## Commands used

Synchronize the project and its dependencies:

```bash
uv sync
```

Start MCP Inspector:

```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server devops-complete-server
```

Run tests and check for syntax errors or other discrepancies:

```bash
uv run pytest
```

Additional commands will be documented as the server grows.
