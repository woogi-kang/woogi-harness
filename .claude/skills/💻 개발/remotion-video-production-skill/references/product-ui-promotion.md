# Product UI Promotion Workflow

Use this workflow for:

- app or web product promotion
- feature walkthroughs using real product screens
- launch videos where camera motion, cursor actions, and typography wrap the UI
- reproducing the motion grammar of a reference product video

The governing pipeline is:

```text
real product renderer
  -> deterministic capture
  -> capture manifest
  -> Remotion camera / transition / typography / audio
  -> MP4
```

Do not redraw a convincing-looking substitute for the product. Product truth
belongs to the product runtime or its deterministic golden renderer; editorial
motion belongs to Remotion.

## 1. Lock the output and evidence contract

Before implementation, record:

- duration, resolution, aspect ratio, fps, codec
- narration, captions, music, and provider envelope
- target viewer and one product thesis
- source repo, source revision, dirty-worktree state, and capture method
- expected capture, scene, render, and QA artifact paths
- approval boundary and stop condition

Required project artifacts:

```text
reference-analysis.json
capture-manifest.json
scene-spec.json
public/
  capture/
artifacts/
  frames/
  contact-sheet.png
  ffprobe.json
  final.mp4
```

Validate the three contracts before rendering:

```bash
python3 <skill>/scripts/validate-product-ui-promo.py \
  --reference reference-analysis.json \
  --capture capture-manifest.json \
  --scenes scene-spec.json \
  --project-root .
```

## 2. Analyze motion grammar, not impressions

If a reference video exists, extract its frames and create a contact sheet.
Use [`../rules/extract-frames.md`](../rules/extract-frames.md), FFmpeg, or an
equivalent deterministic extractor. Record for every shot:

- `startMs`, `endMs`, and `durationMs`
- camera entry and exit
- transition duration in milliseconds
- reveal order between product UI, pointer, and editorial text
- hold duration after the key state becomes readable

Summarize the reusable grammar: typical shot length, camera amplitude, cut vs
crossfade ratio, text hierarchy, and interaction cadence. Do not copy brand
assets or text from a reference.

If no reference video was supplied, record `status: "not_provided"` and a
reason. Then write an explicit target grammar under `motionGrammar`. Never
pretend that a reference was measured.

## 3. Capture the real product deterministically

Preferred source order:

1. live local web app controlled by Playwright
2. a browser-accessible debug or fixture route backed by product components
3. the product repo's deterministic golden renderer for native-only surfaces

The third path is an allowed native-app adaptation, not a license to mock the
UI. The golden must be produced by current product widgets/components and its
source test, viewport, DPR, locale, clock, revision, and hash must be recorded.

For browser capture, expose state through stable inputs such as:

```text
http://localhost:4173/capture?scene=records&frame=42
```

The same URL and inputs MUST reproduce:

- typed text and caret position
- cursor coordinates and click state
- open panels, sheets, and selected items
- loading completion and network fixture state
- scroll or drag position
- clock, locale, timezone, viewport, and device pixel ratio

Wait on an explicit readiness signal such as
`document.documentElement.dataset.captureReady === "true"`. Do not rely on an
arbitrary timeout alone.

Each captured frame entry must include:

- stable id and relative file path
- source route or fixture state
- source frame/time input
- width, height, and SHA-256

Playwright captures pixels. It does not own video camera moves, titles, or
transitions.

## 4. Declare scenes as presets

Every scene must contain exactly the reusable editorial contract:

```ts
type ProductScene = {
  preset:
    | "typing"
    | "cursorClick"
    | "imageDrag"
    | "uiZoom"
    | "cardStack"
    | "brandTitle";
  durationInFrames: number;
  params: Record<string, unknown>;
  transition: {
    type: "cut" | "fade" | "slide" | "wipe";
    durationInFrames: number;
  };
  camera: {
    x: number;
    y: number;
    scale: number;
    rotateX: number;
    rotateY: number;
  };
};
```

Preset responsibilities:

| Preset | Owns |
| --- | --- |
| `typing` | frame-derived text length, caret, and optional suggestion reveal |
| `cursorClick` | pointer path, press state, click ring, target emphasis |
| `imageDrag` | image/card translation, grab state, drop settle |
| `uiZoom` | readable camera push into one product state |
| `cardStack` | multi-screen depth, stagger, and selection |
| `brandTitle` | brand lockup, one thesis, and closing CTA |

Add product-specific content through `params`; do not fork a one-off animation
component for every shot. All motion must derive from `useCurrentFrame()`.

## 5. Use DOM depth for product UI

Product screens remain normal React DOM:

```tsx
const frame = useCurrentFrame();
const progress = interpolate(frame, [0, 24], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});

<div style={{perspective: 1800}}>
  <div
    style={{
      transform: `rotateX(${8 - progress * 8}deg)
        rotateY(${-12 + progress * 12}deg)
        translateZ(${40 + progress * 30}px)
        scale(${0.92 + progress * 0.08})`,
    }}
  >
    <Img src={staticFile("capture/records.png")} />
  </div>
</div>
```

Use `@remotion/three` only for actual 3D geometry or models. A tilted UI panel
does not require React Three Fiber.

For a lens effect, duplicate the UI layer:

1. base layer stays sharp
2. edge layer adds small blur and optional red/cyan channel separation
3. apply a radial mask that hides the edge layer at the center
4. keep key labels and actions inside the sharp region

Readability wins over physically perfect optics. Reject an effect if the
viewer cannot read the product state during its hold.

## 6. Composite, render, and verify

Remotion owns:

- camera and DOM perspective
- transitions
- editorial titles and Korean typography
- pointer visualization
- music, narration, and sound effects

It must not silently edit the product pixels. If a product screen needs
different content, recapture that product state.

Render H.264 locally, then verify:

1. validate the three JSON contracts
2. run `ffprobe` for codec, duration, dimensions, fps, frames, and audio
3. extract representative non-boundary frames
4. assemble a contact sheet
5. visually inspect legibility, clipping, blank frames, camera motion, and UI
   truth
6. record final file and representative frame hashes

For Korean titles and captions:

- use a Korean-capable local font and stable fallback
- keep `word-break: keep-all` behavior in DOM text
- avoid negative tracking for body copy
- review mixed Korean/English/numeric strings at the final resolution

## 7. Failure boundaries

Stop or downgrade honestly when:

- the runtime cannot reproduce a stable state after two bounded attempts
- auth or remote data is required but no approved fixture exists
- a claimed reference timing was not actually measured
- a screen asset cannot be traced to the product runtime or golden renderer

When browser capture is impossible for a native-only app, use a current,
verified golden render and record the adaptation. Do not label it as
Playwright live-app capture.
