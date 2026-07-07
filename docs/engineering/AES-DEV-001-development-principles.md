# AES-DEV-001 Local Profile

Status: Active
Owner: repo_templates
Repository: `dlworrell/repo_templates`

## Inheritance

This repository inherits `AES-DEV-001: Development Principles and Check-In Discipline`.

Governing standard:

```text
dlworrell/AES/standards/AES-DEV-001-development-principles-and-check-in-discipline.md
```

## Repository Role

repo_templates defines the repository standard that Catalyst repositories default to or start with.

## Documentation Authority

Documentation authority is local to this repository for repository layout, shared template files, default policies, bootstrap conventions, and common repository structure.

Authoritative paths:

- `README.md`
- `shared/docs/`
- `shared/config/`
- `docs/`

## Local Expectations

Template changes should be broadly reusable and should not silently impose project-specific assumptions on all Catalyst repositories.

Changes to default policy, default directory structure, or shared workflow conventions should include rationale and migration guidance.

## Deviations

Local deviations from AES-DEV-001 require an ADR, design note, or explicit waiver recorded in the repository.
