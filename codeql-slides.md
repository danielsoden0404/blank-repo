---
marp: true
title: Introduction to CodeQL
description: Explanation on what CodeQL is, how it works, and how to use it effectively for static analysis.
author: Daniel Soden
theme: gaia
pagination: true
size: 16:9
lang: en
footer: "CodeQL • Static Analysis"
---
<style>
  table {
    font-size: 0.5em;
    width: 100%;
    max-width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    overflow: hidden;
    word-break: break-word;
  }
  td, th {
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>

# CodeQL

## Author: Daniel Soden

---

# What is CodeQL?

- CodeQL is a semantic code analysis tool acquired by GitHub, created by Semmle.

- Allows developers and security researchersnto write queries,
  find bugs,vulnerabilities, and code-quality issues.

- CodeQL has two states on a repo: Default Configuration and Advanced (Custom)
  configuration.

---

# CodeQL Default COnfiguration vs Advanced Configuration

## Comparison

| Aspect | Default Configuration | Advanced Configuration |
| --- | --- | --- |
| Configuration Options | No Configuration File | CodeQL.yml file describing actions taken in code scanning |
| Query Suites | Can only use either a default or extended query suite | Any query suite can be used such as security-and-quality or even security-experimental |
| Setup | Little setup effort | Requires exhaustive custom yml file with build steps |

---

# Phase 1 - Default configuration

- As of now on all public repositories, CodeQL is enabled by default.
- This means that if you have a public repository, CodeQL will automatically run on it without any additional configuration.
- For private repositories, CodeQL is not enabled by default, and you will need to set it up manually and it would require additional costs.