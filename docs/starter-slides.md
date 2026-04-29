---
title: Markdown Template For PowerPoint Generation 
subtitle: Reusable patterns and best practices for pandoc-based slide decks. 
author:
   - Daniel Soden 
   - Comcast/RDK/RDKM/CMF 
date: 2026-04-28
lang: en-IE
subject: PowerPoint generation with pandoc 
description: Reusable pandoc-first markdown template for PowerPoint generation.
keywords:
   - pandoc
   - pptx
   - markdown
monofont: Aptos Mono
notes: |
   Opening script for the title slide.
   Mention the audience, the goal of the deck, and the expected outcome.
---

# Opening

## Executive Summary

- State the problem, decision, or proposal in one sentence.
- Put the most important takeaway in the first three bullets.
- Keep each bullet short enough to fit on one line when possible.
- Use speaker notes for detail instead of overloading the slide.

::: notes

Use this slide to frame the presentation in under one minute.

- Why this matters now
- What decision is needed
- What the audience should remember

:::

## How This Template Maps To PowerPoint

- Document metadata builds the title slide.
- Level 1 headings create section header slides.
- Level 2 headings create normal content slides.
   - A `columns` container triggers a two-column PowerPoint layout.
   - Text followed by a table or image can trigger a caption-oriented layout.
- A `notes` container becomes speaker notes in PowerPoint.

## Workflow Assumptions

- This file is designed for `pandoc input.md -t pptx --reference-doc=reference.pptx -o output.pptx`.
- Your reference deck should define these layout names: Title Slide, Title and Content, Section Header, Two Content, Comparison, Content with Caption, and Blank.
- Prefer relative paths for local media so the GitHub Action can resolve them consistently.
- Avoid raw HTML and format-specific hacks unless you also control the conversion command.

# Core Content

## Standard Content Slide

- Use this pattern for status, decisions, risks, and next steps.
- Put supporting detail in notes, appendices, or backup slides.
- Favor one idea per slide over dense mixed content.

### Suggested Structure

1. Headline with the conclusion.
2. Two to four supporting points.
3. One visual, metric, or decision if needed.

## Incremental Talking Points

::: incremental

- First point the audience should absorb.
- Second point that builds on the first.
- Third point that leads into the recommendation.

:::

Use incremental lists sparingly. They work best for paced narration, not dense reference slides.

## Code Example

```python
from pathlib import Path

for slide_file in sorted(Path(".").glob("**/*slides*.md")):
    print(slide_file)
```

- Keep code-only slides short enough to read from the back of the room.

## Table Slide

| Track | Owner | Status | Next Milestone |
|:------|:------|:-------|:---------------|
| Authoring | Docs Team | On track | Draft review |
| Styling | Design Ops | At risk | Update reference deck |
| Automation | Platform | On track | CI validation |

: Delivery status snapshot.

::: notes

Call out the one row that needs attention.

If a table becomes hard to read, split it across multiple slides or convert it into a chart.

:::

## Definition And Quote Slide

Key term
: A short definition written in plain language.

Another term
: A second definition when the audience needs shared vocabulary.

> Use block quotes for a short source statement, customer quote, principle, or policy excerpt.

# Layout Patterns

## Two-Column Slide

:::::::::::::: {.columns}
::: {.column width="50%"}
### Left Column

- Main argument
- Supporting context
- Constraints or assumptions
:::
::: {.column width="50%"}
### Right Column

- Recommendation
- Expected outcome
- Owner and timing
:::
::::::::::::::

## Comparison Layout Slide

:::::::::::::: {.columns}
::: {.column width="45%"}
### Current State

- Manual updates
- Inconsistent formatting
- No shared reference deck
- Review friction across teams
:::
::: {.column width="55%"}
### Proposed State

- Reusable slide template
- GitHub Action conversion
- Reference-driven visuals
- Faster review and release
:::

## Image Pattern

Use real project assets in production decks. Keep image paths relative to the markdown file or repository root.

```markdown
![Architecture overview](images/architecture-overview.png){ width=75% }

: Architecture overview for release 3.
```

- `width=75%` is a practical default for large visuals.
- An image by itself in a paragraph becomes a figure with a caption.
- Prefer PNG, JPEG, or other assets that your pipeline already handles reliably.

## Math And Inline Formatting

- Inline math works for simple expressions such as $E = mc^2$.
- Display math works for formulas that need separation from body text.
- Standard emphasis such as **bold**, *italic*, and `inline code` converts cleanly.

$$
	ext{Risk Score} = \frac{\text{Impact} \times \text{Likelihood}}{\text{Controls}}
$$

# Delivery Guidance

## Authoring Checklist

1. Replace the metadata block with the real title, authors, date, and description.
2. Keep section titles at level 1 and slides at level 2.
3. Use notes for narration and detail that should not appear on the slide.
4. Keep code, tables, and visuals large enough to read at presentation scale.
5. Verify the deck against your `reference.pptx` before relying on final layout.

## Optional Extensions

- Add a bibliography only if your workflow is extended with `--citeproc` and bibliography sources.
- Add background images through the reference PowerPoint, not ad hoc markdown hacks, when you want consistent slide branding.
- Add local diagrams or screenshots once the asset paths are stable in the repository.

::: notes

This slide is a good place to explain any team-specific conventions:

- file naming
- ownership
- review process
- release cadence

:::

# Appendix

## Backup Slide

- Supporting detail
- Alternate option
- Open questions
- Data source notes

## Closing Slide

- Restate the decision, ask, or next action.
- Include owner, timeline, and approval path if relevant.
- Keep the final slide simple enough to leave on screen during Q and A.

