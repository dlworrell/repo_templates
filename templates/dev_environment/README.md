# Development environment template

Authority: Catylist [ADR-0006](https://github.com/dlworrell/Catylist/blob/main/docs/adr/ADR-0006-default-branch-protection-and-signed-commits.md),
[ADR-0007](https://github.com/dlworrell/Catylist/blob/main/docs/adr/ADR-0007-governed-check-in-and-shared-automation.md)
and [ADR-0011](https://github.com/dlworrell/Catylist/blob/main/docs/adr/ADR-0011-agent-attribution-and-trusted-contributors.md);
the setup procedure is the AEMS prompt
[`prompts/git-workflow-dev-environment.md`](https://github.com/dlworrell/AEMS/blob/main/prompts/git-workflow-dev-environment.md).

Copy into a governed repository:

| Source | Destination |
|---|---|
| `scripts/dev-setup.sh` | `scripts/dev-setup.sh` (executable) |
| `.gitmessage` | `.gitmessage` |

`scripts/dev-setup.sh --check` reports on the local clone: Git version,
identity, commit and tag signing (it never prints a key), the fetch refspec,
branch tracking, merge-based pulls and the commit template. `--fix` applies the
safe local settings it reports and nothing else. It exits 1 while anything needs
attention.

It is a convenience, not a control: the required checks in CI decide what
merges (ADR-0007 §2.3). Agents run it at the start of a session, as the
repository's `CLAUDE.md` and `AGENTS.md` say.
