# Repository Lifecycle Contract

Status: Draft implementation contract

## Purpose

Every Catalyst repository shall expose stable automation entry points for repository preparation, verification, documentation and reporting, optimization experiments, and release preparation.

The canonical dependency order is:

```text
Catylist -> AES -> AEMS -> P0 -> repo_templates -> EDT / EVO / EWT -> project repositories
```

## Required workflow entry points

| Workflow | Responsibility | Mutation policy |
|---|---|---|
| `p0.yml` | Inspect, plan, remediate, verify, or assess readiness | Remediation only through a branch and pull request |
| `verify.yml` | Execute repository verification and preserve evidence | Read-only |
| `documentation.yml` | Inventory documentation and produce a report package for EDT | Read-only |
| `compliance.yml` | Verify baseline repository and AES-adoption obligations | Read-only |
| `optimization.yml` | Define and record EVO experiments and candidate measurements | Read-only; no production mutation |
| `release.yml` | Prepare and validate a release evidence package | Read-only unless a later approved release implementation is installed |

Each workflow shall:

1. support `workflow_dispatch` for mobile operation;
2. publish a useful GitHub step summary;
3. produce machine-readable JSON and human-readable Markdown evidence;
4. upload its evidence even when validation fails;
5. avoid direct writes to the default branch;
6. use deterministic inputs and identify the commit under evaluation.

## Verified remediation commits (AES-DEV-001-R005)

Every commit that can reach a default branch must be GitHub-verified
(ADR-0006 rule 5; AES-DEV-001-R001 and AES-DEV-001-R005). Automation therefore
shall not create commits with a local `git commit` and `git push` from a runner,
because those bot commits are unsigned and cannot merge once
`required_signatures` is enforced.

The Project Zero workflow (`.github/workflows/project-zero.yml`, invoked by
`p0.yml`) implements this requirement. With `mode: remediate` and
`mutation_policy: open-remediation-pr` it:

1. runs `tools/project_zero_commit.py`, which stages only the remediation paths
   and exits as a no-op when nothing changed;
2. creates the `p0/remediation-<run id>` branch through the REST API from the
   base branch HEAD if it does not exist, refusing to continue if that HEAD has
   moved since checkout;
3. creates the commit with the GraphQL `createCommitOnBranch` mutation using the
   workflow `GITHUB_TOKEN` (file contents base64-encoded in `fileChanges`,
   guarded by `expectedHeadOid`), so GitHub signs it; and
4. opens a pull request against the base branch.

The helper refuses to write to the base or default branch and refuses to run for
`pull_request_target` events. The checkout does not persist credentials because
no local push is performed. File modes are not carried by
`createCommitOnBranch`; remediation stubs are regular text files.

## Local interfaces

Repositories should expose equivalent local commands through scripts or task runners. GitHub Actions and local execution must call the same underlying implementation rather than maintaining separate policy logic.

## Extension boundary

The template workflows establish stable interfaces. Domain implementations may replace their internal commands while preserving workflow names, inputs, evidence locations, and safety guarantees.
