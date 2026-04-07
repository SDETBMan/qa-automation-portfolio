"""Build an in-memory Chroma vector store from a list of Documents."""

from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def build_vectorstore(docs: list[Document], chunk_size: int = 1000, chunk_overlap: int = 150) -> Chroma:
    """Split *docs* into chunks and index them in an ephemeral Chroma store.

    Args:
        docs: Raw Documents loaded from the monorepo.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        A Chroma instance ready for similarity search.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # collection_name must be unique per process run to avoid Chroma conflicts
    store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="qa_portfolio",
    )
    return store
