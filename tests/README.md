# Tests

This directory contains validation fixtures and executable tests for repository templates and lifecycle workflow contracts.

The initial executable contract is implemented by `.github/workflows/project-zero-self-test.yml`. Python unit tests live in this directory as `test_*.py` and use only the standard library. Run them with:

```bash
python3 -m unittest discover -s tests
```

`test_project_zero_commit.py` covers the verified-commit helper used by the Project Zero remediation workflow (AES-DEV-001-R005).

Future template-specific fixtures should be added here when they require repository-local test data or helper programs.

Tests shall remain deterministic, portable to a clean GitHub Actions runner, and free of private infrastructure dependencies.
