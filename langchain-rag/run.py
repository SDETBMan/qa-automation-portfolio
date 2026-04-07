#!/usr/bin/env python3
"""QA Portfolio Assistant — LangChain RAG demo.

Usage:
    python run.py --question "Which frameworks use Selenium?"
    python run.py --demo          # runs 3 built-in questions
    python run.py --interactive   # REPL loop
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

from rag.chain import build_chain
from rag.loader import load_corpus
from rag.vectorstore import build_vectorstore

DEMO_QUESTIONS = [
    "Which test frameworks in this monorepo use Selenium?",
    "What BDD / Gherkin checkout scenarios exist across the portfolio?",
    "How is DataDog observability implemented in the AI evaluation frameworks?",
]


def ask(chain, question: str, session_id: str) -> str:
    """Invoke the chain and return the answer string."""
    return chain.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}},
    )


def main() -> None:
    load_dotenv(Path(__file__).parent / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit(
            "ERROR: OPENAI_API_KEY not set.\n"
            "  Copy .env.example → .env and add your key, or export OPENAI_API_KEY=..."
        )

    parser = argparse.ArgumentParser(description="QA Portfolio RAG Assistant")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--question", "-q", help="Single question to answer")
    group.add_argument("--demo", action="store_true", help="Run 3 built-in demo questions")
    group.add_argument("--interactive", "-i", action="store_true", help="Interactive REPL")
    args = parser.parse_args()

    print("\n[1/3] Loading corpus from monorepo…", flush=True)
    docs = load_corpus()
    print(f"      Loaded {len(docs)} documents (.md + .feature files)")

    print("[2/3] Building Chroma vector store…", flush=True)
    store = build_vectorstore(docs)
    retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    print("[3/3] Compiling LCEL chain with RunnableWithMessageHistory…\n", flush=True)
    chain = build_chain(retriever)

    session_id = str(uuid.uuid4())

    if args.demo:
        for i, q in enumerate(DEMO_QUESTIONS, 1):
            print(f"{'─' * 60}")
            print(f"Q{i}: {q}")
            answer = ask(chain, q, session_id)
            print(f"A{i}: {answer}\n")

    elif args.question:
        print(f"Q: {args.question}")
        answer = ask(chain, args.question, session_id)
        print(f"A: {answer}\n")

    elif args.interactive:
        print("Interactive mode — type 'exit' or press Ctrl-C to quit.\n")
        while True:
            try:
                q = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if q.lower() in {"exit", "quit", "q"}:
                break
            if not q:
                continue
            answer = ask(chain, q, session_id)
            print(f"Bot: {answer}\n")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
