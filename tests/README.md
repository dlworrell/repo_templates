<!--
SPDX-FileCopyrightText: 2026 Donovan Worrell and Just a Geek LLC

SPDX-License-Identifier: Apache-2.0
Catalyst-File-ID: urn:uuid:793c62d6-b4f0-4096-a8ab-4d57bebad931
-->

# Tests

This directory contains validation fixtures and executable tests for repository templates and lifecycle workflow contracts.

The initial executable contract is implemented by `.github/workflows/project-zero-self-test.yml`. Python unit tests live in this directory as `test_*.py` and use only the standard library. Run them with:

```bash
python3 -m unittest discover -s tests
```

`test_project_zero_commit.py` covers the verified-commit helper used by the Project Zero remediation workflow (AES-DEV-001-R005).

Future template-specific fixtures should be added here when they require repository-local test data or helper programs.

`test_rulesets.py` validates the shared ruleset definitions in `rulesets/` through `tools/verify_rulesets.py`. Run it with `python3 -m unittest discover -s tests`.

Tests shall remain deterministic, portable to a clean GitHub Actions runner, and free of private infrastructure dependencies.
