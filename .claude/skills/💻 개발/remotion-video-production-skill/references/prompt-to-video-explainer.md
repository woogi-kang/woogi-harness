# Prompt-to-video Explainer Workflow

Use this reference for requests like:

- "Make a 60-second animated explainer about how neural networks learn"
- "이 주제로 짧은 설명 영상을 만들어줘"
- "OpenMontage처럼 프롬프트만으로 영상 하나 만들어봐"

This workflow was validated against `calesthio/OpenMontage` at commit
`7ee36dd6b66c7dc0712da194786b77da1c2e7ed3` on 2026-06-25. Treat OpenMontage as
an external reference/runtime. Do not vendor its source into this harness unless
the target repo can accept AGPLv3 obligations.

## Fit

Use the local Remotion path when the request is an explainer, pitch, tutorial,
data story, status report, product walkthrough, or Korean/English narrated
short where structured scenes matter more than photoreal generated motion.

When the request is primarily a real product UI showcase, app promo, or
interaction demo, route to
[`product-ui-promotion.md`](product-ui-promotion.md) instead. That workflow
separates deterministic product capture from Remotion compositing and forbids
redrawing the product UI.

Do not promise cinematic AI video generation, stock footage, premium voice,
music, or word-level subtitles until the relevant provider keys and tools are
available. State the provider envelope before producing assets.

## Output Contract

Before rendering, lock a small contract:

- duration target, e.g. 60 seconds
- aspect ratio and resolution, e.g. 16:9, 1920x1080
- fps, usually 30
- narration language and voice path
- subtitle/caption requirement
- visual grammar: text cards, charts, callouts, comparison, image/video clips
- acceptance checks: `ffprobe`, frame samples, audio present, text not clipped

## Zero-key Path

The zero-key path is:

1. Write the script.
2. Generate narration with local Piper TTS, or skip narration if unavailable.
3. Measure narration length with `ffprobe`.
4. Build a Remotion composition or props file with timed cuts.
5. Render H.264 with Remotion.
6. Verify with `ffprobe` and sampled frames.

For a 60-second English narration, start around 130-165 words. Adjust with TTS
`length_scale` and `sentence_silence`, then remeasure. For Korean narration,
measure the generated audio instead of relying on word count.

## Piper Notes

If Piper is installed in a virtualenv, make sure the `piper` binary is on
`PATH` before invoking tooling:

```bash
PATH="$PWD/.venv/bin:$PATH" python - <<'PY'
from tools.audio.piper_tts import PiperTTS

result = PiperTTS().execute({
    "text": "Short narration text.",
    "model": "projects/demo/models/en_US-lessac-medium.onnx",
    "output_path": "projects/demo/assets/audio/narration.wav",
    "sentence_silence": 0.28,
    "length_scale": 1.08,
})
print(result.success, result.error, result.data)
PY
```

If model download fails on macOS with a certificate error, retry with certifi:

```bash
SSL_CERT_FILE=$(python -c 'import certifi; print(certifi.where())') \
  python -m piper.download_voices \
  --download-dir projects/demo/models en_US-lessac-medium
```

## Remotion Asset Rules

Put audio, images, and video that Remotion should load via `staticFile()` under
the Remotion app's `public/` directory. For example:

```text
remotion-composer/public/assets/demo/narration.wav
```

Then reference it as:

```json
{
  "audio": {
    "narration": {
      "src": "assets/demo/narration.wav",
      "volume": 1
    }
  }
}
```

Avoid absolute local paths for Remotion audio props. In the OpenMontage smoke
test, an absolute WAV path was converted to a `file:///` URL and Remotion audio
loading rejected it. Relative `public/` assets were stable.

## Scene Planning

For a 60-second explainer, use 6-12 cuts. Keep most cuts between 4 and 8
seconds. A practical sequence:

1. hook/title
2. process loop or concept map
3. key term callout
4. before/after or comparison
5. line/bar chart for change over time
6. direct text card for the core mechanism
7. progress/KPI/stat card for repetition or scale
8. closing takeaway

Each scene should carry one idea. Do not add decorative scenes that do not
support the narration.

## Render

Use local Remotion from the project that owns the composition:

```bash
cd remotion-composer
npx remotion render src/index.tsx Explainer ../projects/demo/renders/demo.mp4 \
  --props public/demo-props/demo.json \
  --codec h264
```

If the project uses TypeScript/React components instead of JSON props, render
the registered composition id and pass only the props it declares.

## Verification

Run these checks before handing off:

```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate,nb_frames,duration \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 \
  path/to/output.mp4
```

Sample frames away from scene boundaries. Exact boundaries can show fade-in or
fade-out backgrounds and look blank even when the video is correct.

```bash
ffmpeg -y -hide_banner -loglevel error -ss 00:00:02 -i path/to/output.mp4 -frames:v 1 frame-02.png
ffmpeg -y -hide_banner -loglevel error -ss 00:00:07 -i path/to/output.mp4 -frames:v 1 frame-07.png
ffmpeg -y -hide_banner -loglevel error -ss 00:00:57 -i path/to/output.mp4 -frames:v 1 frame-57.png
```

Inspect sampled frames for nonblank visuals, readable text, and no clipping.
Confirm the output contains an audio stream if narration/music was promised.

## Handoff

Leave these artifacts together:

- final `.mp4`
- source props or composition inputs
- narration script
- sampled frames if visual QA was performed
- short note with duration, resolution, fps, codec, audio status, and known gaps

Do not commit generated videos or private render outputs to this public harness
unless the user explicitly asks for tracked artifacts. Use ignored workspace
output folders for local samples.
