---
marp:true
pagination:true
theme: default
---

<style>
  table {
    font-size: 0.5em;
    height: 80%;
    width: 80%;
    border-collapse: collapse;
  }
</style>
# GitHub Code Scanning with Coverity — Presentation Slides


---

## Slide 1: Overview

**Integrate Coverity with GitHub Code Scanning via SARIF**

- Coverity results appear **natively in GitHub** — inline PR annotations, Security tab, check runs
- Developers never leave their workflow
- One-time dismissals, automatic deduplication, policy enforcement at merge

> **Coverity finds it. SARIF carries it. GitHub surfaces it. Developers fix it — without ever leaving their workflow.**

---

## Slide 2: Prerequisites — What You Need

| Requirement | Detail |
|---|---|
| **GitHub plan** | GitHub Team or Enterprise — **GitHub Code Security** must be enabled per private repository |
| **Token permissions** | `security_events: write` scope (fine-grained PAT or GitHub Actions) |
| **SARIF version** | 2.1.0 only |
| **File size** | ≤ 10 MB gzip-compressed |
| **Coverity** | Access to Coverity server + ability to export results |
| **Custom converter** | Transforms Coverity output → SARIF 2.1.0 |
| **Jenkins** | Job to run scan, convert, and upload on PR and main branch events |

> Without Code Security enabled on a private repo, all uploads return HTTP 403.

---

## Slide 3: What is SARIF?

### SARIF = Static Analysis Results Interchange Format

- **OASIS standard** (version 2.1.0) — a universal JSON format for static analysis output
- Accepted by GitHub, Azure DevOps, VS Code, and more
- Supported by many scanning tools: **Coverity**, **CodeQL**, **Snyk**
- Native SARIF 2.1.0 export **availability varies by Coverity version**; a custom converter is the standard approach for GitHub integration

### Why It Matters
| Without SARIF | With SARIF |
|---|---|
| Results locked in Coverity portal | Results in GitHub Security tab |
| Manual triage in separate tool | Inline PR annotations |
| No merge blocking | Configurable PR gates |
| Tool-specific format | Portable across platforms |

---

## Slide 4: The Integration Flow

```
Coverity Static Analysis
        │
        ▼
  Custom Converter
  (Coverity → SARIF 2.1.0)
        │
        ▼
  GitHub Code Scanning API
  POST /repos/{owner}/{repo}/code-scanning/sarifs
        │
        ▼
  GitHub extracts: rule ID, severity,
  file location, CWE tags (where mapped), fingerprint
        │
        ▼
  Inline PR annotations
  Security tab alerts
  Automated check runs
```

> Coverity's deep analysis appears in GitHub's UI — no portal access needed.

---

## Slide 5: How GitHub Processes a SARIF Upload

### 7-Step Pipeline

| Step | What Happens |
|---|---|
| **1. Upload** | `POST` gzip+base64 encoded SARIF to GitHub API |
| **2. Validation** | Schema check, size limits, commit SHA & ref validation |
| **3. Extraction** | Rule ID, severity, file paths, CWE tags extracted per result |
| **4. Deduplication** | Fingerprints compared — same fingerprint = same alert |
| **5. Baseline Comparison** | PR alerts vs. base branch — only NEW alerts surfaced |
| **6. State Management** | Alerts tracked as open, dismissed, or fixed (independent states) |
| **7. UI Presentation** | Security tab + PR annotations + check run status |

---

## Slide 6: Fingerprints — Why They Matter

### What is a Fingerprint?
A stable identifier that lets GitHub track the **same issue across commits** — even when surrounding line numbers shift.

### The Problem Without Good Fingerprints
- Developer inserts a comment above a bug → line numbers shift
- GitHub sees a new fingerprint → **old alert closes as Fixed, new alert opens**
- Any dismissal on the old alert is **lost** — the reopened alert blocks PRs again
- On an active codebase this compounds: phantom Fixed/New pairs accumulate every sprint

---

## Slide 7: Fingerprints — The Solution

Hash **line content** (not line number) — content only changes when the actual defect changes:

```python
raw = f"{rule_id}:{file_path}:{line_content.strip()}"
fingerprint = hashlib.sha256(raw.encode()).hexdigest()[:16] + ":1"
```

| What shifts | Fingerprint stable? |
|---|---|
| Unrelated code inserted above defect | ✅ Yes — content unchanged |
| Defect line itself edited | ❌ No — content changed (correct behaviour) |
| File renamed / moved | ❌ No — path changed |

---

## Slide 8: Two Types of Coverity Scans

### Full Scan — on `main` after merge
- Analyzes **entire codebase**, commits to Coverity database (baseline)
- Uploads all findings to GitHub Security tab

### Differential Scan — on every PR
- Analyzes **changed files only** against baseline
- Reports only **NEW defects**

```
PR → Differential Scan → Only NEW issues in PR
Merge → Full Scan → Updates baseline → Next PR uses it
```

> ⚠️ Differential scans **require** an existing baseline — full scan must run first.

---

## Slide 9: PR Integration — What Developers See

### GitHub compares fingerprints automatically

```
main branch:  [Alert A] [Alert B]
PR branch:    [Alert A] [Alert C]  ← new

GitHub PR shows: 1 new alert (Alert C)
Alert A is hidden — it already exists in main
```

### What a developer sees
- ❌ New `RESOURCE_LEAK` detected in `src/memory.c:42`
- Inline annotation on the changed line in the PR diff
- "Code scanning" check fails — merge is blocked until resolved or dismissed
- No access to Coverity portal required

---

## Slide 10: Dismissals — Managing False Positives

### Dismiss once → suppressed across the entire repository

When a finding is dismissed on any branch, GitHub stores the decision on the **alert record** (keyed by fingerprint). Any future PR that introduces a finding with the same fingerprint inherits the dismissal automatically.

| Field | Example |
|---|---|
| `dismissed_by` | The user who dismissed |
| `dismissed_at` | `2026-03-09T14:23:01Z` |
| `dismissed_reason` | `false positive` · `won't fix` · `used in tests` |
| `dismissed_comment` | Free-text justification |

### Key behaviours
- Dismissal is **repository-global** — not scoped to a branch or commit
- A new SARIF upload for the same fingerprint **does not clear the dismissal**
- Dismissals survive across sprints until explicitly reopened
- Full audit trail: who, when, why — visible in the Security tab

---

## Slide 11: Merge Blocking — How It Works

### How the block works
- SARIF upload triggers a **Check Run** named `"Code scanning / Coverity"` on the commit
- Without a Ruleset or branch protection: check run is **informational only** — no merge is blocked
- **Rulesets** (Settings → Rules → Rulesets) are recommended — they provide per-tool, per-severity thresholds
- Branch protection rules can also make the check required, but without per-severity control

### Setting up the Ruleset (`main` branch)
1. Enable **"Require code scanning results"**
2. Add tool: **`Coverity`**
3. Set both threshold rows independently:

**Alerts** — based on SARIF `level`
| Threshold | Blocks on |
|---|---|
| `Errors` | SARIF `level: error` (Coverity High-impact) |
| `Errors and Warnings` | `level: error` or `warning` |
| `All` | Any level |

---

## Slide 12: Merge Blocking — Security Alert Thresholds

**Security alerts** — based on `security-severity` score
| Threshold | Blocks on |
|---|---|
| `Critical` | Score > 9.0 only |
| `High or higher` ✅ | Score ≥ 7.0 (High + Critical) |
| `Medium or higher` | Score ≥ 4.0 |

> `inject-security-severity.py` adds per-checker scores to the SARIF before upload — this threshold row is fully active. Set to `High or higher` to block on Critical and High findings.

---

## Slide 13: Merge Blocking — Recommended Configuration

### Recommended configuration
| Tool | Alerts | Security alerts | What blocks |
|---|---|---|---|
| **Coverity** | `Errors` | `High or higher` | Coverity High/Critical findings (`level: error` + score ≥ 7.0) ✅ |
| **CodeQL** | `Errors` | `High or higher` | CodeQL High/Critical + `level: error` ✅ |

**Notes:**
- ℹ️ `inject-security-severity.py` adds per-checker `security-severity` scores and CWE tags to the SARIF before upload. **Both** threshold rows are active.
- ⚠️ Only **new findings introduced by the PR** trigger the block — existing `main` baseline findings do not.

---

## Slide 14: Configuration & Benefits Summary

### For Developers
- ✅ Inline PR annotations — fix issues without leaving GitHub
- ✅ Only NEW issues shown in PRs — no legacy noise
- ✅ Dismiss once, applies everywhere

### For Security / Compliance Teams
- ✅ Full audit trail — who dismissed what and why
- ✅ Configurable PR blocking on Critical/High findings
- ✅ Severity classification from Coverity impact levels; Security severity scores available via post-processing

### For Infrastructure / Operations
- ✅ Coverity server stays internal — only outbound SARIF uploads
- ✅ Fewer Coverity portal licenses needed
- ✅ GitHub manages UI, scaling, and alert database

---

## Slide 15: Multiple Build Configurations

### Separate build targets — use different `tool_name` values
- e.g., `Coverity-Native`, `Coverity-Device`, `Coverity-Firmware`
- Each tool name maintains its own independent alert tracking in GitHub

### Multiple branches — use same `tool_name` with different `ref` values
- Upload with `ref: refs/heads/main`, `refs/heads/develop`, `refs/heads/master`
- Each branch maintains its own independent baseline (open/fixed state is per-branch — but dismissals are repository-wide, as covered in Slide 10)

---

## Slide 16: Severity — Two Separate Fields (1/2)

### GitHub tracks TWO severity fields from SARIF

**Field 1: Severity** — from SARIF `level`
| SARIF `level` | GitHub Severity | Coverity impact |
|---|---|---|
| `error` | Error | High |
| `warning` | Warning | Medium |
| `note` | Note | Low |

> The converter maps Coverity impact to `level`. Both severity fields are active — `level` drives the Alerts threshold; `security-severity` drives the Security alerts threshold.

---

## Slide 17: Security Severity (2/2)

**Field 2: Security Severity** — from `security-severity` score
| Score | Security Severity |
|---|---|
| > 9.0 | Critical |
| 7.0 – 8.9 | High |
| 4.0 – 6.9 | Medium |
| 0.1 – 3.9 | Low |

> `inject-security-severity.py` injects per-checker scores into the SARIF before upload. Both severity columns appear in the Security tab for every Coverity alert. The Security alerts Ruleset threshold is fully active.

---

## Slide 18: Adding `security-severity` Scores

### Post-processing the Coverity SARIF with `inject-security-severity.py`

`cov-format-sarif-for-github.js` does not emit `security-severity`. The post-processing script runs **after** conversion but **before** gzip/upload:

```
cov-format-sarif-for-github.js → coverity.sarif
        │
        ▼
  inject-security-severity.py
  (per-checker scores, CWE tags, "security" tag)
        │
        ▼
  gzip + base64 → upload to GitHub
```

### Multi-tier severity lookup

The script resolves each rule's score via a multi-tier lookup:

| Tier | Match | Example |
|---|---|---|
| **1a** | Multi-segment key in 122-entry `CHECKER_TABLE` (3-seg → 2-seg → 1-seg) | `OVERRUN/overrun/write` → `("9.1", 119)` |
| **1b** | Dotted prefix (`PW.*`, `RW.*`) | `PW.BAD_PRINTF_FORMAT_STRING` → `"3.0"` (Low) |
| **2** | `defaultConfiguration.level` fallback | `error` → `"8.0"`, `warning` → `"6.0"`, `note` → `"3.0"` |

### Representative per-checker scores

| Band | Score | Example checkers |
|---|---|---|
| Critical | `"9.1"` | `OVERRUN`, `USE_AFTER_FREE`, `UNINIT`, `DOUBLE_FREE`, `TAINTED_STRING` |
| High | `"7.5"`–`"8.0"` | `FORWARD_NULL`, `RESOURCE_LEAK`, `NULL_RETURNS`, `INTEGER_OVERFLOW` |
| Medium | `"6.0"` | `CHECKED_RETURN`, `COPY_PASTE_ERROR`, `MISSING_BREAK` |
| Low | `"3.0"` | `DEADCODE`, `UNUSED_VALUE`, `PASS_BY_VALUE`, `PW.*`, `RW.*` |

> Scores are JSON **strings** (e.g. `"8.0"`). The script also injects a `"security"` tag and CWE tags (e.g. `"external/cwe/cwe-476"`) into each rule's `properties.tags[]`. Fine-grained multi-segment entries provide more precise CWE mappings (e.g. `TAINTED_STRING/tainted_string_sql` → CWE-89). See GITHUB_SARIF_PROCESSING.md §5 for the full 122-entry checker table.

---

## Notes — Slide 1: Overview

The goal of this integration is to surface Coverity findings directly inside GitHub, eliminating the need for developers to access the Coverity portal. Currently, acting on a finding requires leaving GitHub, accessing a separate tool, locating the finding, cross-referencing it with the code, then returning to GitHub to make the fix. This integration removes those steps. Full scan results are uploaded to GitHub and appear in the Security tab under Code Scanning — giving the team a centralised view of all open findings across the repository. For pull requests, Coverity results also appear as inline annotations on the exact line of code, at the time of code review.

---

## Notes — Slide 2: Prerequisites

Three hard blockers before any SARIF upload will work on a **private repository**. First, GitHub Code Security must be enabled on the repository — without it, every upload returns HTTP 403. On the GitHub Team plan this is a per-repository toggle, not automatic. For **public repositories**, Code Scanning is available on all plans without enabling Code Security — the HTTP 403 and the toggle do not apply. Second, the token used for the upload must have `security_events: write` permission — a classic PAT needs the `security_events` scope; a fine-grained PAT or GitHub Actions token needs the explicit `Code scanning alerts: write` permission. Third, a custom converter is required to produce SARIF 2.1.0 from Coverity output — the converter is already built and handles all repositories through the same pipeline.

---

## Notes — Slide 3: What is SARIF?

SARIF is an open standard ratified by OASIS in 2020. It provides a common JSON format for static analysis output, accepted by GitHub, Azure DevOps, VS Code, and other platforms. Many scanning tools support SARIF natively — including CodeQL (GitHub’s own scanner), Snyk. This means GitHub Code Scanning is not limited to Coverity — any tool that produces SARIF 2.1.0 can feed into the same Security tab, check runs, and Ruleset thresholds. Because native SARIF 2.1.0 export availability varies by Coverity version and configuration, a custom converter is the standard approach for transforming Coverity’s output into SARIF 2.1.0 format. Once that converter exists, it handles all repositories and all scans through the same pipeline without per-repository configuration.

---

## Notes — Slide 4: The Integration Flow

Coverity runs static analysis as normal. The output is passed through the converter, producing a SARIF 2.1.0 file. A post-processing step (`inject-security-severity.py`) then enriches each rule with a per-checker `security-severity` score, a `"security"` tag, and a CWE tag (e.g. `"external/cwe/cwe-476"`) before the file is uploaded to GitHub via a single API call. GitHub parses each finding, extracts rule ID, severity, file location, and CWE tags, and generates a fingerprint for tracking across commits. Not all checkers have CWE mappings — for those without one, the CWE field will be blank. Results appear in GitHub as inline PR annotations, Security tab alerts, and check run statuses. The Coverity server remains internal — only the SARIF output is transmitted to GitHub.

---

## Notes — Slide 5: How GitHub Processes a SARIF Upload

GitHub processes uploaded SARIF through a 7-step pipeline. The deduplication step uses fingerprints to match findings across scans — the same finding in consecutive scans is tracked as one alert, not duplicated. The baseline comparison step compares the PR branch fingerprints against the base branch. Only findings not present in the base branch are surfaced in the PR. Existing findings on main are not shown. This keeps PR results scoped to what the current change introduced.

---

## Notes — Slide 6: Fingerprints — Why They Matter

A fingerprint is a hash that lets GitHub track the same finding across commits. Without a stable fingerprint, even a routine refactor — inserting a comment or a helper function above a defect — shifts line numbers, which causes GitHub to close the old alert as Fixed and open a brand new one. Any dismissal on the old fingerprint is permanently lost. On an active codebase with many developers this compounds rapidly: after a few sprints the Security tab Fixed count is noise and dismissed false positives keep blocking PRs.

---

## Notes — Slide 7: Fingerprints — The Solution

The fix is to hash the content of the flagged line, not the line number. Line content only changes when the actual defect changes — surrounding edits don't affect it. The converter already generates content-based fingerprints.

---

## Notes — Slide 8: Two Types of Coverity Scans

There are two scan types with distinct roles. The full scan analyzes the entire codebase, commits results to the Coverity database, and establishes the baseline used for all subsequent differential comparisons. It runs post-merge on main because it takes hours. The differential scan runs on every PR — it analyzes only the changed files, compares against the Coverity database baseline, and reports only findings not already present in that baseline. A differential scan cannot run without an existing baseline. The full scan must complete first.

---

## Notes — Slide 9: PR Integration — What Developers See

When a PR is opened, GitHub compares the fingerprints from the PR branch against the base branch baseline. Only findings with fingerprints not present in the base branch are surfaced. Existing baseline findings are not shown. New findings appear as inline annotations on the changed lines in the PR diff and the Code scanning check fails, blocking the merge. Developers see the finding, the rule, the severity, and the exact line — without ever leaving GitHub or accessing the Coverity portal.

---

## Notes — Slide 10: Dismissals — Managing False Positives

Dismissals are written to the alert record — the repository-level object keyed by fingerprint. This means a dismissal is global: it is not scoped to a branch or a commit. Once dismissed on any branch, every future PR that introduces a finding with the same fingerprint inherits the dismissal automatically — the alert is suppressed without any manual intervention. This is because the dismiss API (`PATCH /code-scanning/alerts/{number}`) has no `ref` parameter — it operates on the alert by its repository-wide number. Supported reasons are `false positive`, `won't fix`, and `used in tests`. The dismissal persists across SARIF uploads — a new scan for the same fingerprint does not clear it. To reverse, a user or API call must explicitly reopen the alert. Note: PR suppression of dismissed alerts has been confirmed for PRs targeting the default branch; the exact behaviour for PRs targeting non-default branches has not been independently verified.

---

## Notes — Slide 11: Merge Blocking — How It Works

Merge blocking is not automatic. Uploading a SARIF file creates a check run named "Code scanning / Coverity" on the commit — but without enforcement configured, that check run is purely informational. There are two mechanisms for enforcement: Repository Rulesets (recommended) provide per-tool, per-severity thresholds — navigate to Settings → Rules → Rulesets, create a rule targeting the main branch, enable "Require code scanning results", add Coverity as the tool, and set the two threshold rows independently. Branch protection rules can also make the check required, but without per-severity control — they simply pass or fail based on whether any alerts exist.

---

## Notes — Slide 12: Merge Blocking — Security Alert Thresholds

The Security alerts threshold row evaluates the `security-severity` numeric score embedded in the SARIF rule properties. `inject-security-severity.py` injects per-checker scores into every rule before upload, so this threshold row is fully active. Set it to `High or higher` to block PRs that introduce Critical or High severity findings.

---

## Notes — Slide 13: Merge Blocking — Recommended Configuration

Both threshold rows are active. Set Alerts to `Errors`: the converter maps Coverity High-impact findings to `level: error`, so every High-impact finding introduced by a PR blocks the merge. Medium and Low findings do not block under `Errors`. Set Security alerts to `High or higher`: `inject-security-severity.py` adds per-checker scores, so this row evaluates every finding — checkers scored ≥ 7.0 (High and Critical bands) block the merge through this row as well.

The block applies only to new findings introduced by the PR. Existing findings already in the main baseline are not evaluated. A dismissed finding on main is automatically suppressed in future PRs via fingerprint matching.

---

## Notes — Slide 14: Configuration & Benefits Summary

For developers: findings appear as inline PR annotations scoped to new issues only — existing baseline findings are not shown. Developers do not need access to the Coverity portal. For security and compliance teams: every dismissal is recorded with a timestamp, a username, and a reason. Merge blocking is configurable by severity threshold via Repository Rulesets — with `inject-security-severity.py` adding per-checker scores, both the Alerts row (`Errors`) and the Security alerts row (`High or higher`) are active gates. Each Coverity checker is scored individually (99 base checkers plus 23 fine-grained sub-checker/event entries, 122 total, mapped across Critical, High, Medium, and Low bands). CWE tags and a `"security"` tag are injected into each rule’s `properties.tags[]` — GitHub displays the CWE in the alert detail and uses the security tag for classification. For infrastructure and operations: the Coverity server has no inbound exposure — only SARIF output is transmitted outbound to GitHub. Developers do not require Coverity portal licences, reducing the total licence count.

---

## Notes — Slide 15: Multiple Build Configurations

For multiple build targets, use a different `tool_name` for each — GitHub tracks alerts independently per tool name, so separate firmware, native, and device builds each maintain their own alert set. For multiple branches, use the same `tool_name` but upload with the correct `ref` value for each branch — GitHub maintains an independent baseline per ref, so `main`, `develop`, and `master` each track their own open/fixed state independently. However, dismissals are always repository-wide — dismissing an alert on one branch dismisses it on all branches.

---

## Notes — Severity: Two Separate Fields

GitHub tracks two independent severity fields — both are now active for Coverity alerts. The first is Severity, derived from the SARIF `level` field. The converter maps Coverity impact to `level`: High → `error`, Medium → `warning`, Low → `note`. GitHub displays this as Error, Warning, or Note on every alert, and the Alerts threshold row in Repository Rulesets evaluates this field. The second is Security severity, derived from the `properties.security-severity` numeric score on each rule. GitHub requires the rule's `properties.tags[]` to include `"security"` for this field to activate. GitHub translates the score using CVSS v3.1 qualitative bands: over 9.0 = Critical, 7.0–8.9 = High, 4.0–6.9 = Medium, 0.1–3.9 = Low. When a Security severity is present, GitHub displays it in preference to the basic Severity.

`inject-security-severity.py` is deployed and runs after `cov-format-sarif-for-github.js` but before gzip/upload. It walks the SARIF `runs[].tool.driver.rules[]` array and injects three things into each rule: (1) a `properties.security-severity` string with a per-checker score from a 122-entry `CHECKER_TABLE`, (2) a `"security"` tag in `properties.tags[]` so GitHub activates the Security severity classification, and (3) a CWE tag (e.g. `"external/cwe/cwe-476"`) where a mapping exists. Scores are resolved via a multi-tier lookup: first by multi-segment key (3-seg → 2-seg → 1-seg, covering 122 entries across Critical at `"9.1"`, High at `"7.5"`–`"8.0"`, Medium at `"6.0"`, Low at `"3.0"`), then by dotted prefix (`PW.*` / `RW.*` → `"3.0"`), and finally by `defaultConfiguration.level` as a fallback. Fine-grained multi-segment entries provide more precise CWE mappings for specific sub-checker/event combinations (e.g. `TAINTED_STRING/tainted_string_sql` → CWE-89 instead of the base CWE-78). The value must be a JSON string — GitHub ignores numeric types. With per-checker scores present, the Security severity column appears in GitHub for every Coverity alert, and the Security alerts threshold row in Repository Rulesets is fully active. The full 122-entry checker table and implementation details are documented in GITHUB_SARIF_PROCESSING.md §5.
