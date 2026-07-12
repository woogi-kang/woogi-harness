#!/usr/bin/env node
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const Module = require("node:module");

function addBundledNodeModules() {
  const bundled = path.join(
    os.homedir(),
    ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules",
  );
  if (!fs.existsSync(bundled)) return;
  const current = process.env.NODE_PATH ? process.env.NODE_PATH.split(path.delimiter) : [];
  if (!current.includes(bundled)) {
    process.env.NODE_PATH = [bundled, ...current].join(path.delimiter);
    Module._initPaths();
  }
}

function requireHelpful(name, required = true) {
  try {
    return require(name);
  } catch (error) {
    if (!required) return null;
    console.error(`Missing Node package: ${name}`);
    console.error("Run with the Codex bundled Node runtime or install the package in this workspace.");
    console.error(error.message);
    process.exit(2);
  }
}

function parseArgs(argv) {
  const options = {
    deckPath: null,
    outDir: null,
    mobile: false,
    allowWarnings: false,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--out") {
      options.outDir = argv[++i];
    } else if (arg === "--mobile") {
      options.mobile = true;
    } else if (arg === "--allow-warnings") {
      options.allowWarnings = true;
    } else if (!options.deckPath) {
      options.deckPath = arg;
    } else {
      console.error(`Unknown argument: ${arg}`);
      process.exit(2);
    }
  }

  if (!options.deckPath) {
    console.error("Usage: node check-tightened-deck.cjs <path/to/index.html> [--out qa-dir] [--mobile] [--allow-warnings]");
    process.exit(2);
  }

  options.deckPath = path.resolve(options.deckPath);
  options.outDir = path.resolve(options.outDir || path.join(path.dirname(options.deckPath), "qa"));
  return options;
}

function safeName(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function normalizeAssetPath(value) {
  return String(value || "").replace(/\\/g, "/").replace(/^\.\//, "");
}

function loadAssetManifest(deckPath) {
  const manifestPath = path.join(path.dirname(deckPath), "asset_manifest.json");
  if (!fs.existsSync(manifestPath)) {
    return { path: manifestPath, present: false, entries: [], byFile: new Map(), errors: [] };
  }

  try {
    const parsed = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    const entries = Array.isArray(parsed) ? parsed : [];
    return {
      path: manifestPath,
      present: true,
      entries,
      byFile: new Map(entries.map((entry) => [normalizeAssetPath(entry.file), entry])),
      errors: Array.isArray(parsed) ? [] : [{ reason: "asset_manifest.json must contain an array." }],
    };
  } catch (error) {
    return {
      path: manifestPath,
      present: true,
      entries: [],
      byFile: new Map(),
      errors: [{ reason: `asset_manifest.json parse failed: ${error.message}` }],
    };
  }
}

function checkManifestForSlide(slideNumber, images, manifest) {
  const imageErrors = [];
  const imageWarnings = [];
  const localImages = images.filter((image) => normalizeAssetPath(image.src).startsWith("images/"));

  if (!localImages.length) return { imageErrors, imageWarnings };

  if (!manifest.present) {
    localImages.forEach((image) => {
      imageErrors.push({
        index: image.index,
        src: image.src,
        reason: "Local image requires asset_manifest.json with generator status and visual contract.",
      });
    });
    return { imageErrors, imageWarnings };
  }

  manifest.errors.forEach((error) => {
    imageErrors.push({ slide: slideNumber, reason: error.reason, manifest: manifest.path });
  });

  localImages.forEach((image) => {
    const src = normalizeAssetPath(image.src);
    const entry = manifest.byFile.get(src);

    if (!entry) {
      imageErrors.push({
        index: image.index,
        src: image.src,
        reason: "Local image is missing from asset_manifest.json.",
      });
      return;
    }

    const status = String(entry.status || "");
    const kind = String(entry.kind || "generated-raster");
    const compiler = String(entry.compiler || "");
    const generator = String(entry.generator || "");
    const hasLegacyModel = Object.prototype.hasOwnProperty.call(entry, "model");
    const requiredModel = String(entry.required_model || "");
    const modelBinding = String(entry.model_binding || "");
    const localModelVerification = String(entry.local_model_verification || "");
    const generationAssurance = String(entry.generation_assurance || "");
    const hasHostReportedModel = Object.prototype.hasOwnProperty.call(entry, "host_reported_model");
    const hostReportedModel = entry.host_reported_model;
    const promptRecord = String(entry.prompt_record || "");
    const visualContract = entry.visual_contract || {};
    const generatedRaster = kind === "generated-raster";
    const evidenceAsset = new Set([
      "product-screenshot",
      "reference-photo",
      "deterministic-chart",
      "deterministic-svg",
    ]).has(kind);

    if (status === "blocked_imagegen_not_run") {
      imageErrors.push({
        index: image.index,
        src: image.src,
        status,
        reason: "Codex image generation was not executed for this asset.",
      });
    }

    if (/fallback|placeholder|preview/i.test(`${status} ${generator}`)) {
      imageErrors.push({
        index: image.index,
        src: image.src,
        status,
        generator,
        reason: "Fallback, placeholder, or local preview images are not production visuals.",
      });
    }

    if (!generatedRaster && !evidenceAsset) {
      imageErrors.push({ index: image.index, src: image.src, kind, reason: "Manifest entry has an unsupported asset kind." });
    }

    if (generatedRaster && compiler !== "image-prompt@2.3.0") {
      imageErrors.push({ index: image.index, src: image.src, compiler, reason: "Generated raster must use image-prompt@2.3.0." });
    }

    if (generatedRaster && generator !== "image_gen__imagegen") {
      imageErrors.push({ index: image.index, src: image.src, generator, reason: "Generated raster must record the exact Codex image_gen__imagegen host tool." });
    }

    if (generatedRaster && hasLegacyModel) {
      imageErrors.push({ index: image.index, src: image.src, reason: "Generated raster must not claim a locally verified model field." });
    }

    if (generatedRaster && requiredModel !== "gpt-image-2") {
      imageErrors.push({ index: image.index, src: image.src, requiredModel, reason: "Generated raster must require gpt-image-2." });
    }

    if (generatedRaster && modelBinding !== "trusted-host-fixed") {
      imageErrors.push({ index: image.index, src: image.src, modelBinding, reason: "Generated raster must use the trusted-host-fixed model binding." });
    }

    if (generatedRaster && localModelVerification !== "unavailable") {
      imageErrors.push({ index: image.index, src: image.src, localModelVerification, reason: "Local model verification must be recorded as unavailable." });
    }

    if (generatedRaster && (!hasHostReportedModel || hostReportedModel !== null)) {
      imageErrors.push({ index: image.index, src: image.src, hostReportedModel, reason: "host_reported_model must be explicitly null when the Codex host exposes no model identity." });
    }

    if (generatedRaster && generationAssurance !== "generated_under_trusted_host_contract") {
      imageErrors.push({ index: image.index, src: image.src, generationAssurance, reason: "Generated raster must use trusted-host provenance without claiming local model attestation." });
    }

    if (generatedRaster && !promptRecord) {
      imageErrors.push({ index: image.index, src: image.src, reason: "Generated raster is missing prompt_record." });
    }

    if (generatedRaster && Object.prototype.hasOwnProperty.call(entry, "prompt")) {
      imageErrors.push({ index: image.index, src: image.src, reason: "Inline image prompts are forbidden; store the Gongnyang prompt_record reference." });
    }

    if (evidenceAsset && !String(entry.source || "").trim()) {
      imageErrors.push({ index: image.index, src: image.src, kind, reason: "Evidence/deterministic asset is missing source provenance." });
    }

    if (!entry.status) {
      imageErrors.push({ index: image.index, src: image.src, reason: "Manifest entry missing status." });
    }

    if (!visualContract || typeof visualContract !== "object" || Array.isArray(visualContract)) {
      imageErrors.push({ index: image.index, src: image.src, reason: "Manifest entry missing visual_contract." });
      return;
    }

    if (!String(visualContract.claim || "").trim()) {
      imageErrors.push({ index: image.index, src: image.src, reason: "visual_contract.claim is required." });
    }

    if (!Array.isArray(visualContract.must_show) || visualContract.must_show.length === 0) {
      imageErrors.push({ index: image.index, src: image.src, reason: "visual_contract.must_show must be a non-empty array." });
    }

    if (!String(visualContract.acceptance_check || "").trim()) {
      imageErrors.push({ index: image.index, src: image.src, reason: "visual_contract.acceptance_check is required." });
    }

    if (/generic|abstract|random|filler|decorative/i.test(String(entry.alt || ""))) {
      imageWarnings.push({
        index: image.index,
        src: image.src,
        reason: "Alt text contains generic/decorative language; confirm the visual contract is specific enough.",
      });
    }
  });

  return { imageErrors, imageWarnings };
}

async function makeContactSheet(sharp, outDir, shots) {
  if (!sharp || shots.length === 0) return null;

  const thumbW = 420;
  const thumbH = 236;
  const gap = 18;
  const cols = Math.min(3, Math.max(1, Math.ceil(Math.sqrt(shots.length))));
  const rows = Math.ceil(shots.length / cols);
  const composites = [];

  for (let i = 0; i < shots.length; i += 1) {
    const input = await sharp(shots[i]).resize(thumbW, thumbH, { fit: "cover" }).png().toBuffer();
    composites.push({
      input,
      left: (i % cols) * (thumbW + gap),
      top: Math.floor(i / cols) * (thumbH + gap),
    });
  }

  const outPath = path.join(outDir, "contact-sheet.png");
  await sharp({
    create: {
      width: thumbW * cols + gap * (cols - 1),
      height: thumbH * rows + gap * (rows - 1),
      channels: 4,
      background: "#fafaf8",
    },
  }).composite(composites).png().toFile(outPath);

  return outPath;
}

async function inspectSlide(page) {
  return page.evaluate(() => {
    const active = document.querySelector(".slide.active");
    const width = window.innerWidth;
    const height = window.innerHeight;
    if (!active) {
      return {
        layout: null,
        title: "",
        offscreen: [{ label: "No active slide", rect: [0, 0, 0, 0] }],
        overflow: [],
        padding: [],
        wordBreaking: [],
        images: [],
        imageErrors: [],
        imageWarnings: [],
      };
    }

    function getVisualLines(el) {
      const lines = [];
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      let node = walker.nextNode();

      while (node) {
        const text = node.textContent || "";
        for (let i = 0; i < text.length; i += 1) {
          const char = text[i];
          if (!char || !char.trim()) continue;

          const range = document.createRange();
          range.setStart(node, i);
          range.setEnd(node, i + 1);
          const rect = Array.from(range.getClientRects()).find((item) => item.width > 0 && item.height > 0);
          range.detach();
          if (!rect) continue;

          const top = Math.round(rect.top / 3) * 3;
          let line = lines.find((item) => Math.abs(item.top - top) <= 3);
          if (!line) {
            line = { top, left: rect.left, text: "" };
            lines.push(line);
          }
          line.left = Math.min(line.left, rect.left);
          line.text += char;
        }
        node = walker.nextNode();
      }

      return lines
        .sort((a, b) => a.top - b.top || a.left - b.left)
        .map((line) => line.text.replace(/\s+/g, " ").trim())
        .filter(Boolean);
    }

    function findKoreanLineBreakIssues(lines) {
      const issues = [];
      const orphanParticles = /^(은|는|이|가|을|를|의|에|에서|에게|로|으로|와|과|도|만|부터|까지|보다)$/;
      const orphanEnding = /^(다|다\.|요|요\.|죠|죠\.|함|됨|임|됨\.|임\.)$/;

      lines.forEach((line, index) => {
        const compact = line.replace(/\s+/g, "");
        if (!/[가-힣]/.test(compact)) return;

        if (orphanParticles.test(compact) || orphanEnding.test(compact)) {
          issues.push({ line: compact, index, reason: "Korean orphan particle or sentence ending rendered as its own line." });
          return;
        }

        if (/^[가-힣][.!?]$/.test(compact) && index > 0) {
          issues.push({ line: compact, index, reason: "Korean one-syllable punctuation ending rendered as its own line." });
          return;
        }

        if (/^[,.;:!?)]/.test(compact)) {
          issues.push({ line: compact, index, reason: "Line starts with punctuation." });
        }
      });

      return issues;
    }

    const textSelector = [
      "h1",
      "h2",
      "h3",
      "p",
      ".t-meta",
      ".t-cat",
      ".body",
      ".body-sm",
      ".lead",
      ".ledger-num",
      ".force-num",
      ".why-num-bottom",
      ".num-mega",
      ".sys-label",
      ".fc-col",
    ].join(",");

    const elements = Array.from(active.querySelectorAll(textSelector));
    const offscreen = [];
    const overflow = [];
    const padding = [];
    const wordBreaking = [];
    const navSafeBottom = height - 28;
    const minPadX = width < 800 ? 18 : 32;
    const minPadTop = width < 800 ? 18 : 30;

    for (const el of elements) {
      const label = (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 120);
      if (!label) continue;

      const rect = el.getBoundingClientRect();
      if (rect.width < 1 || rect.height < 1) continue;

      const style = getComputedStyle(el);
      const isHeading = /H[1-3]/.test(el.tagName)
        || el.classList.contains("h-xl")
        || el.classList.contains("h-md")
        || el.classList.contains("h-statement")
        || el.classList.contains("h-hero");
      const isMeta = el.classList.contains("t-meta") || el.classList.contains("t-cat");
      const isDisplayNumber = el.classList.contains("ledger-num")
        || el.classList.contains("force-num")
        || el.classList.contains("why-num-bottom")
        || el.classList.contains("num-mega");

      if (rect.left < -1 || rect.top < -1 || rect.right > width + 1 || rect.bottom > height + 1) {
        offscreen.push({ label, rect: [rect.left, rect.top, rect.width, rect.height] });
      }

      if (rect.left < minPadX || rect.right > width - minPadX || rect.top < minPadTop || rect.bottom > navSafeBottom) {
        if (!isMeta || rect.bottom > navSafeBottom || rect.left < minPadX - 8 || rect.right > width - (minPadX - 8)) {
          padding.push({
            label,
            rect: [rect.left, rect.top, rect.width, rect.height],
            safe: { left: minPadX, right: width - minPadX, top: minPadTop, bottom: navSafeBottom },
          });
        }
      }

      const overflowX = el.scrollWidth > el.clientWidth + 2;
      const overflowY = el.scrollHeight > el.clientHeight + (isHeading ? 42 : 2);
      if ((overflowX || overflowY) && !isDisplayNumber) {
        overflow.push({
          label,
          tag: el.tagName,
          heading: isHeading,
          scroll: [el.scrollWidth, el.scrollHeight],
          client: [el.clientWidth, el.clientHeight],
        });
      }

      if (style.wordBreak === "break-all" || style.overflowWrap === "anywhere") {
        wordBreaking.push({ label, reason: `CSS ${style.wordBreak}/${style.overflowWrap}` });
      }

      if (isHeading && /[가-힣]/.test(label) && !el.innerHTML.includes("<br")) {
        const lineHeight = Number.parseFloat(style.lineHeight);
        const fontSize = Number.parseFloat(style.fontSize);
        const expectedLine = Number.isFinite(lineHeight) ? lineHeight : fontSize * 1.1;
        if (rect.height > expectedLine * 1.6) {
          wordBreaking.push({ label, reason: "Korean heading wraps without explicit <br>." });
        }
      }

      if (/[0-9]+%/.test(label) && Number.parseFloat(style.letterSpacing) > 1) {
        wordBreaking.push({ label, reason: "Percent label has wide letter spacing." });
      }

      if (isHeading && /[가-힣]/.test(label)) {
        const lines = getVisualLines(el);
        const lineIssues = findKoreanLineBreakIssues(lines);
        lineIssues.forEach((issue) => {
          wordBreaking.push({ label, lines, ...issue });
        });
      }
    }

    const images = [];
    const imageErrors = [];
    const imageWarnings = [];
    Array.from(active.querySelectorAll("img")).forEach((img, index) => {
      const src = img.getAttribute("src") || "";
      const slot = img.getAttribute("data-image-slot") || "";
      const alt = img.getAttribute("alt") || "";
      const frame = img.closest(".frame-img");
      const frameClass = frame ? frame.className : "";
      const natural = [img.naturalWidth, img.naturalHeight];

      images.push({ index: index + 1, src, slot, alt, frameClass, natural });

      if (src.startsWith("images/") && !slot) {
        imageErrors.push({ index: index + 1, src, reason: "Local image missing data-image-slot." });
      }
      if (src.startsWith("images/") && !alt.trim()) {
        imageErrors.push({ index: index + 1, src, reason: "Local image missing alt text." });
      }
      if (src && natural[0] === 0) {
        imageErrors.push({ index: index + 1, src, reason: "Image did not load." });
      }
      if (/^s1[56]-(grid|brief)-21x9$/.test(slot) && frame && !frame.classList.contains("r-21x9")) {
        imageErrors.push({ index: index + 1, src, slot, reason: "S15/S16 21:9 slot must use .r-21x9." });
      }
      if (slot === "s22-hero-21x9" && frame && !frame.classList.contains("r-21x9")) {
        imageErrors.push({ index: index + 1, src, slot, reason: "S22 hero slot must use .r-21x9." });
      }
      if (slot && /text|label|title|copy|headline/i.test(src)) {
        imageWarnings.push({ index: index + 1, src, slot, reason: "Filename suggests text-bearing image; confirm no readable slide text is embedded." });
      }
    });

    return {
      layout: active.getAttribute("data-layout"),
      title: active.querySelector("h1,h2,.h-hero,.h-xl,.h-statement")?.textContent?.trim().replace(/\s+/g, " ") || "",
      offscreen,
      overflow,
      padding,
      wordBreaking,
      images,
      imageErrors,
      imageWarnings,
    };
  });
}

async function runViewport(browser, options, viewport, manifest) {
  const page = await browser.newPage({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: 1,
  });

  await page.goto(pathToFileURL(options.deckPath).href);
  await page.waitForLoadState("networkidle", { timeout: 3000 }).catch(() => {});
  await page.evaluate(() => {
    localStorage.setItem("tightened-slide-low-power", "1");
    document.body.classList.add("low-power");
  });

  const slideCount = await page.locator(".slide").count();
  const slides = [];
  const screenshots = [];

  for (let i = 0; i < slideCount; i += 1) {
    await page.evaluate((idx) => {
      const slides = Array.from(document.querySelectorAll(".slide"));
      slides.forEach((slide, slideIdx) => slide.classList.toggle("active", slideIdx === idx));
      const navButtons = Array.from(document.querySelectorAll("#nav button"));
      navButtons.forEach((button, buttonIdx) => button.classList.toggle("active", buttonIdx === idx));
      window.__currentSlideIndex = idx;
    }, i);
    await page.waitForTimeout(100);

    const screenshot = path.join(
      options.outDir,
      `${safeName(viewport.name)}-slide-${String(i + 1).padStart(2, "0")}.png`,
    );
    await page.screenshot({ path: screenshot, fullPage: false });
    screenshots.push(screenshot);

    const result = await inspectSlide(page);
    const manifestResult = checkManifestForSlide(i + 1, result.images, manifest);
    result.imageErrors.push(...manifestResult.imageErrors);
    result.imageWarnings.push(...manifestResult.imageWarnings);

    const hardOverflow = result.overflow.filter((item) => !item.heading);
    const failCount = result.offscreen.length
      + result.padding.length
      + result.wordBreaking.length
      + hardOverflow.length
      + result.imageErrors.length;
    const warnCount = result.overflow.filter((item) => item.heading).length + result.imageWarnings.length;

    slides.push({
      slide: i + 1,
      screenshot,
      status: failCount ? "FAIL" : warnCount ? "WARN" : "PASS",
      failCount,
      warnCount,
      ...result,
    });
  }

  await page.close();
  return { viewport, slideCount, slides, screenshots };
}

function formatDetails(items) {
  if (!items.length) return "";
  return `\n\`\`\`json\n${JSON.stringify(items, null, 2)}\n\`\`\``;
}

function buildReport(options, results, contactSheet) {
  const lines = [
    "# Future Slide QA Report",
    "",
    `Deck: ${options.deckPath}`,
    `Generated: ${new Date().toISOString()}`,
    contactSheet ? `Contact sheet: ${contactSheet}` : "Contact sheet: skipped (sharp not available)",
    "",
    "## Summary",
    "",
    "| Viewport | Slides | PASS | WARN | FAIL |",
    "|---|---:|---:|---:|---:|",
  ];

  for (const result of results) {
    const pass = result.slides.filter((slide) => slide.status === "PASS").length;
    const warn = result.slides.filter((slide) => slide.status === "WARN").length;
    const fail = result.slides.filter((slide) => slide.status === "FAIL").length;
    lines.push(`| ${result.viewport.name} ${result.viewport.width}x${result.viewport.height} | ${result.slideCount} | ${pass} | ${warn} | ${fail} |`);
  }

  lines.push(
    "",
    "## Checks",
    "",
    "- offscreen elements",
    "- text overflow",
    "- safe padding and bottom navigation collision",
    "- Korean heading word breaking",
    "- percent label letter spacing",
    "- local image loading, alt text, and data-image-slot",
    "- asset_manifest image-prompt/Codex trusted-host contract (required_model gpt-image-2; model_binding trusted-host-fixed; local_model_verification unavailable; host_reported_model null; generation_assurance generated_under_trusted_host_contract) or explicit deterministic evidence kind",
    "- S15/S16/S22 image slot class consistency",
    "",
    "## Details",
    "",
  );

  for (const result of results) {
    lines.push(`### ${result.viewport.name} ${result.viewport.width}x${result.viewport.height}`, "");
    for (const slide of result.slides) {
      lines.push(
        `#### Slide ${String(slide.slide).padStart(2, "0")} / ${slide.layout || "NO_LAYOUT"} / ${slide.status}`,
        "",
        `Title: ${slide.title}`,
        `Screenshot: ${slide.screenshot}`,
        `Offscreen: ${slide.offscreen.length}`,
        `Overflow: ${slide.overflow.length}`,
        `Padding: ${slide.padding.length}`,
        `Word breaking: ${slide.wordBreaking.length}`,
        `Image errors: ${slide.imageErrors.length}`,
        `Image warnings: ${slide.imageWarnings.length}`,
      );

      if (slide.offscreen.length) lines.push(`Offscreen detail:${formatDetails(slide.offscreen)}`);
      if (slide.overflow.length) lines.push(`Overflow detail:${formatDetails(slide.overflow)}`);
      if (slide.padding.length) lines.push(`Padding detail:${formatDetails(slide.padding)}`);
      if (slide.wordBreaking.length) lines.push(`Word breaking detail:${formatDetails(slide.wordBreaking)}`);
      if (slide.imageErrors.length) lines.push(`Image error detail:${formatDetails(slide.imageErrors)}`);
      if (slide.imageWarnings.length) lines.push(`Image warning detail:${formatDetails(slide.imageWarnings)}`);
      lines.push("");
    }
  }

  return lines.join("\n");
}

(async () => {
  addBundledNodeModules();
  const options = parseArgs(process.argv);

  if (!fs.existsSync(options.deckPath)) {
    console.error(`Deck not found: ${options.deckPath}`);
    process.exit(2);
  }
  fs.mkdirSync(options.outDir, { recursive: true });

  const { chromium } = requireHelpful("playwright");
  const sharp = requireHelpful("sharp", false);
  const manifest = loadAssetManifest(options.deckPath);
  const browser = await chromium.launch();

  const viewports = [
    { name: "desktop", width: 1366, height: 768 },
    ...(options.mobile ? [{ name: "mobile", width: 390, height: 844 }] : []),
  ];

  const results = [];
  try {
    for (const viewport of viewports) {
      results.push(await runViewport(browser, options, viewport, manifest));
    }
  } finally {
    await browser.close();
  }

  const screenshots = results.flatMap((result) => result.screenshots);
  const contactSheet = await makeContactSheet(sharp, options.outDir, screenshots).catch((error) => {
    console.warn(`Contact sheet skipped: ${error.message}`);
    return null;
  });

  const report = buildReport(options, results, contactSheet);
  const reportPath = path.join(options.outDir, "qa-report.md");
  fs.writeFileSync(reportPath, report, "utf8");

  const failTotal = results.reduce((sum, result) => sum + result.slides.filter((slide) => slide.status === "FAIL").length, 0);
  const warnTotal = results.reduce((sum, result) => sum + result.slides.filter((slide) => slide.status === "WARN").length, 0);
  console.log(reportPath);

  if (failTotal > 0) process.exit(1);
  if (warnTotal > 0 && !options.allowWarnings) process.exit(1);
})();
