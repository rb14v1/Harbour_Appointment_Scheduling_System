# Accepted Security Risks

This file lists dependency CVEs rated CRITICAL or HIGH that have **no fixed version available yet**
and are therefore accepted temporarily. CVEs with a fixed version are never listed here — they must be
fixed by upgrading the dependency.

Each entry needs: CVE ID, affected package and version, severity, justification, owner and next review date.

| CVE | Package (version) | Severity | Justification | Owner | Review date |
|-----|-------------------|----------|---------------|-------|-------------|
| _None_ | — | — | No unfixed CRITICAL/HIGH CVEs are currently known in `backend/requirements.txt` or `frontend/package.json`. | — | 2027-02-25 |

## Recently remediated

| CVE | Package | Severity | Fix |
|-----|---------|----------|-----|
| CVE-2025-24964 | vitest 2.1.8 | Critical | Upgraded to `^2.1.9` (`frontend/package.json`) |
| CVE-2025-13372 | Django 5.2.8 | High | Upgraded to `5.2.9` (`backend/requirements.txt`) |

## Review process

- Review this file at least every 3 months, and whenever a dependency scan reports new findings.
- When a fix becomes available for an accepted CVE, upgrade the dependency and move the entry to "Recently remediated".
