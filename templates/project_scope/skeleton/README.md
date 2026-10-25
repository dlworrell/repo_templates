# {{SCOPE_NAME}}

{{SCOPE_DESCRIPTION}}

Scope ID/path: `{{SCOPE_ID}}` / `{{SCOPE_PATH}}/`.
Accountable owner: `{{GITHUB_OWNER}}`.
Template source revision: `{{TEMPLATE_REVISION}}`.

The repository manifest records this scope's actual class, lifecycle, standards
and dependencies. Architecture and implementation evidence belong in `docs/`;
standards adoption records belong in `docs/engineering/`; meaningful behavioral
tests belong in `tests/`. Scope automation lives in `ci/`.

Run `bash {{SCOPE_PATH}}/ci/check.sh` from the repository root after configuring
it. The unconfigured skeleton fails visibly and does not claim verification.

Governing sources:
- https://github.com/dlworrell/Catylist/blob/{{CATYLIST_REVISION}}/docs/adr/ADR-0004-governed-project-scopes.md
- https://github.com/dlworrell/AES/blob/{{AES_REVISION}}/docs/standards/AES-003-manifest-fields.md
