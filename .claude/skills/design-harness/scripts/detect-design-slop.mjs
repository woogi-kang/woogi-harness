#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const targets = args.length ? args : ['.'];
const root = process.cwd();

const SKIP_DIRS = new Set([
  '.git',
  '.agents',
  '.claude',
  '.codex',
  '.cursor',
  '.gemini',
  '.github',
  '.opencode',
  'node_modules',
  '.next',
  'dist',
  'build',
  'coverage',
  '.turbo',
  '.vercel',
  '__pycache__',
]);

const EXTENSIONS = new Set([
  '.html',
  '.css',
  '.scss',
  '.sass',
  '.js',
  '.jsx',
  '.ts',
  '.tsx',
  '.vue',
  '.svelte',
  '.astro',
  '.md',
  '.mdx',
]);

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
    regex: /\b(99\.99%|100%|1,000,000\+|10x|\d+%\s+(?:faster|better|more))\b/i,
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
];

const findings = [];

function shouldRead(filePath) {
  return EXTENSIONS.has(path.extname(filePath));
}

function isSkippedPath(filePath) {
  return path.relative(root, filePath).split(path.sep).some(part => SKIP_DIRS.has(part));
}

function walk(target) {
  const absolute = path.resolve(root, target);
  if (!fs.existsSync(absolute)) return;
  if (isSkippedPath(absolute)) return;
  const stat = fs.statSync(absolute);

  if (stat.isDirectory()) {
    for (const entry of fs.readdirSync(absolute)) {
      if (SKIP_DIRS.has(entry)) continue;
      walk(path.join(absolute, entry));
    }
    return;
  }

  if (!stat.isFile() || !shouldRead(absolute)) return;

  const rel = path.relative(root, absolute);
  const text = fs.readFileSync(absolute, 'utf8');
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
}

for (const target of targets) walk(target);

if (!findings.length) {
  console.log('No design-slop pattern hits found.');
  process.exit(0);
}

findings.sort((a, b) => {
  const severityDelta = SEVERITY_RANK[b.severity] - SEVERITY_RANK[a.severity];
  if (severityDelta) return severityDelta;
  return `${a.file}:${a.line}`.localeCompare(`${b.file}:${b.line}`);
});

const counts = findings.reduce((acc, finding) => {
  acc[finding.severity] = (acc[finding.severity] || 0) + 1;
  return acc;
}, {});

for (const finding of findings) {
  console.log(`${finding.file}:${finding.line} [${finding.severity}] [${finding.id}] ${finding.message}`);
  console.log(`  ${finding.snippet}`);
}

console.log(`\n${findings.length} finding(s). hard-fail=${counts['hard-fail'] || 0}, strong-warning=${counts['strong-warning'] || 0}, warning=${counts.warning || 0}.`);
console.log('Treat warnings as review prompts. Hard-fail findings require a fix or an explicit waiver.');

process.exit(counts['hard-fail'] ? 2 : 1);
