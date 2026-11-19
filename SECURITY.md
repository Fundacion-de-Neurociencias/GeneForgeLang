# Security Policy

## Overview

The **GeneForgeLang (GFL)** ecosystem is dedicated to maintaining high standards of scientific integrity, biological data safety, and software security across all parser, compiler, satellite plugin, and execution components.

This project is promoted by **Fundación de Neurociencias** and developed as open-source scientific infrastructure for computational genomics and multi-omic design.

---

## Supported Versions

Only the latest active minor release receives formal security patches and vulnerability triage:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

We support and encourage coordinated, responsible vulnerability disclosure:

### Preferred Channel: GitHub Private Vulnerability Reporting
Please report vulnerabilities privately via our GitHub repository:
1. Navigate to the repository's **Security** tab.
2. Select **Advisories** and click **Report a vulnerability**.
3. Provide details including affected components, proof-of-concept (PoC), and potential impact.

### Alternative Channel: Security Contact
If you cannot use GitHub Private Vulnerability Reporting, you may email our security team directly:
- **Email**: `security@fneurociencias.org` or `info@neurociencias.org`
- **Subject**: `[SECURITY VULNERABILITY] GeneForgeLang - <Component>`

Please do **not** report security vulnerabilities through public GitHub issues or discussions.

---

## Response Timeline & Coordination Policy

When a security vulnerability report is received:
1. **Initial Acknowledgement**: Within 48 hours of submission.
2. **Impact Assessment & Triage**: Within 5 business days, confirming vulnerability scope and severity rating (CVSS).
3. **Patch Development & Validation**: A fix will be developed on an isolated private security advisory branch and validated against our automated test gates.
4. **Public Disclosure**: Coordinated disclosure will occur simultaneously with the release of the patched version, crediting the discoverer unless anonymity is requested.

---

## Automated Security Scanning

GeneForgeLang welcomes opt-in automated vulnerability analysis of open-source software. The repository currently runs:
- **GitHub Dependency Graph & Dependabot**: Automated CVE tracking for supply chain dependencies.
- **Secret scanning**: the `Secret scan` workflow runs gitleaks on pushes and pull requests.
- **Static analysis**: Ruff runs in CI on every pull request; Bandit and Mypy run as pre-commit hooks.

Automated scanning systems that discover valid vulnerabilities with verifiable PoCs are invited to submit reports directly through **GitHub Private Vulnerability Reporting** or submit non-destructive security pull requests addressing identified findings.

---

## Scope & Non-Vulnerabilities

### In Scope
- Remote code execution (RCE) or arbitrary file access through malicious `.gfl` scripts or YAML AST deserialization.
- Injection attacks in GFL parameter interpolation (`${param}`).
- Container escape or privilege escalation in `ContainerExecutor`.
- API credential leakage or unsafe transmission in satellite plugins (e.g., AlphaGenome, NCBI, ChEMBL).
- Denial of Service (DoS) resulting from algorithmic complexity attacks in AST parsing or topological graph construction.

### Out of Scope
- Denial of Service requiring physical access or root privileges on the host machine.
- Theoretical vulnerabilities without reproducible proof of concept.
- Social engineering attacks against maintainers.
