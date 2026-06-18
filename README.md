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

## Versioning

Templates are versioned like software. Projects created from a template should record the source template name and version in their project charter or README.

## License

The templates are provided under the license selected for this repository. Individual generated projects may use a different license if specified during creation.
