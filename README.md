# repo_templates

Canonical repository templates for Just a Geek LLC and the broader Atarix engineering ecosystem.

This repository defines repeatable starting points for new software, documentation, firmware, FPGA, and company repositories. Templates are intended to keep project layout, documentation, CI, licensing, and engineering practices consistent across all future work.

## Purpose

`repo_templates` exists to make new repositories boring, repeatable, and professional from the first commit.

Each template should provide:

- A standard directory structure.
- Baseline documentation.
- GitHub issue and pull request templates.
- CI workflow scaffolding.
- Formatting and static-analysis configuration.
- Build-system boilerplate where appropriate.
- Placeholder tokens for project-specific metadata.

## Initial Template Set

The first production milestone is `repo_templates` v1.0.

Planned templates:

- `company` — organization, business, and governance repositories.
- `c_library` — C23 static/shared library projects.
- `c_application` — C23 application projects.
- `documentation` — documentation-only repositories.

Future templates may include C++, Python, iOS, embedded firmware, FPGA, web services, research projects, and hardware projects.

Available governance scaffolds:

- [`project_scope`](templates/project_scope/README.md): a self-contained scope,
  evidence locations and a read-only root caller under Catylist ADR-0004.
- [`agent_instructions`](templates/agent_instructions/README.md): root and scope
  `CLAUDE.md` plus minimal `.claude/` routing under Catylist ADR-0005.

These scaffolds require explicit parameter replacement and project evidence;
their presence does not establish adoption, verification or production readiness.

## Proposed Layout

```text
repo_templates/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── shared/
│   ├── licenses/
│   ├── github/
│   ├── docs/
│   └── config/
├── templates/
│   ├── company/
│   ├── c_library/
│   ├── c_application/
│   └── documentation/
├── scripts/
└── examples/
```

## Placeholder Tokens

Templates use double-brace placeholders to be replaced by future tooling:

```text
{{PROJECT_NAME}}
{{PROJECT_SLUG}}
{{PROJECT_DESCRIPTION}}
{{AUTHOR_NAME}}
{{ORGANIZATION_NAME}}
{{YEAR}}
{{LICENSE}}
{{VERSION}}
{{GITHUB_OWNER}}
{{WEBSITE}}
```

## Daily, Fitment and Release Branches

Repositories that adopt Catylist ADR-0013 work in three branches: topic
branches merge into `dev-daily` (the daily merge scope), AEMS promotes
`dev-daily` into `fitment` where its agents review documentation and tests and
send findings to the authors, and `fitment` is promoted into `main` for
release. They install:

- `rulesets/protect-integration-branches.json`, applied by AEMS, which gives
  `dev-daily` and `fitment` the default-branch rules;
- `shared/github/workflows/ci.yml` as `.github/workflows/ci.yml` (or the same
  branch triggers in the repository's existing CI), with its own test command;
  and
- `shared/github/workflows/release.yml` as `.github/workflows/release.yml`,
  which tests `main` and parks at the `release` environment until the owner
  approves the tag.

Project Zero verifies adoption with the
`.aems/project-zero/profiles/adr-0013/profile.json` profile: it adds high
findings for a missing `dev-daily` or `fitment` branch, CI that does not run on
them, and a release workflow without the `release` approval gate. The default
profile is unchanged, so repositories that have not adopted ADR-0013 still
certify.

## Distributed AES-SEC-001 Controls

Native-code repositories receive the centrally maintained AEMS governance
baseline from:

- `shared/config/.clang-tidy`;
- `shared/config/clang-tidy-aes-sec-001.yml`; and
- `shared/github/workflows/aes-sec-001-governance.yml`.

The two shared Clang-Tidy files and the repository-root policy are intentionally
byte-identical. Generated repositories install either shared configuration as
`.clang-tidy` and copy the shared workflow to
`.github/workflows/aes-sec-001-governance.yml`. The workflow calls the AEMS
reusable control at `@main`, reports review-required primitives as warnings,
and blocks the adopted AES-SEC-001 banned APIs.

## Versioning

Templates are versioned like software. Projects created from a template should record the source template name and version in their project charter or README.

## License

The templates are provided under the license selected for this repository. Individual generated projects may use a different license if specified during creation.
