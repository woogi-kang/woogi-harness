# img2threejs upstream

- Repository: `https://github.com/img2threejs/img2threejs`
- License: Apache-2.0
- Integration: exact-vendored runtime snapshot with no local patches
- Active entrypoint: `.claude/skills/img2threejs -> ../../third_party/img2threejs`

`UPSTREAM.lock.json` records the pinned full commit, upstream skill version,
selected runtime paths, and deterministic archive hash. `UPSTREAM.manifest`
records the Git object id and mode for every vendored upstream file.

Update only through:

```bash
bash scripts/update-img2threejs.sh --commit <full-upstream-sha>
bash scripts/update-img2threejs.sh --commit <full-upstream-sha> --apply
```

The first command is a check-only staged diff. The second applies the reviewed
snapshot and runs the vendor verifier. Do not patch files below
`third_party/img2threejs`; contribute fixes upstream and repin.
