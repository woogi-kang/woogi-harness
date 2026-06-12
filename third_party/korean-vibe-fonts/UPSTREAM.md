# korean-vibe-fonts upstream

Source: https://github.com/seulkikaang/korean-vibe-fonts
Pinned commit: `8ada4c61db411b3bcf9ca3a4d45857f23f0a84b9`
Imported for: Korean typography quality layer / eval-harness presets.
Repository license at review time: no repository-level LICENSE detected.

## Usage policy

- Treat this directory as a pinned reference snapshot, not an unpinned runtime dependency.
- Use the bundled catalog for typography recommendations and paste-ready CSS snippets.
- Do not present catalog license notes as legal advice; final commercial deployment should verify official font licenses.
- Prefer `recommendation_only` or self-hosted delivery for production/customer deliverables when external CDN loading is sensitive.

## Update procedure

1. Review upstream README, SKILL.md, catalog, and scripts.
2. Check whether upstream added a repository-level LICENSE.
3. Run `python3 scripts/recommend_font.py --theme "AI SaaS 랜딩 페이지" --json`.
4. Run the Korean typography eval/grader in `.claude/evals/korean-typography`.
5. Update this file with the new pinned commit and review notes.
