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

---

## Quick start

```bash
cd langchain-rag
pip install -r requirements.txt

# Add your OpenAI key
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

## File layout

```
langchain-rag/
├── run.py                  # CLI entry point
├── requirements.txt
├── .env.example            # OPENAI_API_KEY template
├── rag/
│   ├── loader.py           # Loads .md + .feature files from monorepo
│   ├── vectorstore.py      # Chroma in-memory store builder
│   └── chain.py            # LCEL RAG chain + conversation history
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
