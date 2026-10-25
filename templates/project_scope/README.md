# Governed project-scope template

Authority: Catylist [ADR-0004](https://github.com/dlworrell/Catylist/blob/main/docs/adr/ADR-0004-governed-project-scopes.md)
and AES [AES-003](https://github.com/dlworrell/AES/blob/main/docs/standards/AES-003-manifest-fields.md).
This template supplies wiring and record locations, not policy or a compliance verdict.

Copy `skeleton/` to a distinct top-level `{{SCOPE_PATH}}/`, copy the caller
example to `.github/workflows/{{SCOPE_ID}}.yml`, and replace every double-brace
parameter. Record this template's exact source revision. Merge the example
scope entry into the repository manifest using the current AES-003 contract.
Review class, lifecycle, dependencies and standard applicability from actual
evidence; the example intentionally contains unresolved applicability tokens.

Implement meaningful checks in the scope's `ci/check.sh` and tests before using
the caller as a gate. The supplied check deliberately exits 2 until configured.
Retrieve applicable adoption profiles and record waivers/dispositions through
their owning authority. A directory of empty evidence files is not adoption.

Optional scope agent context is supplied by `templates/agent_instructions/scope/`.
No root or scope-local logic is executed with a write token or self-hosted runner
in this example; the caller has read-only permissions and ordinary PR triggers.

Parameters: `SCOPE_ID`, `SCOPE_PATH`, `SCOPE_NAME`, `SCOPE_DESCRIPTION`,
`GITHUB_OWNER`, `CATYLIST_REVISION`, `AES_REVISION`, `TEMPLATE_REVISION`,
`STANDARD_APPLICABILITY`, `APPLICABILITY_REASON`.
