---
title: Introduction to CodeQL
author: Daniel Soden
date: April 28, 2026
---

# CodeQL

## What is CodeQL?

* CodeQL is a semantic code analysis tool acquired by GitHub, created by Semmle.
* Allows developers and security researchers to write queries, find bugs, vulnerabilities, and code-quality issues.
* CodeQL has two states on a repo: Default Configuration and Advanced (Custom) configuration.

## Default vs Advanced Configuration

| Aspect | Default Configuration | Advanced Configuration |
| --- | --- | --- |
| Configuration Options | Query suite, Runner type, Threat Model | CodeQL.yml file |
| Query Suites | Default or extended only | Any suite, including security-experimental |
| Setup | Little setup effort | Requires exhaustive custom yml with build steps |

# Rollout Phases

## Phase 1 — Default Configuration

* CodeQL is enabled by default on all public repositories — no configuration needed.
* For private repositories, CodeQL must be set up manually and requires additional costs.

## Phase 2 — Extended Suite

* Security extended includes:
  * Additional low precision and low severity queries
  * Experimental queries
* Broader coverage of potential vulnerabilities than the default suite.

## Notes on Extended and Advanced Configuration

* Can produce a large number of alerts, including false positives.
* Code owners decide whether to dismiss alerts.
* String operations, library calls, and typing are more likely to be flagged — even if not exploitable in practice.

## How Will We Implement the Extended Suite?

* Add code scanning endpoints for:
  * Editing Default configuration
  * Getting Default configuration
* Record metadata for the default and extended configuration.

# Metadata for CodeQL Configuration

## Disabled

```json
"codeql": "disabled"
```

CodeQL is not enabled — no code scanning will be performed.

## Default

```json
"codeql": "default"
```

CodeQL is enabled with the default configuration and default query suite.

## Extended

```json
"codeql": "extended"
```

CodeQL is enabled with the default configuration and security-extended query suite.

## Advanced

```json
"codeql": "advanced"
```

CodeQL uses a custom `codeql.yml` configuration. In the get request, codeql will be `not-configured`, but Code Scanning UI will show code issues.

# Phase 3 — Advanced Configuration

## Advanced Configuration

* Repository maintainers will automatically use the custom CodeQL configuration via `codeql-caller.yml`, which calls `codeql-ccp-common.yml` from build_tools_workflows.
* This greatly increases the number of code issues found — code owners must triage and manage alerts.

## Conclusion

* Next steps: push endpoint changes live, record metadata, and start rollout of the extended suite to all public repositories.
* Scripts have been created to aid in this process and will be shared with the team.
