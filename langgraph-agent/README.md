# langgraph-agent — Test Case Generator Pipeline

> **Stack:** LangGraph 0.4 · LangChain Anthropic · `claude-haiku-4-5` · StateGraph · Conditional edges

A stateful multi-agent graph that turns a plain-English feature description into reviewed, production-quality BDD Gherkin scenarios — with an automated review/revise cycle.

---

## What it demonstrates

| Concept | Where |
|---|---|
| **StateGraph + TypedDict state** | `graph/state.py`, `graph/pipeline.py` |
| **Multi-node orchestration** | `graph/nodes.py` — 4 nodes, each a pure function |
| **Conditional edges** | `graph/edges.py` — `review_router` routes to revise or END |
| **Cycle with bounded iterations** | `review_quality → revise_tests → review_quality` (max 2 revisions) |
| **Provider-agnostic LLM** | `ChatAnthropic` — shows LangGraph works beyond OpenAI |
| **Real-time streaming** | `graph.stream()` in `run.py` prints node-by-node progress |

---

## Quick start

```bash
cd langgraph-agent
pip install -r requirements.txt

# Add your Anthropic key
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# Run built-in demo
python run.py --demo

# Provide your own feature
python run.py --feature "User can reset their password via email"
```

Output is saved to `output/test_cases_<timestamp>.md`.

---

## Graph topology

```
parse_requirements
    → generate_tests
        → review_quality
            ├── (REVISE, count < 2) → revise_tests → review_quality  [loop]
            └── (PASS or count ≥ 2) → END
```

---

## Key LangGraph pattern

```python
def review_router(state: AgentState) -> Literal["revise_tests", "__end__"]:
    if state["review_verdict"] == "PASS" or state["revision_count"] >= 2:
        return "__end__"
    return "revise_tests"

builder.add_conditional_edges(
    "review_quality",
    review_router,
    {"revise_tests": "revise_tests", "__end__": END},
)
builder.add_edge("revise_tests", "review_quality")  # cycle
```

---

## File layout

```
langgraph-agent/
├── run.py                  # CLI entry point (streams node events)
├── requirements.txt
├── .env.example            # ANTHROPIC_API_KEY template
├── graph/
│   ├── state.py            # AgentState TypedDict
│   ├── nodes.py            # 4 node functions (parse, generate, review, revise)
│   ├── edges.py            # review_router conditional function
│   └── pipeline.py         # build_graph() → compiled StateGraph
└── output/                 # Generated .md files (git-ignored)
```

---

## Cost

| Step | Model | Est. calls | Est. cost |
|---|---|---|---|
| parse + generate + review + revise | `claude-haiku-4-5` | 4–6 | < $0.02 |

Auto-recharge is disabled — this runs only on `workflow_dispatch` in CI.
