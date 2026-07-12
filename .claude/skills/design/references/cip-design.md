# CIP design workflow

## Responsibilities

- Search deliverable, industry, style, and mockup context data.
- Collect the real logo/source files and brand constraints.
- Route generative mockups through `image-prompt` C8 and Codex `gpt-image-2`.
- Render already-produced assets into a reviewable HTML presentation.

```bash
python3 .claude/skills/design/scripts/cip/search.py \
  "business card consulting" --cip-brief -b "BrandName"
```

The brief is compiler evidence, not a prompt. Use `scripts/cip/generate.py` only
to validate a Gongnyang JSONL plan and create output directories; the script
does not call an image model.

```bash
python3 .claude/skills/design/scripts/cip/generate.py \
  --manifest prompts.jsonl --output assets/cip
```

Use deterministic templates when exact source-logo fidelity or editable text is
required. Do not overlay native text onto a generated raster.

## Evidence lookup

```bash
python3 .claude/skills/design/scripts/cip/search.py \
  "business card letterhead" --domain deliverable
python3 .claude/skills/design/scripts/cip/search.py \
  "luxury premium elegant" --domain style
python3 .claude/skills/design/scripts/cip/search.py \
  "hospitality hotel" --domain industry
python3 .claude/skills/design/scripts/cip/search.py \
  "office reception" --domain mockup
```

Search results are structured evidence only. Do not concatenate them into a
local image prompt.

## Deliverable families

| Family | Examples |
|---|---|
| Core identity | Primary mark, lockup, monochrome and small-size variants |
| Stationery | Business card, letterhead, envelope, folder, notebook |
| Access | ID badge, lanyard, access card |
| Environment | Reception sign, wayfinding, wall graphic, meeting-room sign |
| Apparel | Shirt, jacket, cap, apron |
| Promotional | Tote, gift box, bottle, mug, umbrella |
| Vehicle | Sedan, van, truck livery |
| Digital | Social profile, email signature, slide/document template |
| Product | Packaging, label, tag, retail display |
| Event | Booth, banner stand, table cover, backdrop |

## Production decision

- Use deterministic templates for business cards, letterheads, labels, legal
  copy, dimensions, and any deliverable that must remain editable.
- Use `image-prompt` C8 for concept visualization or contextual mockups where
  the generated raster itself is the approved artifact.
- Never claim pixel-faithful logo reproduction from a generated mockup. When
  fidelity is required, place the real source logo in a deterministic layout.
- Keep print production requirements such as bleed, color space, stock, and
  finishing in the deliverable specification, outside the image prompt.

## Review presentation

```bash
python3 .claude/skills/design/scripts/cip/render-html.py \
  --brand "TopGroup" --industry "consulting" \
  --images assets/cip --output presentation.html
```

The HTML presentation is a review surface, not proof that source files are
print-ready. Check the detailed specifications in `cip-deliverable-guide.md`
and art-direction evidence in `cip-style-guide.md`.
