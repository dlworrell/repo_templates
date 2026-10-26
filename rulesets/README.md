# Repository Rulesets

Versioned GitHub repository ruleset definitions for Catylist-governed
repositories. AEMS applies these files to existing repositories, and new
repositories created from `repo_templates` start from them.

## Files

| File | Target | Purpose |
| --- | --- | --- |
| `protect-default-branch.json` | branch (`~DEFAULT_BRANCH`) | Blocks deletion and force-push of the default branch, requires signed commits, and requires every change to land through a pull request merged with a merge commit. No approving review count is required, so a sole maintainer can merge their own pull request. |
| `protect-release-tags.json` | tag (`refs/tags/v*`) | Blocks deletion, force-update, and any update of release tags once created. |
| `protect-integration-branches.json` | branch (`dev-daily`, `fitment`) | The same rules as the default branch for the daily merge scope and the fitment branch (Catylist ADR-0013). Because the branches cannot be deleted, merging a promotion pull request never removes them. |

No ruleset defines bypass actors. Repository administrators are subject
to the same rules as every other contributor.

The paths and file names are a consumed interface: AEMS fetches exactly
`rulesets/protect-default-branch.json`, `rulesets/protect-release-tags.json`
and `rulesets/protect-integration-branches.json`. Renaming or moving any of
them is a breaking change.

## Authority

- Catylist ADR-0006 (repository protection and merge policy).
- Catylist ADR-0013 (daily, fitment and release branches).
- AES-DEV-001 requirements R001 through R007.

## Matching Repository Merge Settings

The default-branch ruleset allows only the `merge` method. Configure the
repository merge settings to match, otherwise the merge button offers methods
the ruleset rejects:

| Setting | Value |
| --- | --- |
| `allow_merge_commit` | `true` |
| `allow_squash_merge` | `false` |
| `allow_rebase_merge` | `false` |
| `delete_branch_on_merge` | `true` |

## How the Rulesets Are Applied

The AEMS workflow `apply-catylist-rulesets.yml` fetches these files from
`dlworrell/repo_templates` at a pinned commit SHA and applies them to target
repositories. Pinning means a change here has no effect on any repository
until AEMS is updated to reference the new SHA.

### Manual Fallback

If the AEMS workflow is unavailable, apply a ruleset with the GitHub CLI using
a token that has administration rights on the target repository:

```sh
gh api --method POST /repos/{owner}/{repo}/rulesets \
  --input rulesets/protect-default-branch.json

gh api --method POST /repos/{owner}/{repo}/rulesets \
  --input rulesets/protect-release-tags.json
```

`POST` creates a new ruleset. If a ruleset with the same name already exists,
list rulesets with `gh api /repos/{owner}/{repo}/rulesets`, then update it with
`gh api --method PUT /repos/{owner}/{repo}/rulesets/{ruleset_id} --input <file>`
instead of creating a duplicate.

Apply the matching merge settings with:

```sh
gh api --method PATCH /repos/{owner}/{repo} \
  -F allow_merge_commit=true \
  -F allow_squash_merge=false \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true
```

## WARNING: Do Not Add Unmet Requirements

Do not add `required_status_checks` or `code_scanning` rules to these files,
and do not add them to a repository's ruleset, until those checks actually run
and report in the target repository.

The 2026-10-15 sandbox test (`dlworrell/ruleset-sandbox`) showed that a
required check that never reports blocks every merge, including pull requests
whose commits are fully signed and otherwise compliant. There is no bypass
actor to recover with, so an unmet requirement locks the default branch.

`required_linear_history` is also excluded: it conflicts with the merge-commit
policy above.

`tools/verify_rulesets.py` enforces these exclusions in CI.

## Required Status Checks (Proposed, Not Enabled)

Required status checks are intentionally absent from the shared baseline
because each repository runs different workflows. They are chosen per
repository from the check names reported by the latest successful run on that
repository's default branch, and enabled separately from this baseline, as a
reviewed change to that repository's ruleset, only after the checks are
confirmed to run on every pull request.
