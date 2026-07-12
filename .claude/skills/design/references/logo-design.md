# Logo design workflow

## Responsibilities

- Search local style/color/industry data and produce a design brief.
- Route generative concepts through `logo-creator` and `image-prompt`.
- Preserve source raster, user selection, and derived artifacts.

```bash
python3 .claude/skills/design/scripts/logo/search.py \
  "tech startup modern" --design-brief -p "BrandName"
```

The search result is evidence, not an image prompt. `image-prompt` owns prompt
authoring and Codex `$imagegen` with `gpt-image-2` owns generation. This
reference does not define local templates or model choices.

After selection, deterministic crop, background processing, or vector tracing
may create derived artifacts. Keep the original raster and provenance manifest.

## Evidence lookup

```bash
# Style evidence
python3 .claude/skills/design/scripts/logo/search.py \
  "minimalist clean" --domain style

# Palette evidence
python3 .claude/skills/design/scripts/logo/search.py \
  "tech professional" --domain color

# Industry evidence
python3 .claude/skills/design/scripts/logo/search.py \
  "healthcare medical" --domain industry
```

The following axes are brief vocabulary, not prompt suffixes.

| Axis | Options |
|---|---|
| Mark structure | Wordmark, lettermark, pictorial, abstract, mascot, emblem, combination |
| Visual register | Minimal, corporate, luxury, playful, organic, editorial, vintage |
| Geometry | Geometric, monoline, negative space, fragmented, responsive/adaptive |
| Surface | Flat, line art, duotone, tactile, 3D/isometric, motion-ready |

## Color and industry evidence

| Color family | Common association | Typical domains |
|---|---|---|
| Blue/navy | Trust, stability | Finance, technology, healthcare |
| Green | Growth, natural systems | Sustainability, wellness, food |
| Red/orange | Energy, appetite, urgency | Food, sports, entertainment |
| Gold/black | Premium, heritage | Luxury, hospitality, jewelry |
| Purple | Creativity, innovation | Beauty, creative tools, technology |

Treat these as hypotheses to validate against the actual brand. Do not let a
generic industry default override project evidence or an existing identity.

## Review sequence

1. Validate the brief against brand name, audience, use sizes, and trademark risk.
2. Compile separate `image-prompt` records for materially different concepts.
3. Review legibility at favicon, app-icon, header, and print sizes.
4. Preserve the chosen raster and record every crop/vector derivative.
5. Use `design-harness` for the selection gallery and independent visual QA.

Detailed local evidence remains in `logo-style-guide.md` and
`logo-color-psychology.md`; prompt construction remains exclusively upstream.
