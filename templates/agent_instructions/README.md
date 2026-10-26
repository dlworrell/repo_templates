# Agent instruction templates

Authority: Catylist [ADR-0005](https://github.com/dlworrell/Catylist/blob/main/docs/adr/ADR-0005-agent-instruction-files.md).
These files route agents to the repository's authoritative sources and contain
no duplicated standards. Replace parameters with observed repository facts.

Copy `root/CLAUDE.md` and `root/AGENTS.md` to the repository root and
`root/.claude/` alongside them. `AGENTS.md` serves agents other than Claude
(ChatGPT, Notion and others) with the same routing.
The empty `settings.json` grants no extra tools or permissions. Append
`**/.claude/settings.local.json` to the repository ignore file; never copy local
settings or credentials. The shared ignore template already supplies this rule.
Copy `scope/CLAUDE.md` into a declared top-level scope when scope context helps.

Fill `REPOSITORY_NAME`, `REPOSITORY_PURPOSE`, `REPOSITORY_LAYOUT`,
`TEST_COMMAND`, `SCAN_COMMAND`, `LOCAL_CONVENTIONS`, `TEMPLATE_REVISION`,
`CATYLIST_REVISION`, `AES_REVISION`, `AEMS_REVISION`, `ADR_LOG_PATH`,
`SCOPE_NAME` and `SCOPE_PATH` from evidence.
If information is unavailable, record the missing evidence rather than inventing
a command, convention or approval. Existing instruction files require review;
this is not authorization to overwrite them.
