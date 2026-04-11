# Security Policy

## Reporting a vulnerability

If you believe you have found a security vulnerability in `trilium-fastmcp`, please report it privately. **Do not open a public GitHub issue.**

Preferred reporting channels:

1. **GitHub private vulnerability reporting** — use the "Report a vulnerability" button on the [Security tab](https://github.com/eliassoares/trilium-fastmcp/security) of this repository
2. **Email** — contact the maintainer directly via the email on their [GitHub profile](https://github.com/eliassoares)

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce, or a proof-of-concept
- The affected version or commit
- Any suggested mitigation, if known

You should receive an acknowledgement within a few days. The fix timeline depends on severity and complexity.

## Scope

This project is an MCP server that wraps Trilium's ETAPI. In-scope issues include:

- Authentication or authorization bypass in the MCP server itself
- Leakage of `TRILIUM_TOKEN`, `MCP_AUTH_TOKEN`, or other secrets
- Injection vulnerabilities (command injection, SSRF, etc.)
- Improper handling of user-controlled input passed to Trilium
- Dependency vulnerabilities that affect this project's runtime

Out of scope:

- Vulnerabilities in Trilium itself — please report those to [TriliumNext/Trilium](https://github.com/TriliumNext/Trilium/security)
- Vulnerabilities in FastMCP or other upstream dependencies — report to the respective maintainers
- Misconfigurations of a user's own deployment (e.g. exposing the server to the public internet without `MCP_AUTH_TOKEN`)

## Supported versions

Only the latest `main` branch is actively supported. Fixes are not backported to older tags.
