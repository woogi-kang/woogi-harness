#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

function parseArgs(argv) {
  const options = {
    format: 'text',
    failOn: 'warning',
    output: null,
    targets: [],
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--format') options.format = argv[++index];
    else if (arg === '--fail-on') options.failOn = argv[++index];
    else if (arg === '--output') options.output = argv[++index];
    else if (arg === '--help' || arg === '-h') {
      console.log('Usage: detect-design-slop.mjs [--format text|json|sarif] [--fail-on warning|strong-warning|hard-fail|none] [--output FILE] [TARGET ...]');
      process.exit(0);
    } else if (arg.startsWith('--')) {
      throw new Error(`Unknown option: ${arg}`);
    } else options.targets.push(arg);
  }
  if (!['text', 'json', 'sarif'].includes(options.format)) throw new Error(`Unsupported --format: ${options.format}`);
  if (!['warning', 'strong-warning', 'hard-fail', 'none'].includes(options.failOn)) throw new Error(`Unsupported --fail-on: ${options.failOn}`);
  if (!options.targets.length) options.targets = ['.'];
  return options;
}

let options;
try {
  options = parseArgs(process.argv.slice(2));
} catch (error) {
  console.error(`detect-design-slop: ${error.message}`);
  process.exit(64);
}
const targets = options.targets;
const root = fs.realpathSync(process.cwd());

const sourcePolicyPath = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../registry/design/source-policy.json');
const sourcePolicy = JSON.parse(fs.readFileSync(sourcePolicyPath, 'utf8'));
if (sourcePolicy.schema !== 'design-source-policy-v1') throw new Error('invalid design source policy');
const SKIP_DIRS = new Set(sourcePolicy.skip_directories);
const EXTENSIONS = new Set(sourcePolicy.extensions);

const SEVERITY_RANK = {
  warning: 1,
  'strong-warning': 2,
  'hard-fail': 3,
};

const RULES = [
  {
    id: 'ai-gradient',
    severity: 'strong-warning',
    regex: /\b(from|to|via)-(purple|violet|indigo|blue)-\d{2,3}\b|linear-gradient\([^)]*(purple|violet|indigo|blue)/i,
    message: 'Purple/blue gradient reflex',
  },
  {
    id: 'gradient-text',
    severity: 'strong-warning',
    regex: /background-clip:\s*text|bg-clip-text/i,
    message: 'Gradient text; verify this is earned and not default emphasis',
  },
  {
    id: 'default-glass',
    severity: 'warning',
    regex: /backdrop-blur|glassmorphism/i,
    message: 'Glass/blur surface; verify fallback and purpose',
  },
  {
    id: 'h-screen',
    severity: 'warning',
    regex: /\bh-screen\b|height:\s*100vh/i,
    message: 'Use min-height: 100dvh for viewport sections',
  },
  {
    id: 'transition-all',
    severity: 'strong-warning',
    regex: /\btransition-all\b|transition:\s*all\b/i,
    message: 'Over-broad transition; target changed properties only',
  },
  {
    id: 'will-change-all',
    severity: 'hard-fail',
    regex: /\bwill-change-\[all\]\b|will-change:\s*all\b/i,
    message: 'will-change must be specific and rare',
  },
  {
    id: 'scale-zero',
    severity: 'warning',
    regex: /\b(?:scale-0|scale-\[0(?:\.0+)?\])\b|scale\(\s*0(?:\.0+)?\s*\)/i,
    message: 'Check scale(0) animation; prefer opacity plus near-full scale for UI entries',
  },
  {
    id: 'overdone-press-scale',
    severity: 'warning',
    regex: /\bactive:[\w:-]*scale-(?:[0-8]\d|9[0-4])\b|\bactive:[\w:-]*scale-\[(?:0?\.[0-8]\d*|0?\.9[0-4]\d*)\]/i,
    message: 'Press scale below 0.95 can feel exaggerated',
  },
  {
    id: 'giant-z',
    severity: 'warning',
    regex: /z-\[(999|9999|99999)\]|z-index:\s*(999|9999|99999)/i,
    message: 'Arbitrary giant z-index',
  },
  {
    id: 'side-stripe',
    severity: 'warning',
    regex: /\bborder-[lr]-[2-9]\b|border-(left|right)-width:\s*[2-9]px/i,
    message: 'Decorative side stripe; verify it is not generic card decoration',
  },
  {
    id: 'fake-name',
    severity: 'strong-warning',
    regex: /\b(John Doe|Jane Doe|Acme|Nexus|SmartFlow|Cloudly)\b/i,
    message: 'Generic placeholder name or startup-slop brand',
  },
  {
    id: 'cliche-copy',
    severity: 'strong-warning',
    regex: /\b(elevate|seamless|unleash|revolutionize|next-gen|game-changing|game changer|cutting-edge)\b/i,
    message: 'Generic marketing copy',
  },
  {
    id: 'placeholder-label',
    severity: 'strong-warning',
    regex: /placeholder=["'][^"']+["'][^>\n]*(aria-label)?/i,
    message: 'Check placeholder-only labels',
  },
  {
    id: 'scroll-cue',
    severity: 'strong-warning',
    regex: />\s*(Scroll|↓\s*scroll|Scroll to explore)\s*</i,
    message: 'Decorative scroll cue',
  },
  {
    id: 'lorem',
    severity: 'hard-fail',
    regex: /Lorem ipsum/i,
    message: 'Lorem ipsum placeholder',
  },
  {
    id: 'hero-version-label',
    severity: 'warning',
    regex: /\b(v\d+(?:\.\d+)?|beta|alpha|early access|invite[-\s]?only|preview)\b/i,
    message: 'Version/preview label; do not use as decorative hero eyebrow unless launch status is the message',
  },
  {
    id: 'section-number-eyebrow',
    severity: 'strong-warning',
    regex: /\b(?:section\s*)?0?\d{1,3}\s*(?:\/|·|\.|-|—|:)\s*[A-Z가-힣][\w가-힣 -]{2,}|\b\d{2,3}\s*\/\s*(?:index|intro|features|capabilities)\b/i,
    message: 'Section-number eyebrow/pagination label; often an AI design tell',
  },
  {
    id: 'decorative-status-dot',
    severity: 'warning',
    regex: /\b(?:bg|text|fill)-(?:green|emerald|red|rose|yellow|amber)-\d{2,3}\b[^\n]{0,80}\b(?:rounded-full|h-2|w-2|size-2|status|dot)\b|\b(?:status|dot)\b[^\n]{0,80}\b(?:bg|text|fill)-(?:green|emerald|red|rose|yellow|amber)-\d{2,3}\b/i,
    message: 'Decorative status dot; verify it communicates real state',
  },
  {
    id: 'fake-product-ui',
    severity: 'hard-fail',
    regex: /\b(fake|mock|placeholder)\s+(dashboard|terminal|browser|screenshot|chart|ui)\b|\b(div[-\s]?based|rectangle)\s+(dashboard|screenshot|chart|ui)\b/i,
    message: 'Fake product UI/screenshot evidence',
  },
  {
    id: 'default-shadcn-card',
    severity: 'strong-warning',
    regex: /rounded-lg[^\n]{0,80}\bborder\b[^\n]{0,80}\bbg-card\b[^\n]{0,80}\btext-card-foreground\b|bg-card\s+text-card-foreground\s+shadow-sm/i,
    message: 'Default shadcn card styling; customize tokens, radius, elevation, and hierarchy',
  },
  {
    id: 'generic-section-heading',
    severity: 'warning',
    regex: />\s*(Everything you need|Built for modern teams|Designed to scale|Powerful features|All-in-one platform|Work smarter|Move faster)\s*</i,
    message: 'Generic SaaS section heading',
  },
  {
    id: 'unsupported-perfect-metric',
    severity: 'warning',
    regex: /(?:\b99\.99%|\b100%|\b1,000,000\+|\b10x\b|\b\d+%\s+(?:faster|better|more)\b)/i,
    message: 'Perfect or unsupported metric; verify source or make organic/sourced',
  },
  {
    id: 'long-divide-y-list',
    severity: 'warning',
    regex: /\bdivide-y\b|\bborder-t\b[^\n]{0,80}\bborder-b\b|\bborder-b\b[^\n]{0,80}\bborder-t\b/i,
    message: 'Divider-list pattern; verify long lists are not lazy repeated rows',
  },
  {
    id: 'empty-bento-card',
    severity: 'strong-warning',
    regex: /\b(empty|decorative-only|placeholder)\b[^\n]{0,80}\b(card|tile|bento|cell)\b|\b(card|tile|bento|cell)\b[^\n]{0,80}\b(empty|decorative-only|placeholder)\b/i,
    message: 'Empty/decorative bento card; replace with evidence or remove',
  },
  {
    id: 'fake-logo-wall',
    severity: 'strong-warning',
    regex: /\b(?:trusted by|used by|logo wall)\b[^\n]{0,160}\b(?:Acme|Globex|Initech|Umbrella|Soylent|Stark)\b/i,
    message: 'Fake logo wall or generic logos',
  },
  {
    id: 'overused-uppercase-tracking',
    severity: 'warning',
    regex: /\buppercase\b[^\n]{0,80}\btracking-(?:wide|wider|widest|\[[^\]]+\])/i,
    message: 'Uppercase tracking eyebrow; count and verify it is not overused',
  },
  {
    id: 'generic-cta',
    severity: 'warning',
    regex: />\s*(Get Started|Learn More|Explore More|Start Now)\s*</i,
    message: 'Generic CTA; replace with a concrete action when the product intent is known',
  },
  {
    id: 'flutter-backdrop-filter',
    severity: 'warning',
    regex: /\bBackdropFilter\s*\(/,
    message: 'Flutter blur/glass surface; verify purpose, performance, contrast, and fallback',
  },
];

const FILE_RULES = [
  {
    id: 'flutter-ai-gradient',
    severity: 'strong-warning',
    regex: /LinearGradient\s*\([\s\S]{0,700}?(?:Colors\.(?:purple|deepPurple|indigo|blue)|Color\(0xFF(?:7C3AED|8B5CF6|4F46E5|2563EB)\))/i,
    message: 'Flutter purple/blue gradient reflex',
  },
  {
    id: 'default-ai-landing-structure',
    severity: 'strong-warning',
    regex: /(?:pill|badge)[\s\S]{0,1200}(?:Get Started|Start Now)[\s\S]{0,1800}(?:grid-cols-3|three (?:equal )?(?:cards|features))/i,
    message: 'Default AI landing structure: pill, generic CTA, and three equal cards',
  },
];

const findings = [];
const filesScanned = [];
const fileHashes = {};
const inputErrors = [];

function shouldRead(filePath) {
  return EXTENSIONS.has(path.extname(filePath));
}

function isSkippedPath(filePath) {
  return path.relative(root, filePath).split(path.sep).some(part => SKIP_DIRS.has(part));
}

function isInsideRoot(filePath) {
  const relative = path.relative(root, filePath);
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative));
}

function walk(target, topLevel = false) {
  const absolute = path.resolve(root, target);
  let stat;
  try {
    stat = fs.lstatSync(absolute);
  } catch {
    if (topLevel) inputErrors.push(`target does not exist: ${target}`);
    return;
  }
  if (stat.isSymbolicLink()) {
    if (topLevel) inputErrors.push(`target is a symlink and cannot be scanned: ${target}`);
    return;
  }
  let real;
  try {
    real = fs.realpathSync(absolute);
  } catch {
    if (topLevel) inputErrors.push(`target cannot be resolved: ${target}`);
    return;
  }
  if (!isInsideRoot(real)) {
    if (topLevel) inputErrors.push(`target resolves outside project root: ${target}`);
    return;
  }
  if (isSkippedPath(absolute)) return;

  if (stat.isDirectory()) {
    for (const entry of fs.readdirSync(absolute)) {
      if (SKIP_DIRS.has(entry)) continue;
      walk(path.join(absolute, entry), false);
    }
    return;
  }

  if (!stat.isFile() || !shouldRead(absolute)) return;

  const rel = path.relative(root, absolute);
  filesScanned.push(rel || path.basename(absolute));
  const bytes = fs.readFileSync(absolute);
  fileHashes[rel || path.basename(absolute)] = crypto.createHash('sha256').update(bytes).digest('hex');
  const text = bytes.toString('utf8');
  const lines = text.split(/\r?\n/);

  lines.forEach((line, index) => {
    for (const rule of RULES) {
      if (rule.regex.test(line)) {
        findings.push({
          id: rule.id,
          severity: rule.severity,
          message: rule.message,
          file: rel,
          line: index + 1,
          snippet: line.trim().slice(0, 220),
        });
      }
    }
  });

  for (const rule of FILE_RULES) {
    const match = text.match(rule.regex);
    if (!match || match.index === undefined) continue;
    const line = text.slice(0, match.index).split(/\r?\n/).length;
    findings.push({
      id: rule.id,
      severity: rule.severity,
      message: rule.message,
      file: rel,
      line,
      snippet: match[0].replace(/\s+/g, ' ').trim().slice(0, 220),
    });
  }
}

for (const target of targets) walk(target, true);
if (!filesScanned.length) inputErrors.push('no supported UI source files were scanned');

findings.sort((a, b) => {
  const severityDelta = SEVERITY_RANK[b.severity] - SEVERITY_RANK[a.severity];
  if (severityDelta) return severityDelta;
  return `${a.file}:${a.line}`.localeCompare(`${b.file}:${b.line}`);
});

const counts = findings.reduce((acc, finding) => {
  acc[finding.severity] = (acc[finding.severity] || 0) + 1;
  return acc;
}, {});

const status = inputErrors.length || counts['hard-fail'] ? 'fail' : findings.length ? 'review' : 'pass';
const payload = {
  schema: 'design-slop-scan-v2',
  status,
  targets,
  files_scanned: [...new Set(filesScanned)].sort(),
  file_hashes: Object.fromEntries(Object.entries(fileHashes).sort(([left], [right]) => left.localeCompare(right))),
  errors: inputErrors,
  counts: {
    'hard-fail': counts['hard-fail'] || 0,
    'strong-warning': counts['strong-warning'] || 0,
    warning: counts.warning || 0,
    total: findings.length,
  },
  findings,
};

function toSarif() {
  const ruleMap = new Map([...RULES, ...FILE_RULES].map(rule => [rule.id, rule]));
  return {
    version: '2.1.0',
    $schema: 'https://json.schemastore.org/sarif-2.1.0.json',
    runs: [{
      tool: {
        driver: {
          name: 'Woogi Harness Design Slop Detector',
          version: '3.0.0',
          rules: [...ruleMap.values()].map(rule => ({
            id: rule.id,
            shortDescription: { text: rule.message },
            defaultConfiguration: { level: rule.severity === 'hard-fail' ? 'error' : 'warning' },
          })),
        },
      },
      results: findings.map(finding => ({
        ruleId: finding.id,
        level: finding.severity === 'hard-fail' ? 'error' : 'warning',
        message: { text: finding.message },
        locations: [{ physicalLocation: { artifactLocation: { uri: finding.file }, region: { startLine: finding.line } } }],
      })),
    }],
  };
}

let rendered;
if (options.format === 'json') rendered = `${JSON.stringify(payload, null, 2)}\n`;
else if (options.format === 'sarif') rendered = `${JSON.stringify(toSarif(), null, 2)}\n`;
else if (inputErrors.length) rendered = `${inputErrors.map(error => `ERROR: ${error}`).join('\n')}\n`;
else if (!findings.length) rendered = 'No design-slop pattern hits found.\n';
else {
  const lines = [];
  for (const finding of findings) {
    lines.push(`${finding.file}:${finding.line} [${finding.severity}] [${finding.id}] ${finding.message}`);
    lines.push(`  ${finding.snippet}`);
  }
  lines.push('');
  lines.push(`${findings.length} finding(s). hard-fail=${payload.counts['hard-fail']}, strong-warning=${payload.counts['strong-warning']}, warning=${payload.counts.warning}.`);
  lines.push('Treat warnings as review prompts. Hard-fail findings require a fix or an explicit waiver.');
  rendered = `${lines.join('\n')}\n`;
}

if (options.output) fs.writeFileSync(path.resolve(root, options.output), rendered, 'utf8');
else process.stdout.write(rendered);

if (inputErrors.length) process.exit(2);
if (options.failOn === 'none') process.exit(0);
const threshold = SEVERITY_RANK[options.failOn];
const shouldFail = findings.some(finding => SEVERITY_RANK[finding.severity] >= threshold);
process.exit(shouldFail ? (counts['hard-fail'] ? 2 : 1) : 0);
