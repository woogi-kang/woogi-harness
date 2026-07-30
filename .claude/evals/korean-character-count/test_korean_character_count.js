"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "../../..");
const helperPath = path.join(
  repoRoot,
  ".claude",
  "skills",
  "🇰🇷 k-skill",
  "korean-character-count",
  "scripts",
  "korean_character_count.js",
);

const {
  countLines,
  countNeisBytes,
  countUtf8Bytes,
  createReport,
  parseArgs,
} = require(helperPath);

test("createReport counts graphemes, lines, and bytes with the default contract", () => {
  const sample = "한🙂\r\n둘째 줄";
  const report = createReport(sample);

  assert.equal(report.profile, "default");
  assert.equal(report.counts.characters, 7);
  assert.equal(report.counts.characters_without_whitespace, 5);
  assert.equal(report.counts.lines, 2);
  assert.equal(report.counts.bytes, countUtf8Bytes(sample));
  assert.equal(report.counts.bytes_utf8, report.counts.bytes);
  assert.equal(report.counts.bytes_neis, countNeisBytes(sample));
  assert.match(report.contract.characters, /grapheme/i);
  assert.match(report.contract.bytes, /UTF-8/);
});

test("countLines treats every documented newline sequence once", () => {
  assert.equal(countLines(""), 0);
  assert.equal(countLines("가"), 1);
  assert.equal(countLines("가\n"), 2);
  assert.equal(countLines("가\r\n나\r다\u2028라\u2029마"), 5);
});

test("countNeisBytes applies the compatibility profile without guessing", () => {
  assert.equal(countNeisBytes("가A 1\n나🙂"), 15);
  assert.equal(countNeisBytes("ABC"), 3);
  assert.equal(countNeisBytes("한글"), 6);
  assert.equal(countNeisBytes("\u0301"), countUtf8Bytes("\u0301"));
  assert.equal(countNeisBytes("🙂"), countUtf8Bytes("🙂"));
});

test("parseArgs enforces one input source and validates the profile", () => {
  assert.deepEqual(parseArgs(["--text", "가나다"]), {
    format: "json",
    inputMode: "text",
    profile: "default",
    text: "가나다",
  });
  assert.throws(
    () => parseArgs(["--text", "가", "--file", "sample.txt"]),
    /exactly one input source/i,
  );
  assert.throws(
    () => parseArgs(["--text", "가", "--text", "나"]),
    /exactly one input source/i,
  );
  assert.throws(
    () => parseArgs(["--profile", "legacy", "--text", "가"]),
    /unknown profile/i,
  );
});

test("CLI accepts text, file, and stdin and returns the documented schema", () => {
  const tempDir = fs.mkdtempSync(
    path.join(os.tmpdir(), "woogi-korean-character-count-"),
  );
  const samplePath = path.join(tempDir, "sample.txt");

  try {
    fs.writeFileSync(samplePath, "가나다\nABC", "utf8");

    const textOutput = JSON.parse(
      childProcess.execFileSync(
        "node",
        [helperPath, "--text", "가나다", "--format", "json"],
        { cwd: repoRoot, encoding: "utf8" },
      ),
    );
    assert.equal(textOutput.counts.characters, 3);
    assert.equal(textOutput.counts.bytes_utf8, 9);

    const fileOutput = JSON.parse(
      childProcess.execFileSync(
        "node",
        [helperPath, "--file", samplePath, "--format", "json"],
        { cwd: repoRoot, encoding: "utf8" },
      ),
    );
    assert.equal(fileOutput.counts.lines, 2);
    assert.equal(
      fileOutput.counts.bytes_utf8,
      countUtf8Bytes("가나다\nABC"),
    );

    const stdinOutput = JSON.parse(
      childProcess.execFileSync(
        "node",
        [helperPath, "--stdin", "--profile", "neis"],
        { cwd: repoRoot, encoding: "utf8", input: "가나다\nABC" },
      ),
    );
    assert.equal(stdinOutput.profile, "neis");
    assert.equal(stdinOutput.counts.bytes, countNeisBytes("가나다\nABC"));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});
