# Security Policy

## Supported Versions

Until the first stable release, security fixes apply to the `main` branch.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately before public disclosure.

Include:

- A clear description of the issue.
- Steps to reproduce the issue, if applicable.
- Affected files or templates.
- Potential impact.
- Suggested mitigation, if known.

## Security Expectations for Templates

Templates should avoid insecure defaults. In particular:

- Do not commit secrets or credentials.
- Do not include production tokens in examples.
- Do not disable compiler warnings without explanation.
- Prefer least-privilege CI permissions.
- Keep generated projects easy to audit.
