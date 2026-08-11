# Contributing

Thank you for contributing to this guide about MCP applied to DevOps.

## Project goal

This guide aims to explain MCP progressively and build practical examples of MCP servers focused on DevOps.

## Types of contributions

- Corrections to technical or language-related errors.
- Documentation improvements.
- Translations between Spanish and English.
- New MCP examples.
- Diagrams and visual materials.
- Use cases for Kubernetes, Terraform, Docker, CI/CD, or observability.
- Security or clarity improvements.

## Documentation structure

- `docs/es/`: Spanish documentation.
- `docs/en/`: English documentation.
- `examples/`: Progressive examples.
- `complete-server/`: Complete reference MCP server.
- `diagrams/`: Project diagrams.

## Bilingual documentation

Each new chapter should include:

- A version in `docs/es/`.
- An equivalent version in `docs/en/`.
- Links between both versions.
- Updated links from `docs/README.md`.

Conceptual changes should be applied to both languages.

## Sources and references

Important technical statements should be based on official MCP documentation or primary sources.

The sources used should be added to:

- `docs/SOURCES.md`

When a section depends on a specific MCP version, the relevant version should be stated.

## Documentation conventions

- Use clear and structured Markdown.
- Keep internal tables of contents up to date.
- Prefer small, progressive examples.
- Explain the concept before showing the code.
- Avoid presenting destructive actions as the default.
- Document risks and limitations in DevOps examples.

## Code examples

Examples should:

- Be executable, or clearly state when they are conceptual.
- Have a focused responsibility.
- Validate their inputs.
- Avoid arbitrary commands.
- Contain no real secrets.
- Explain which transport they use.
- Include a way to test them.

## Security

Examples should prioritize:

- Read-only operations.
- Allowlists.
- Parameter validation.
- Time and output limits.
- Human confirmation for sensitive operations.
- Protection of secrets and internal data.

## Pull requests

A contribution should verify:

- That the Markdown renders correctly.
- That internal links work.
- That the Spanish and English versions are synchronized.
- That examples contain no secrets.
- That the documentation reflects the MCP version being used.
- That the changes remain within the chapter's scope.

## Commit style

Use clear commit messages, for example:

- `docs: add MCP resources chapter`
- `docs: translate tools chapter`
- `fix: correct architecture links`
- `example: add Kubernetes read-only server`
