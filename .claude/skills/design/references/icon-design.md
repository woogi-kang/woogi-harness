# Icon workflow

Choose one production lane.

## Generated raster icon

Use `image-prompt` C9, the upstream validator, and Codex `$imagegen`
(`gpt-image-2`). The compiler owns every prompt decision.

## Editable SVG icon

Use an existing icon library or deterministic code/vector tooling. The local
`scripts/icon/generate.py` command only normalizes and validates an existing SVG
source; it does not call a language or image model.

```bash
python3 .claude/skills/design/scripts/icon/generate.py \
  --input icon.svg --output icon-normalized.svg --size 24 --color '#6366F1'
```

Do not convert a generated raster into an allegedly source-quality SVG without
human inspection. Preserve provenance for every derived artifact.

## Evidence axes

These labels guide brief classification and source-library lookup. They are not
local prompt suffixes.

| Style | Typical use |
|---|---|
| Outlined / thin | Dense product UI, tables, toolbars |
| Filled / glyph | Compact navigation and selected states |
| Duotone | Marketing and onboarding support |
| Rounded | Friendly consumer and health products |
| Sharp / geometric | Technical and enterprise products |
| Flat | Simple product and documentation graphics |
| Tactile / 3D | Generated campaign or app-icon concept |
| Pixel / hand-drawn | Deliberately expressive brand systems |
| Animated-ready | Motion systems with explicit path constraints |

| Category | Examples |
|---|---|
| Navigation | Arrow, menu, home, chevron |
| Action | Edit, delete, save, download, upload |
| Communication | Mail, chat, phone, notification |
| Media | Play, pause, volume, camera |
| File | Document, folder, archive, cloud |
| User | Person, group, profile, settings |
| Commerce | Cart, wallet, card, receipt |
| Data | Chart, analytics, dashboard |
| Development | Code, terminal, bug, git, API |
| Social | Heart, star, bookmark, trophy |
| Weather / map | Sun, cloud, rain, pin, compass, globe |

## SVG quality gate

- Use a stable `viewBox` and test at the actual smallest size.
- Prefer `currentColor` when the icon belongs to UI chrome.
- Keep paths and nodes minimal; do not embed fonts, scripts, remote assets, or
  raster data.
- Provide an accessible label where the icon is not purely decorative.
- Keep stroke width, cap, join, optical size, and bounding-box rhythm consistent
  across the set.
- Treat multi-size exports as deterministic derivatives of one reviewed source.
