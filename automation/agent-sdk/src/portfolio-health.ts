/**
 * Portfolio Health Orchestrator — Agent SDK
 *
 * Multi-step health assessment that uses Claude Code as a library to:
 *   1. Detect which frameworks have uncommitted changes
 *   2. Run dependency audit across all ecosystems
 *   3. Check site-monitor for DOM drift
 *   4. Analyze flakiness data (if JUnit XML available)
 *   5. Synthesize an executive health report
 *
 * Unlike the headless scripts (single-prompt, single-response), this uses
 * the Agent SDK's multi-turn capability: Claude decides what to run based
 * on what it finds in earlier steps.
 *
 * Usage:
 *   npx tsx src/portfolio-health.ts              # standard assessment
 *   npx tsx src/portfolio-health.ts --quick       # skip slow checks
 *   npx tsx src/portfolio-health.ts --full        # include all optional scans
 *   npx tsx src/portfolio-health.ts --json        # JSON output only
 */

import { query } from "@anthropic-ai/claude-code";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

// ── Configuration ───────────────────────────────────────────────────────────

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "../../..");

type RunMode = "quick" | "standard" | "full";

interface HealthConfig {
  mode: RunMode;
  jsonOnly: boolean;
  repoRoot: string;
}

function parseArgs(): HealthConfig {
  const args = process.argv.slice(2);
  let mode: RunMode = "standard";
  let jsonOnly = false;

  for (const arg of args) {
    switch (arg) {
      case "--quick":
        mode = "quick";
        break;
      case "--full":
        mode = "full";
        break;
      case "--json":
        jsonOnly = true;
        break;
      case "--help":
      case "-h":
        console.log(
          "Usage: portfolio-health [--quick|--full] [--json]\n" +
            "  --quick   Skip dependency audit and site monitor (faster)\n" +
            "  --full    Include vulnerability scan and QMS evidence check\n" +
            "  --json    Output only the final JSON report"
        );
        process.exit(0);
    }
  }

  return { mode, jsonOnly, repoRoot: REPO_ROOT };
}

// ── System prompt ───────────────────────────────────────────────────────────

function buildSystemPrompt(config: HealthConfig): string {
  const modeInstructions: Record<RunMode, string> = {
    quick: `QUICK MODE — Only run these checks:
1. git status (uncommitted changes, current branch)
2. Last 5 commit messages
3. Check for .verified marker at .claude/hooks/.verified
Skip dependency audit, site-monitor, and flakiness analysis.`,

    standard: `STANDARD MODE — Run these checks in order:
1. git status (uncommitted changes, current branch, staged files)
2. Last 10 commit messages (look for patterns: lots of fix: commits = instability)
3. Detect affected frameworks: bash .claude/skills/verify-changes/scripts/check.sh --detect
4. Run dependency audit: cd dependency-audit && pip install -r requirements.txt -q 2>/dev/null && python run.py --repo-dir .. 2>/dev/null
5. Run site monitor: cd site-monitor && pip install -r requirements.txt -q 2>/dev/null && python run.py 2>/dev/null
6. Check .verified marker status at .claude/hooks/.verified`,

    full: `FULL MODE — Run all standard checks plus:
1-6. Everything from standard mode
7. Run vulnerability aggregator: cd vulnerability-aggregator && pip install -r requirements.txt -q 2>/dev/null && python run.py --repo SDETBMan/qa-automation-portfolio 2>/dev/null
8. Run QMS evidence collector: cd qms-evidence-collector && pip install -r requirements.txt -q 2>/dev/null && python run.py --repo-dir .. --standard all 2>/dev/null
9. If any JUnit XML directories exist, run flakiness detector on them`,
  };

  return `You are a QA portfolio health assessor for a polyglot monorepo with 26 independent test frameworks.

Your job is to run diagnostic tools and synthesize a health report. Work step by step — run each check, read the output, then move to the next.

${modeInstructions[config.mode]}

IMPORTANT RULES:
- Run commands from the repo root: ${config.repoRoot}
- If a tool fails or is not installed, note it as "skipped" and continue — never stop on a single failure
- Do NOT modify any files — this is a read-only assessment
- Do NOT install global packages — only use pip install -r within each framework dir
- Capture stdout from each tool; if a tool writes to a file, read that file

After all checks complete, output your final report as a JSON object with this exact structure:
{
  "assessed_at": "<ISO 8601 timestamp>",
  "mode": "${config.mode}",
  "branch": "<current git branch>",
  "overall_health": "healthy" | "degraded" | "critical",
  "checks": {
    "<check_name>": {
      "status": "pass" | "warn" | "fail" | "skipped",
      "detail": "<one-line summary>"
    }
  },
  "frameworks_needing_attention": [
    { "framework": "<name>", "issue": "<what's wrong>", "priority": "high" | "medium" | "low" }
  ],
  "recommendations": ["<actionable item 1>", "<actionable item 2>", ...],
  "raw_outputs": {
    "<check_name>": "<first 500 chars of raw output>"
  }
}

Output ONLY the JSON object as your final message — no markdown fences, no preamble.`;
}

// ── Main orchestration ──────────────────────────────────────────────────────

async function assessHealth(config: HealthConfig): Promise<void> {
  if (!config.jsonOnly) {
    console.error(`Portfolio Health Assessment (${config.mode} mode)`);
    console.error("─".repeat(50));
  }

  const messages: Array<{ type: string; content?: string }> = [];
  let lastText = "";

  const conversation = query({
    prompt: "Run the portfolio health assessment now. Execute each check step by step.",
    options: {
      systemPrompt: buildSystemPrompt(config),
      allowedTools: ["Bash", "Read", "Glob", "Grep"],
      cwd: config.repoRoot,
      permissionMode: "acceptEdits",
      maxTurns: config.mode === "quick" ? 8 : config.mode === "full" ? 25 : 15,
    },
  });

  for await (const message of conversation) {
    messages.push(message as { type: string; content?: string });

    // Log progress to stderr so stdout stays clean for JSON
    if (!config.jsonOnly && message.type === "assistant" && typeof (message as any).content === "string") {
      const content = (message as any).content as string;
      // Show tool-use progress
      if (content.includes("Running") || content.includes("Checking")) {
        console.error(`  → ${content.slice(0, 80)}`);
      }
    }

    // Capture last text response (the final report)
    if (message.type === "assistant") {
      const content = (message as any).content;
      if (typeof content === "string") {
        lastText = content;
      } else if (Array.isArray(content)) {
        const textBlock = content.find((b: any) => b.type === "text");
        if (textBlock) {
          lastText = textBlock.text;
        }
      }
    }
  }

  // ── Extract and output the report ───────────────────────────────────────
  // Try to parse JSON from the last message
  let report: Record<string, unknown> | null = null;
  try {
    // Handle case where JSON is wrapped in markdown fences
    const jsonMatch = lastText.match(/```(?:json)?\s*([\s\S]*?)```/) ||
                      lastText.match(/(\{[\s\S]*\})/);
    if (jsonMatch) {
      report = JSON.parse(jsonMatch[1]);
    }
  } catch {
    // If parsing fails, wrap the raw output
    report = {
      assessed_at: new Date().toISOString(),
      mode: config.mode,
      overall_health: "unknown",
      error: "Could not parse structured report from Claude output",
      raw_output: lastText.slice(0, 2000),
    };
  }

  if (report) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(lastText);
  }

  if (!config.jsonOnly) {
    console.error("─".repeat(50));
    console.error("Assessment complete.");
  }
}

// ── Entry point ─────────────────────────────────────────────────────────────

const config = parseArgs();
assessHealth(config).catch((err) => {
  console.error("Health assessment failed:", err.message);
  process.exit(1);
});
