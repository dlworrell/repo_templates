# {{REPOSITORY_NAME}} agent context

Purpose: {{REPOSITORY_PURPOSE}}
Layout: {{REPOSITORY_LAYOUT}}
Template source revision: {{TEMPLATE_REVISION}}

## Read first

Read `README.md`, `aes-manifest.yaml`, applicable scope READMEs, and their linked
architecture, specifications, ADRs and engineering evidence before changing code.
The manifest and owning documents determine applicability and authority.

## Ring 0

- The Catylist Code of Conduct binds every change here; this repository adopts
  it as `{{ADR_LOG_PATH}}/ADR-0000-catylist-code-of-conduct.md`.
- At the start of a session, run `scripts/dev-setup.sh --check` and work as the
  AEMS Git workflow prompt describes.
- Start every post, pull request body, review and comment you write with
  `**<Agent> for @<prompting user>**` (Catylist ADR-0011).

## Repository commands and conventions

- Tests: `{{TEST_COMMAND}}`
- Local scan: `{{SCAN_COMMAND}}`
- Observed conventions: {{LOCAL_CONVENTIONS}}

## Authoritative references

- https://github.com/dlworrell/Catylist/blob/{{CATYLIST_REVISION}}/CODE_OF_CONDUCT.md
- https://github.com/dlworrell/Catylist/blob/{{CATYLIST_REVISION}}/docs/adr/ADR-0000-catylist-code-of-conduct.md
- https://github.com/dlworrell/Catylist/blob/{{CATYLIST_REVISION}}/docs/adr/ADR-0004-governed-project-scopes.md
- https://github.com/dlworrell/Catylist/blob/{{CATYLIST_REVISION}}/docs/adr/ADR-0005-agent-instruction-files.md
- https://github.com/dlworrell/Catylist/blob/{{CATYLIST_REVISION}}/docs/adr/ADR-0006-default-branch-protection-and-signed-commits.md
- https://github.com/dlworrell/Catylist/blob/{{CATYLIST_REVISION}}/docs/adr/ADR-0007-governed-check-in-and-shared-automation.md
- https://github.com/dlworrell/Catylist/blob/{{CATYLIST_REVISION}}/docs/adr/ADR-0011-agent-attribution-and-trusted-contributors.md
- https://github.com/dlworrell/AES/blob/{{AES_REVISION}}/standards/AES-DEV-001-development-principles-and-check-in-discipline.md
- https://github.com/dlworrell/AEMS/blob/{{AEMS_REVISION}}/prompts/git-workflow-dev-environment.md

These references own the requirements; this context file does not restate them.
