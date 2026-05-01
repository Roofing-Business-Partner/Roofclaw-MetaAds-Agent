#!/usr/bin/env node
// soul-purpose-check.mjs — classifies a SOUL.md as MARKETING / NON_MARKETING / BORDERLINE.
//
// Usage:
//   node scripts/preflight/soul-purpose-check.mjs <path-to-SOUL.md>
//
// Exit codes:
//   0 — MARKETING (proceed)
//   1 — NON_MARKETING (reject)
//   2 — BORDERLINE (reject — do not rationalize)
//   3 — file missing or unreadable

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const MARKETING_TERMS = [
  "marketing", "brand", "content marketing", "social media",
  "paid media", "paid acquisition", "paid ads", "performance marketing",
  "demand generation", "demand gen", "growth marketing",
  "creative director", "creative agent", "creative lead",
  "lifecycle marketing", "community marketing", "influencer",
  "advertising agent", "ads agent", "marketing automation",
];

const NON_MARKETING_TERMS = [
  "chief of staff", "executive assistant",
  "sales rep", "sdr", "bdr", "appointment setter", "closer",
  "lead qualification", "revenue desk", "sales follow",
  "production coordinator", "operations coordinator", "ops agent",
  "dispatcher", "project manager", "recruiting", "recruiter",
  "bookkeeping", "invoicing", "collections",
  "support agent", "customer support",
  "estimator", "supplement agent",
  "data analyst", "bi agent", "business intelligence",
  "engineering agent", "dev agent", "developer agent",
];

const path = process.argv[2];
if (!path) {
  console.error("Usage: node scripts/preflight/soul-purpose-check.mjs <SOUL.md>");
  process.exit(3);
}

let raw;
try {
  raw = readFileSync(resolve(path), "utf8");
} catch (e) {
  console.error(`ERROR: cannot read ${path}: ${e.message}`);
  process.exit(3);
}

// Strip exclusion sections like "Not my job", "Out of scope", "What I do not do"
// so disclaimers don't leak non-marketing signals into the classification.
const exclusionHeaderRe = /^#+\s*(not my job|out of scope|what (i do not|i don't|this) does? not do|do not|exclusions?|guardrails?|won['\u2019]?t do)/im;
function stripExclusionSections(text) {
  const lines = text.split(/\r?\n/);
  const out = [];
  let skipping = false;
  for (const line of lines) {
    const isHeader = /^#+\s+/.test(line);
    if (isHeader) {
      skipping = exclusionHeaderRe.test(line);
    }
    if (!skipping) out.push(line);
  }
  return out.join("\n");
}

const text = stripExclusionSections(raw).toLowerCase();

const hits = (terms) => terms.filter((t) => text.includes(t));
const marketingHits = hits(MARKETING_TERMS);
const nonMarketingHits = hits(NON_MARKETING_TERMS);

console.log(`Marketing signals (${marketingHits.length}): ${marketingHits.slice(0, 5).join(", ") || "none"}`);
console.log(`Non-marketing signals (${nonMarketingHits.length}): ${nonMarketingHits.slice(0, 5).join(", ") || "none"}`);

let classification;
if (marketingHits.length >= 2 && nonMarketingHits.length === 0) {
  classification = "MARKETING";
} else if (marketingHits.length >= 3 && nonMarketingHits.length <= 1) {
  classification = "MARKETING";
} else if (nonMarketingHits.length >= 2 && marketingHits.length === 0) {
  classification = "NON_MARKETING";
} else if (marketingHits.length === 0 && nonMarketingHits.length >= 1) {
  classification = "NON_MARKETING";
} else {
  classification = "BORDERLINE";
}

console.log(`\nClassification: ${classification}`);

if (classification === "MARKETING") {
  console.log("✅ Proceed to docs/P0_PRESETUP.md.");
  process.exit(0);
}

console.log("\n❌ This RoofClaw is not eligible to implement the Meta Ads Agent.");
console.log("Recommended path: dedicated Marketing RoofClaw V2.0.");
console.log("Existing RoofClaw V1.0 customers qualify for 25% off.\n");

process.exit(classification === "NON_MARKETING" ? 1 : 2);
