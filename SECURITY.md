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

- Do not commit secrets or credentials. `shared/config/.gitignore` blocks common
  credential files (environment files, private keys and key stores, tool and
  cloud credential files, secret files, and infrastructure state); generated
  repositories should install it as `.gitignore`. Ignore rules are a guard
  against accidents, not a control: keep CI/CD secrets in GitHub Actions
  secrets or environments, and enable secret scanning and push protection.
- If a secret is ever pushed, revoke and rotate it first, then remove it from
  history; deleting the file in a later commit leaves it readable.
- Do not include production tokens in examples.
- Do not disable compiler warnings without explanation.
- Prefer least-privilege CI permissions.
- Keep generated projects easy to audit.
