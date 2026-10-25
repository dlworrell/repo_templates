# Changelog

All notable changes to `repo_templates` will be documented in this file.

This project follows semantic versioning once the first tagged release is created.

## [Unreleased]

### Changed

- Project Zero remediation pull requests now carry GitHub-verified commits
  created through the GraphQL `createCommitOnBranch` API
  (`tools/project_zero_commit.py`) instead of unsigned local `git commit` /
  `git push`, implementing AES-DEV-001-R005 (Catylist ADR-0006 rule 5). The
  `project_zero` template (now 0.2.0) distributes the helper, and the checkout
  no longer persists credentials.

### Added

- Governed project-scope and agent-instruction scaffolds for Catylist #26,
  citing ADR-0004/0005, with read-only CI wiring, visible unconfigured failure
  and ignored personal agent settings.

- Initial repository purpose and roadmap.
- Planned template categories for company, C library, C application, and documentation repositories.
- Versioned repository ruleset definitions in `rulesets/` (`protect-default-branch`, `protect-release-tags`) consumed by AEMS, with `tools/verify_rulesets.py` and tests enforced in `verify.yml`.
