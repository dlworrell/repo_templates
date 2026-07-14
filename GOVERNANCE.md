# Governance

`repo_templates` is the canonical source of repository-initiation templates and lifecycle workflow entry points for the Catalyst ecosystem.

## Authority

The repository follows the authority chain:

```text
Catylist → AES → AEMS → Project Zero → repo_templates
```

- Catylist defines ecosystem structure and repository relationships.
- AES defines engineering obligations and terminology.
- AEMS manages engineering work and lifecycle state.
- Project Zero inspects, initiates, and remediates repositories.
- `repo_templates` provides the versioned files and workflows instantiated by Project Zero.

This repository does not define project-specific architecture and does not supersede the governing standards above it.

## Change Control

Changes to shared templates or lifecycle workflows shall:

1. be proposed through a pull request;
2. preserve backward compatibility where practical;
3. document migration requirements when compatibility cannot be preserved;
4. pass the Project Zero self-test and applicable repository checks;
5. avoid direct mutation of downstream default branches.

## Approval

A template change may merge after required checks pass and unresolved review findings are addressed. High-impact changes affecting all future repositories should identify their governing Catylist or AES requirement in the pull request.
