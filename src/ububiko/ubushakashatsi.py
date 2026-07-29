"""ubushakashatsi — AI Data Platform for UBUBIKO.

Provides vector embeddings, semantic search, knowledge bases,
document storage, and RAG (Retrieval-Augmented Generation) pipelines.
"""

from __future__ import annotations

import hashlib
import json
import math
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


@dataclass
class Document:
    """A document with content and metadata for AI processing.

    Attributes:
        id: Unique document identifier.
        content: Document text content.
        metadata: Arbitrary key-value metadata.
        embedding: Optional vector embedding.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Document:
        return cls(**data)


@dataclass
class SearchResult:
    """Result of a similarity search."""

    document: Document
    score: float = 0.0
    rank: int = 0


class EmbeddingService:
    """Service for generating and managing vector embeddings.

    Supports configurable embedding dimensions and similarity metrics.
    Uses a pluggable embedding function (default: simple hash-based vector).
    """

    def __init__(self, dimensions: int = 384,
                 embedding_fn: Optional[Callable[[str], List[float]]] = None) -> None:
        self._dimensions = dimensions
        self._embedding_fn = embedding_fn or self._default_embed

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def _default_embed(self, text: str) -> List[float]:
        """Generate a deterministic pseudo-embedding from text.

        Uses a hash-based approach to create fixed-dimension vectors
        for development and testing. Replace with a real model in production.
        """
        import hashlib
        vec = []
        seed = hashlib.sha256(text.encode()).digest()
        for i in range(self._dimensions):
            h = hashlib.sha256(seed + str(i).encode()).digest()
            val = int.from_bytes(h[:4], "big") / 4294967295.0
            vec.append(val * 2.0 - 1.0)
        return vec

    def embed(self, text: str) -> List[float]:
        """Generate an embedding vector for text."""
        return self._embedding_fn(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed(t) for t in texts]

    def similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec_a or not vec_b:
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def magnitude(self, vec: List[float]) -> float:
        """Compute the magnitude of a vector."""
        return math.sqrt(sum(v * v for v in vec))


class VectorIndex:
    """In-memory vector index for similarity search.

    Stores document embeddings and provides fast nearest-neighbor
    lookup using cosine similarity.
    """

    def __init__(self, dimensions: int = 384, metric: str = "cosine") -> None:
        self._dimensions = dimensions
        self._metric = metric
        self._documents: Dict[str, Document] = {}
        self._embeddings: Dict[str, List[float]] = {}

    @property
    def dimensions(self) -> int:
        return self._dimensions

    @property
    def size(self) -> int:
        return len(self._documents)

    def add(self, doc: Document) -> None:
        """Add a document to the index."""
        if doc.embedding:
            self._documents[doc.id] = doc
            self._embeddings[doc.id] = doc.embedding

    def add_many(self, docs: List[Document]) -> None:
        """Add multiple documents to the index."""
        for doc in docs:
            self.add(doc)

    def remove(self, doc_id: str) -> None:
        """Remove a document from the index."""
        self._documents.pop(doc_id, None)
        self._embeddings.pop(doc_id, None)

    def search(self, query_vector: List[float], top_k: int = 10) -> List[SearchResult]:
        """Search for nearest neighbors by cosine similarity."""
        scores: List[Tuple[str, float]] = []
        emb = EmbeddingService(self._dimensions)
        for doc_id, vec in self._embeddings.items():
            score = emb.similarity(query_vector, vec)
            scores.append((doc_id, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for rank, (doc_id, score) in enumerate(scores[:top_k]):
            doc = self._documents.get(doc_id)
            if doc:
                results.append(SearchResult(document=doc, score=score, rank=rank + 1))
        return results

    def clear(self) -> None:
        """Clear all documents from the index."""
        self._documents.clear()
        self._embeddings.clear()


class SemanticSearch:
    """Semantic search engine combining embedding and ranking."""

    def __init__(self, embedding_service: Optional[EmbeddingService] = None,
                 vector_index: Optional[VectorIndex] = None) -> None:
        self._embedding = embedding_service or EmbeddingService()
        self._index = vector_index or VectorIndex(self._embedding.dimensions)

    @property
    def embedding_service(self) -> EmbeddingService:
        return self._embedding

    @property
    def index(self) -> VectorIndex:
        return self._index

    def index_document(self, doc: Document) -> None:
        """Index a document with its embedding."""
        if not doc.embedding:
            doc.embedding = self._embedding.embed(doc.content)
        self._index.add(doc)

    def index_documents(self, docs: List[Document]) -> None:
        """Index multiple documents."""
        for doc in docs:
            self.index_document(doc)

    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search documents semantically similar to query."""
        query_vector = self._embedding.embed(query)
        return self._index.search(query_vector, top_k)

    def hybrid_search(self, query: str, keyword_weight: float = 0.3,
                      top_k: int = 10) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword matching."""
        semantic_results = self.search(query, top_k)
        keyword_results = self._keyword_search(query, top_k)
        combined: Dict[str, SearchResult] = {}
        for i, r in enumerate(semantic_results):
            score = (1 - keyword_weight) * r.score
            combined[r.document.id] = SearchResult(
                document=r.document, score=score, rank=i + 1,
            )
        keyword_seen: set = set()
        for i, r in enumerate(keyword_results):
            kw_score = keyword_weight * (1.0 - i / max(len(keyword_results), 1))
            if r.document.id in combined:
                combined[r.document.id].score += kw_score
            else:
                combined[r.document.id] = SearchResult(
                    document=r.document, score=kw_score, rank=len(combined) + 1,
                )
            keyword_seen.add(r.document.id)
        results = sorted(combined.values(), key=lambda x: x.score, reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1
        return results[:top_k]

    def _keyword_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Simple keyword-based search fallback."""
        terms = query.lower().split()
        results: List[SearchResult] = []
        for doc in self._index._documents.values():
            content_lower = doc.content.lower()
            score = sum(1 for t in terms if t in content_lower) / max(len(terms), 1)
            if score > 0:
                results.append(SearchResult(document=doc, score=score))
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]


class KnowledgeBase:
    """Knowledge base for structured and unstructured data storage.

    Provides document management, categorization, and retrieval
    for AI-powered applications.
    """

    def __init__(self, name: str = "default") -> None:
        self._name = name
        self._documents: Dict[str, Document] = {}
        self._categories: Dict[str, List[str]] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def document_count(self) -> int:
        return len(self._documents)

    def add_document(self, doc: Document, category: str = "") -> None:
        """Add a document to the knowledge base."""
        self._documents[doc.id] = doc
        if category:
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(doc.id)

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        return self._documents.get(doc_id)

    def remove_document(self, doc_id: str) -> None:
        """Remove a document by ID."""
        self._documents.pop(doc_id, None)
        for cat in self._categories.values():
            if doc_id in cat:
                cat.remove(doc_id)

    def get_by_category(self, category: str) -> List[Document]:
        """Get all documents in a category."""
        doc_ids = self._categories.get(category, [])
        return [self._documents[did] for did in doc_ids if did in self._documents]

    def search(self, query: str) -> List[Document]:
        """Simple keyword search across all documents."""
        terms = query.lower().split()
        results: List[Tuple[Document, int]] = []
        for doc in self._documents.values():
            score = sum(1 for t in terms if t in doc.content.lower())
            if score > 0:
                results.append((doc, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results]

    def categories(self) -> List[str]:
        """List all categories."""
        return list(self._categories.keys())


@dataclass
class RAGContext:
    """Context for RAG (Retrieval-Augmented Generation)."""

    query: str = ""
    retrieved_docs: List[Document] = field(default_factory=list)
    context_text: str = ""
    prompt: str = ""


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline.

    Retrieves relevant documents for a query and constructs
    a rich prompt with context for LLM-based generation.
    """

    def __init__(self, retriever: Optional[SemanticSearch] = None,
                 knowledge_base: Optional[KnowledgeBase] = None) -> None:
        self._retriever = retriever or SemanticSearch()
        self._knowledge_base = knowledge_base or KnowledgeBase()
        self._max_docs: int = 5
        self._max_chars: int = 4000

    @property
    def retriever(self) -> SemanticSearch:
        return self._retriever

    @property
    def knowledge_base(self) -> KnowledgeBase:
        return self._knowledge_base

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """Retrieve relevant documents for a query."""
        results = self._retriever.search(query, top_k=top_k)
        return [r.document for r in results]

    def build_context(self, query: str, top_k: Optional[int] = None) -> RAGContext:
        """Build a RAG context with retrieved documents."""
        k = top_k or self._max_docs
        docs = self.retrieve(query, top_k=k)
        context_parts = []
        char_count = 0
        selected_docs: List[Document] = []
        for doc in docs:
            if char_count + len(doc.content) > self._max_chars:
                break
            context_parts.append(f"Document [{doc.id}]:\n{doc.content}")
            selected_docs.append(doc)
            char_count += len(doc.content)
        context_text = "\n\n".join(context_parts)
        prompt = self._build_prompt(query, context_text)
        return RAGContext(
            query=query,
            retrieved_docs=selected_docs,
            context_text=context_text,
            prompt=prompt,
        )

    def _build_prompt(self, query: str, context: str) -> str:
        """Build a prompt with context for LLM generation."""
        return (
            f"You are an AI assistant. Use the following context to answer the question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )

    def set_max_docs(self, count: int) -> None:
        self._max_docs = count

    def set_max_chars(self, chars: int) -> None:
        self._max_chars = chars
