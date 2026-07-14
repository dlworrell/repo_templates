# Tests

This directory contains validation fixtures and executable tests for repository templates and lifecycle workflow contracts.

The initial executable contract is implemented by `.github/workflows/project-zero-self-test.yml`. Future template-specific fixtures should be added here when they require repository-local test data or helper programs.

Tests shall remain deterministic, portable to a clean GitHub Actions runner, and free of private infrastructure dependencies.
