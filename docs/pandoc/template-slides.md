--- 
title: Markdown to PPTX — Pandoc Feature Reference
author: Your Name
date: 27 May 2026
---

## Slide 1: Title Slide

This is a new line I want to see a regeneration of the title slide
The YAML front matter block at the top of this file produces the title slide.

- `title:` → main title text
- `author:` → subtitle / author line
- `date:` → date line below author

Pandoc maps this metadata to the **Title Slide** layout in the reference `.pptx`. Only one title slide is ever generated.

## Slide 2: Content Slides

Every `## ` heading starts a new **Title and Content** slide.

- The heading text becomes the slide title
- All content beneath it fills the body placeholder
- Blank lines between items are ignored

> A `# ` heading with no body content creates a **Section Header** slide using the Section Header layout from the reference `.pptx`.

# Section Divider Example

## Slide 3: Bullet Points

Both `*` and `-` markers create bullet points.

* Extra bullet point
* This bullet uses an asterisk
- This bullet uses a dash
- This bullet uses a dash and has **bold text** and `inline code`

Bullet styling — font, size, colour, indent — is inherited from the **Title and Content** layout in the reference `.pptx`.

## Slide 4: Inline Formatting

Inline markdown is parsed inside bullets, plain text, and blockquotes.

- `**double asterisks**` → **bold**
- `*single asterisks*` → *italic*
- `` `backticks` `` → `monospace`
- Combinations: **bold and *italic* together**
- Inline code example: `os.path.join(dir, file)`

> Inline formatting is stripped to plain text inside table cells.

## Slide 5: Sub-Headings

### This is a sub-heading (###)

Sub-headings use `### ` (three hashes) and render as bold paragraphs inside the slide body. They are useful for labelling sections within a dense slide.

### Another Sub-Heading

- Bullets can follow a sub-heading
- They appear inside the same body placeholder

## Slide 6: Blockquotes

Blockquotes use `> ` and render as italic text.

- Regular bullet before the quote
- Another regular bullet

> A single blockquote line — renders as italic.

> A second blockquote on the same slide — each `> ` line is its own italic paragraph.

> **Bold text inside a blockquote** renders as bold-italic.

## Slide 7: Fenced Code Blocks

Code blocks use triple backticks and render in a monospace font.

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"

print(hello("world"))
```

The language hint after the opening backticks (e.g. `python`) is passed through but does not affect PPTX rendering. Font styling is controlled by the reference `.pptx` theme.

## Slide 8: Code Block — Shell Example

```bash
# Convert markdown to PPTX using a reference template
pandoc slides.md \
  -o presentation.pptx \
  --to=pptx \
  --slide-level=2 \
  --reference-doc=reference.pptx
```

Code blocks can appear alone or after bullet points on the same slide.

## Slide 9: Tables

Tables render as a PPTX table shape positioned below the slide title.

| Column A | Column B | Column C |
|---|---|---|
| Row 1A | Row 1B | Row 1C |
| Row 2A | Row 2B | Row 2C |
| Row 3A | Row 3B | Row 3C |

The separator row (`|---|---|`) is automatically skipped. Inline markdown in cells is stripped to plain text.

## Slide 10: Tables After Bullets

When a table follows bullet points on the same slide, it is rendered below the text in the body placeholder.

- This bullet appears in the body text frame
- So does this one

| Threshold | Blocks on |
|---|---|
| Errors | level: error |
| Errors and Warnings | level: error or warning |
| All | Any level |

## Slide 11: Mixed Content — Bullets and Code

A slide can contain both bullet points and a code block.

- Step 1: install Pandoc
- Step 2: run the converter

```bash
pandoc slides.md -o deck.pptx --to=pptx --reference-doc=reference.pptx
```

## Slide 12: Two-Column Layout

Use Pandoc fenced divs to create a **Two Content** slide layout from the reference `.pptx`.

:::::: {.columns}
::: {.column}
**Left column**

- First point
- Second point
- Third point
:::
::: {.column}
**Right column**

- Fourth point
- Fifth point
- Sixth point
:::
::::::

## Slide 13: Speaker Notes

Add speaker notes with a fenced `notes` div after slide content. Notes appear in Presenter View only.

- Main bullet one
- Main bullet two

::: notes
These notes are visible in Presenter View but not on the slide itself.
Only the speaker sees this text during the presentation.
:::
