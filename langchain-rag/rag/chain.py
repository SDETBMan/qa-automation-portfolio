"""LCEL RAG chain with conversation history."""

from __future__ import annotations

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI


# ---------------------------------------------------------------------------
# In-process session store (sufficient for a demo; swap for Redis in prod)
# ---------------------------------------------------------------------------

_session_store: dict[str, "InMemoryHistory"] = {}


class InMemoryHistory(BaseChatMessageHistory):
    """Minimal in-memory chat message history."""

    def __init__(self) -> None:
        self.messages: list[BaseMessage] = []

    def add_messages(self, messages: list[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


def get_session_history(session_id: str) -> InMemoryHistory:
    if session_id not in _session_store:
        _session_store[session_id] = InMemoryHistory()
    return _session_store[session_id]


# ---------------------------------------------------------------------------
# Chain builder
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are the QA Portfolio Assistant, an expert on the \
qa-automation-portfolio monorepo. Use only the retrieved context below to \
answer the question. If the answer is not in the context, say so.

Retrieved context:
{context}"""

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)


def _format_docs(docs: list) -> str:
    return "\n\n---\n\n".join(
        f"[{d.metadata.get('source', 'unknown')}]\n{d.page_content}" for d in docs
    )


def build_chain(retriever: VectorStoreRetriever) -> RunnableWithMessageHistory:
    """Return a conversation-aware RAG chain backed by *retriever*.

    Demonstrates:
    - LCEL chain composition with dict fan-out
    - RunnablePassthrough for question pass-through
    - RunnableWithMessageHistory for multi-turn conversation
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Core RAG chain (stateless)
    rag_chain = (
        {
            "context": retriever | _format_docs,
            "question": RunnablePassthrough(),
            "history": RunnablePassthrough(),
        }
        | _PROMPT
        | llm
        | StrOutputParser()
    )

    # Wrap with message history — history key must match MessagesPlaceholder name
    chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    return chain_with_history
