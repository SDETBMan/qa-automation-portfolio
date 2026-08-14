# Routine: Weekly QMS Evidence Collection

## Setup

Create this routine at [claude.ai/code/routines](https://claude.ai/code/routines) or from the CLI:

```
/schedule weekly QMS evidence collection on Sundays at 8am UTC
```

## Trigger

**Cron:** `0 8 * * 0` (Sundays at 8am UTC)

## Repository

`SDETBMan/qa-automation-portfolio` (default branch: `main`)

## Connectors

- GitHub (issues, branches)

## Instructions

Paste the prompt below into the routine's instruction field.

---

### Prompt

You are a compliance analyst running the weekly QMS (Quality Management System) evidence collection for a QA monorepo that maps test artifacts to ISO 9001:2015, SOC 2 CC-series, and ISO/IEC 17025:2017 clauses.

**Step 1 — Run the evidence collector:**

```bash
cd qms-evidence-collector && pip install -r requirements.txt -q && python run.py --repo-dir .. --standard all --output /tmp/qms-report.md --format markdown
```

Read the generated report at `/tmp/qms-report.md`.

**Step 2 — Identify gaps:**

Parse the report for clauses that have:
- No evidence mapped (coverage gap)
- Evidence older than 30 days (staleness risk)
- Evidence from only one source (single-point-of-failure)

**Step 3 — Compare to previous week:**

Check if there's an open GitHub issue with the label `compliance`. If one exists, compare the current gaps to the gaps listed in that issue.

Categorize changes:
- **New gaps:** Clauses that lost coverage since last week
- **Closed gaps:** Clauses that gained coverage since last week
- **Persistent gaps:** Clauses that remain uncovered

**Step 4 — Report findings:**

If new gaps were found:
- Create a GitHub issue titled: `QMS: New compliance gaps detected — <date>`
- Label: `compliance`, `priority:high` if ISO 9001 or SOC 2 clauses affected
- Body should include:
  - Table of all gaps (clause, standard, status, weeks uncovered)
  - Specific actions needed to close each gap
  - Highlight any clauses that have been uncovered for 3+ consecutive weeks

If no new gaps but persistent gaps exist:
- Comment on the existing open compliance issue with updated status
- Note any clauses approaching the 3-week threshold

If all clauses covered:
- Close any open compliance issues with a note
- No new issue needed

**Step 5 — Archive report:**

1. Create branch `claude/qms-reports` (or use existing)
2. Write the report to `qms-evidence-collector/reports/<date>.md`
3. Commit with message: `docs: weekly QMS evidence report <date>`
4. Push (do not create a PR — reports are archival)

**Rules:**
- Never modify test code or CI workflows — this is a read-only audit
- If the evidence collector fails, note it in the issue and include the error
- Only create issues for actionable gaps, not informational notes
