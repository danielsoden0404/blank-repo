---
title: CMF Status
author: Kieran Coghlan
date: 29 May 2026
---

<!--
  PANDOC COMMAND
  pandoc slides.md -o deck.pptx --to=pptx --slide-level=2 --reference-doc=reference.pptx

  SLIDE STRUCTURE
  - YAML front matter  → Title slide
  - ## heading         → Content slide (Title and Content layout)
  - # heading          → Section divider (Section Header layout)
-->

# Section One

## Bullets and Inline Formatting

- Status is good
- **Very Good!**, *On Time*, `AI Code is key`
- Nested bullet
  - Developer Experience Improved
  - Metrics on the ball

> This blockqote should render as Italic!

## Code Block

```bash
echo "This is a sample code block"
```

- Bullets and code blocks can share a slide

## Table

| Initiative | Objective | Target        | Status |
| ---------- | --------- | ------------- | ------ |
| Dev        | Build     | Docker        | Done   |
| Metrics    | SLT       | Contributions | Done   |

## Two-Column Layout

:::::: {.columns}
::: {.column}
**Left column**

- On the Left
- Left Wing
:::
::: {.column}
**Right column**

- On the right
- Right wing
:::
::::::

## Speaker Notes

- This slide hha speaker notes

::: notes
My note is that this is the note for the slide
:::
