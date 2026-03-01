# job-agent

A Claude-powered agentic tool that finds relevant job postings, scores them against your
resume/portfolio, and drafts tailored cover letters. All in one automated run.

Demonstrates **Anthropic Claude tool-use / agentic loops** alongside the portfolio's
existing OpenAI-based evaluation frameworks.

---

## How it works

```
run.py
  └─ JobHunter.run()
       ├─ Loads profile/profile.md → system prompt
       ├─ Agentic loop (Claude claude-sonnet-4-6, max 30 iterations):
       │    ├─ search_jobs()        → Tavily web search (5 role queries)
       │    ├─ fetch_job_posting()  → Tavily extract (full JD text)
       │    ├─ score_job_fit()      → Claude scores 0-10 per role
       │    ├─ draft_cover_letter() → Claude writes tailored letters
       │    └─ save_results()       → writes output/ files
       └─ Returns plain-text summary
```

---

## Quick start

```bash
cd job-agent

# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your profile
cp profile/profile.example.md profile/profile.md
# Edit profile/profile.md with your actual background

# 3. Configure API keys
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY and TAVILY_API_KEY

# 4. Run
python run.py

# Optional: filter to a specific role
python run.py --role "SDET"
```

---

## Output

```
output/
├── jobs_2026-03-01.md          ← all scored jobs (score >= 6), sorted by fit
└── cover_letters/
    ├── Acme_Corp_SDET.md
    └── TechCorp_Lead_QA_Engineer.md
```

---

## Configuration

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key |
| `TAVILY_API_KEY` | Yes | Tavily search API key (free tier: 1,000 searches/month) |
| `DD_API_KEY` | No | DataDog API key for metrics |

---

## CI / Nightly runs

The workflow `.github/workflows/job-agent.yml` runs nightly at **09:00 UTC** and on
`workflow_dispatch`. Results are uploaded as a 7-day artifact.

Required repository secrets: `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`
Optional: `DD_API_KEY`

To trigger manually with a role filter:
1. Go to Actions → Job Agent → Run workflow
2. Enter a role keyword in the `role_filter` input (e.g. `SDET`)

---

## Search queries

Five queries run per execution (one per role type):

- `SDET remote job opening 2026`
- `Lead QA Engineer remote job opening 2026`
- `Quality Engineering Manager remote job 2026`
- `AI QA Engineer LLM testing remote 2026`
- `QA Automation Lead Selenium Playwright remote 2026`

Pass `--role <keyword>` (or set `ROLE_FILTER` env var) to restrict to matching queries.

---

## DataDog metrics

| Metric | Description |
|---|---|
| `llm.job_agent.jobs_found` | Total jobs discovered |
| `llm.job_agent.jobs_scored` | Jobs with score >= 6 |
| `llm.job_agent.cover_letters_drafted` | Cover letters written |
| `llm.job_agent.duration_ms` | Total run duration |
| `llm.api.latency_ms` | LLM API latency (tagged `framework:job-agent`) |

---

## Security note

`profile/profile.md` and `output/` are git-ignored. Your personal details and generated
letters never leave your machine (or CI runner ephemeral storage).
