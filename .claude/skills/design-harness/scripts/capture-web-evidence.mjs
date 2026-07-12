#!/usr/bin/env node
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

function parseArgs(argv) {
  const result = { root: '.', spec: null, out: null, validateOnly: false, runId: '', nonce: '', sourceFingerprint: '' };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--root') result.root = argv[++index];
    else if (arg === '--spec') result.spec = argv[++index];
    else if (arg === '--out') result.out = argv[++index];
    else if (arg === '--validate-only') result.validateOnly = true;
    else if (arg === '--run-id') result.runId = argv[++index];
    else if (arg === '--nonce') result.nonce = argv[++index];
    else if (arg === '--source-fingerprint') result.sourceFingerprint = argv[++index];
    else if (arg === '--help' || arg === '-h') {
      console.log('Usage: capture-web-evidence.mjs --root PROJECT --spec capture.json --out DIR [--validate-only]');
      process.exit(0);
    } else throw new Error(`unknown argument: ${arg}`);
  }
  if (!result.spec) throw new Error('--spec is required');
  if (!result.out) throw new Error('--out is required');
  if (!result.validateOnly && (!result.runId || !/^[a-f0-9]{48}$/.test(result.nonce) || !/^[a-f0-9]{64}$/.test(result.sourceFingerprint))) {
    throw new Error('trusted capture requires --run-id, a 48-hex --nonce, and a 64-hex --source-fingerprint');
  }
  return result;
}

function readObject(file) {
  const payload = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) throw new Error(`expected JSON object: ${file}`);
  return payload;
}

function validateSpec(spec) {
  const errors = [];
  if (spec.schema !== 'design-web-capture-v1') errors.push('schema must be design-web-capture-v1');
  let base;
  try {
    base = new URL(spec.base_url);
    if (!['http:', 'https:'].includes(base.protocol)) errors.push('base_url must use http or https');
    if (!['127.0.0.1', 'localhost', '[::1]'].includes(base.hostname)) errors.push('base_url must target a loopback host');
  } catch {
    errors.push('base_url must be an absolute URL');
  }
  if (!Array.isArray(spec.cases) || !spec.cases.length) errors.push('cases must be a non-empty array');
  const ids = new Set();
  for (const [index, capture] of (spec.cases || []).entries()) {
    const where = `cases[${index}]`;
    if (!capture || typeof capture !== 'object') {
      errors.push(`${where} must be an object`);
      continue;
    }
    if (!/^[a-z0-9][a-z0-9_-]*$/.test(capture.id || '')) errors.push(`${where}.id is invalid`);
    else if (ids.has(capture.id)) errors.push(`${where}.id is duplicated`);
    else ids.add(capture.id);
    if (typeof capture.path !== 'string') errors.push(`${where}.path must be a string`);
    else {
      if (!capture.path.startsWith('/') || capture.path.startsWith('//') || capture.path.includes('\\') || /[\u0000-\u001f]/.test(capture.path)) {
        errors.push(`${where}.path must be a same-origin relative path`);
      } else if (base) {
        try {
          const target = new URL(capture.path, base);
          if (target.origin !== base.origin) errors.push(`${where}.path resolves outside base_url origin`);
        } catch {
          errors.push(`${where}.path is not a valid URL path`);
        }
      }
    }
    if (typeof capture.state !== 'string' || !capture.state) errors.push(`${where}.state is required`);
    if (capture.phase !== undefined && !['baseline', 'result'].includes(capture.phase)) {
      errors.push(`${where}.phase must be baseline or result`);
    }
    const viewport = capture.viewport;
    if (!viewport || typeof viewport.name !== 'string' || !Number.isInteger(viewport.width) || !Number.isInteger(viewport.height)) {
      errors.push(`${where}.viewport requires name and integer width/height`);
    }
    for (const action of capture.actions || []) {
      if (!['click', 'fill', 'press'].includes(action.type)) errors.push(`${where} has unsupported action type: ${action.type}`);
      if (typeof action.selector !== 'string' || !action.selector) errors.push(`${where} action selector is required`);
      if (action.type === 'fill' && typeof action.value !== 'string') errors.push(`${where} fill action value must be a string`);
      if (action.type === 'press' && typeof action.key !== 'string') errors.push(`${where} press action key must be a string`);
    }
    const assertions = capture.assertions || [];
    if (capture.state !== 'default' && !assertions.length) {
      errors.push(`${where}.assertions is required for non-default states`);
    }
    for (const assertion of assertions) {
      if (!['visible', 'text', 'aria_contains'].includes(assertion.type)) {
        errors.push(`${where} has unsupported assertion type: ${assertion.type}`);
      }
      if (['visible', 'text'].includes(assertion.type) && (typeof assertion.selector !== 'string' || !assertion.selector)) {
        errors.push(`${where} assertion selector is required for ${assertion.type}`);
      }
      if (['text', 'aria_contains'].includes(assertion.type) && (typeof assertion.value !== 'string' || !assertion.value)) {
        errors.push(`${where} assertion value is required for ${assertion.type}`);
      }
      if (assertion.match !== undefined && !['contains', 'exact'].includes(assertion.match)) {
        errors.push(`${where} assertion match must be contains or exact`);
      }
    }
  }
  return errors;
}

function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

function safeArtifactPath(out, id, suffix) {
  const result = path.resolve(out, `${id}${suffix}`);
  if (path.dirname(result) !== path.resolve(out)) throw new Error(`artifact path escapes output: ${result}`);
  return result;
}

function loadPlaywright(root) {
  const packageFile = path.join(root, 'package.json');
  if (!fs.existsSync(packageFile)) throw new Error(`package.json not found: ${packageFile}`);
  const requireFromProject = createRequire(packageFile);
  for (const name of ['playwright', '@playwright/test']) {
    try {
      const library = requireFromProject(name);
      if (library.chromium) return library;
    } catch {
      // Try the next project-installed package.
    }
  }
  throw new Error('Playwright is not installed in the target project; do not silently install or use a different browser tool');
}

async function performAction(page, action) {
  const locator = page.locator(action.selector);
  if (action.type === 'click') await locator.click();
  else if (action.type === 'fill') await locator.fill(action.value);
  else if (action.type === 'press') await locator.press(action.key);
}

async function performAssertion(page, assertion) {
  let actual;
  let passed = false;
  if (assertion.type === 'visible') {
    actual = await page.locator(assertion.selector).isVisible();
    passed = actual === true;
  } else if (assertion.type === 'text') {
    actual = (await page.locator(assertion.selector).textContent()) || '';
    passed = assertion.match === 'exact' ? actual === assertion.value : actual.includes(assertion.value);
  } else if (assertion.type === 'aria_contains') {
    actual = await page.locator('body').ariaSnapshot();
    passed = assertion.match === 'exact' ? actual === assertion.value : actual.includes(assertion.value);
  }
  return {
    type: assertion.type,
    selector: assertion.selector || '',
    expected: assertion.value ?? true,
    match: assertion.match || 'contains',
    actual,
    status: passed ? 'passed' : 'failed',
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = path.resolve(args.root);
  const specPath = path.resolve(args.spec);
  const out = path.resolve(args.out);
  const spec = readObject(specPath);
  const errors = validateSpec(spec);
  if (errors.length) {
    console.error(JSON.stringify({ status: 'invalid', errors }, null, 2));
    return 2;
  }
  if (args.validateOnly) {
    console.log(JSON.stringify({ status: 'valid', cases: spec.cases.length }));
    return 0;
  }
  fs.mkdirSync(out, { recursive: true });
  const { chromium } = loadPlaywright(root);
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const capture of spec.cases) {
      const consoleErrors = [];
      const pageErrors = [];
      const context = await browser.newContext({
        viewport: { width: capture.viewport.width, height: capture.viewport.height },
        deviceScaleFactor: capture.viewport.device_scale_factor || 1,
        reducedMotion: capture.reduced_motion ? 'reduce' : 'no-preference',
      });
      const page = await context.newPage();
      page.on('console', message => {
        if (message.type() === 'error') consoleErrors.push(message.text());
      });
      page.on('pageerror', error => pageErrors.push(error.message));
      const result = { id: capture.id, status: 'passed', errors: [], artifacts: [] };
      try {
        const base = new URL(spec.base_url);
        const resolved = new URL(capture.path, base);
        if (resolved.origin !== base.origin) throw new Error('capture path escaped base_url origin');
        const target = resolved.toString();
        await page.goto(target, { waitUntil: capture.wait_until || 'domcontentloaded', timeout: capture.timeout_ms || 30000 });
        if (capture.wait_for_selector) await page.locator(capture.wait_for_selector).waitFor({ state: 'visible' });
        for (const action of capture.actions || []) await performAction(page, action);
        if (capture.settle_ms) await page.waitForTimeout(capture.settle_ms);
        const assertionResults = [];
        for (const assertion of capture.assertions || []) {
          assertionResults.push(await performAssertion(page, assertion));
        }
        if (assertionResults.length) {
          const assertionPath = safeArtifactPath(out, capture.id, '.state-assertions.json');
          const assertionPayload = {
            schema: 'design-state-assertion-result-v1',
            case_id: capture.id,
            route: capture.path,
            state: capture.state,
            viewport: capture.viewport.name,
            status: assertionResults.every(item => item.status === 'passed') ? 'passed' : 'failed',
            assertions: assertionResults,
          };
          fs.writeFileSync(assertionPath, `${JSON.stringify(assertionPayload, null, 2)}\n`, 'utf8');
          result.artifacts.push({
            kind: 'state-assertion', path: assertionPath, sha256: sha256(assertionPath), route: capture.path,
            state: capture.state, viewport: capture.viewport.name, platform: 'web', supports: ['state-coverage'],
          });
          if (assertionPayload.status !== 'passed') {
            result.status = 'failed';
            result.errors.push('one or more typed state assertions failed');
          }
        }
        const screenshot = safeArtifactPath(out, capture.id, '.png');
        await page.screenshot({ path: screenshot, fullPage: Boolean(capture.full_page) });
        result.artifacts.push({
          kind: capture.phase === 'baseline' ? 'baseline-screenshot' : 'result-screenshot', path: screenshot, sha256: sha256(screenshot), route: capture.path,
          state: capture.state, viewport: capture.viewport.name, platform: 'web', supports: capture.supports || ['visual-qa'],
        });
        if (capture.capture_aria !== false) {
          const aria = await page.locator('body').ariaSnapshot();
          const ariaPath = safeArtifactPath(out, capture.id, '.aria.txt');
          fs.writeFileSync(ariaPath, `${aria}\n`, 'utf8');
          result.artifacts.push({
            kind: 'accessibility-tree', path: ariaPath, sha256: sha256(ariaPath), route: capture.path,
            state: capture.state, viewport: capture.viewport.name, platform: 'web', supports: ['accessibility'],
          });
        }
        if ((consoleErrors.length || pageErrors.length) && !capture.allow_console_errors) {
          result.status = 'failed';
          result.errors.push(...consoleErrors.map(value => `console: ${value}`), ...pageErrors.map(value => `page: ${value}`));
        }
      } catch (error) {
        result.status = 'failed';
        result.errors.push(error instanceof Error ? error.message : String(error));
      } finally {
        await context.close();
      }
      results.push(result);
    }
  } finally {
    await browser.close();
  }
  const payload = {
    schema: 'design-capture-index-v1',
    producer: 'capture-web-evidence@1',
    generated_at: new Date().toISOString(),
    platform: 'web',
    project_root: root,
    spec: specPath,
    spec_sha256: sha256(specPath),
    run_id: args.runId,
    nonce: args.nonce,
    adapter_sha256: sha256(fileURLToPath(import.meta.url)),
    source_fingerprint_digest: args.sourceFingerprint,
    status: results.every(result => result.status === 'passed') ? 'passed' : 'failed',
    results,
  };
  const indexPath = path.join(out, 'capture-index.json');
  fs.writeFileSync(indexPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
  console.log(indexPath);
  return payload.status === 'passed' ? 0 : 2;
}

main().then(code => process.exit(code)).catch(error => {
  console.error(`capture-web-evidence: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(2);
});
