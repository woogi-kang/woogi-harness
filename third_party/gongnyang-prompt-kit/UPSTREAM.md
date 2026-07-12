# Gongnyang Prompt Kit provenance

The runtime files under `LICENSE`, `hooks/`, and `skills/image-prompt/` are an
unmodified snapshot of `kimsh-1/gongnyang-prompt-kit` at the commit recorded in
`UPSTREAM.lock.json`.

- Upstream: https://github.com/kimsh-1/gongnyang-prompt-kit
- License: MIT; preserve `LICENSE` in every distributed copy.
- Local patches: none. Do not edit the vendored runtime files.
- Claude Craft owns only routing, provider binding, hook registration,
  provenance, and update verification.

Run `bash scripts/verify-gongnyang-prompt-kit.sh` after checkout and before a
release. Use `bash scripts/update-gongnyang-prompt-kit.sh --commit <sha>` to
stage an explicit upstream update; floating updates from `main` are not used.

The active generation provider is Codex `$imagegen`, whose built-in model is
`gpt-image-2`. The upstream note about a `gpt-image-1.5` transparency fallback
is not active in Claude Craft: transparent-background requests must use an
opaque result or stop as unsupported.
