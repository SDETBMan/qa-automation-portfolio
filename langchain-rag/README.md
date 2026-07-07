# langchain-rag — QA Portfolio RAG Assistant

> **Stack:** LangChain 0.3 · LCEL · Chroma (in-memory) · OpenAI `gpt-4o-mini` · `text-embedding-3-small`

A Retrieval-Augmented Generation (RAG) pipeline that loads the monorepo's own `.md` and `.feature` files as its knowledge corpus, then answers natural-language questions about the test frameworks.

---

## What it demonstrates

| Concept | Where |
|---|---|
| **LCEL chain composition** | `rag/chain.py` — dict fan-out, `RunnablePassthrough`, `StrOutputParser` |
| **In-memory Chroma vector store** | `rag/vectorstore.py` — `RecursiveCharacterTextSplitter` + `OpenAIEmbeddings` |
| **Multi-source document loader** | `rag/loader.py` — walks monorepo, skips noise dirs |
| **Conversation history** | `rag/chain.py` — `RunnableWithMessageHistory` + `InMemoryHistory` |
| **Cost-efficient models** | `gpt-4o-mini` + `text-embedding-3-small` (< $0.01 per demo run) |
| **Langfuse observability** | `rag/observability.py` — LLM tracing, token/cost tracking, retriever spans |

---

## Quick start

```bash
cd langchain-rag
pip install -r requirements.txt

# Add your OpenAI key (required) + optional Langfuse keys for tracing
cp .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...

# Run 3 built-in demo questions
python run.py --demo

# Ask a single question
python run.py --question "Which frameworks use Selenium?"

# Interactive REPL
python run.py --interactive
```

---

## Key LCEL pattern

```python
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
        "history": RunnablePassthrough(),
    }
    | prompt
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)
```

---

## Observability (Langfuse)

When `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY` are set in `.env`, every chain invocation is traced to [Langfuse](https://langfuse.com). Tracing is disabled gracefully when the keys are absent.

**What gets traced:**

| Span | Data captured |
|---|---|
| Retriever | Query text, returned documents, latency |
| LLM | Model, prompt tokens, completion tokens, cost, latency |
| Chain | Full input/output at each LCEL step |

**Setup:**
1. Create a free account at [cloud.langfuse.com](https://cloud.langfuse.com)
2. Create a project and copy the API keys
3. Add to `.env`:
   ```
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```
4. Run `python run.py --demo` — traces appear in the Langfuse dashboard

---

## File layout

```
langchain-rag/
├── run.py                  # CLI entry point
├── requirements.txt
├── .env.example            # OPENAI_API_KEY + Langfuse keys template
├── rag/
│   ├── loader.py           # Loads .md + .feature files from monorepo
│   ├── vectorstore.py      # Chroma in-memory store builder
│   ├── chain.py            # LCEL RAG chain + conversation history
│   └── observability.py    # Langfuse tracing (opt-in via env vars)
└── output/                 # (empty placeholder)
```

---

## Demo questions

```
Q1: Which test frameworks in this monorepo use Selenium?
Q2: What BDD / Gherkin checkout scenarios exist across the portfolio?
Q3: How is DataDog observability implemented in the AI evaluation frameworks?
```

---

## Cost

| Step | Model | Est. cost |
|---|---|---|
| Embedding corpus | `text-embedding-3-small` | ~$0.001 |
| 3 demo questions | `gpt-4o-mini` | ~$0.005 |
| **Total** | | **< $0.01** |

Auto-recharge is disabled — this runs only on `workflow_dispatch` in CI.
