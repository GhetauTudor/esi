# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |

## Reporting a Vulnerability

If you discover a security vulnerability in ESI, please **do not** open a public GitHub issue.

Instead, report it privately:

1. Go to the [Security tab](https://github.com/GhetauTudor/esi/security) on GitHub
2. Click **"Report a vulnerability"**
3. Describe the issue, steps to reproduce, and potential impact

You will receive a response within **72 hours**. We take all reports seriously and will coordinate a fix and disclosure timeline with you.

## Scope

ESI is a memory abstraction library. Security-relevant areas include:

- Data leakage between memory namespaces
- Injection via memory content passed to backends
- Unsafe deserialization in backend integrations

Thank you for helping keep ESI secure.
