"""RAG platform — document indexing, embeddings, chunking, hybrid search, knowledge bases, citations."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple
from enum import Enum


class ChunkStrategy(str, Enum):
    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    SEMANTIC = "semantic"
    RECURSIVE = "recursive"
    TOKEN = "token"


class RetrievalStrategy(str, Enum):
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    ENSEMBLE = "ensemble"


@dataclass
class Document:
    doc_id: str = ""
    content: str = ""
    title: str = ""
    source: str = ""
    content_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunks: List[str] = field(default_factory=list)
    embeddings: Optional[List[List[float]]] = None
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if not self.doc_id:
            try:
                digest = hashlib.md5(self.content.encode(), usedforsecurity=False)
            except TypeError:  # Python < 3.9
                digest = hashlib.md5(self.content.encode())
            self.doc_id = digest.hexdigest()[:16]
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class Chunk:
    chunk_id: str = ""
    doc_id: str = ""
    content: str = ""
    index: int = 0
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    content: str = ""
    doc_id: str = ""
    chunk_id: str = ""
    score: float = 0.0
    source: str = ""
    title: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    rank: int = 0


class DocumentIndexer:
    def __init__(self, chunk_strategy: ChunkStrategy = ChunkStrategy.PARAGRAPH,
                 chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_strategy = chunk_strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._documents: Dict[str, Document] = {}
        self._chunks: Dict[str, Chunk] = {}

    def add_document(self, content: str, title: str = "", source: str = "",
                     content_type: str = "text",
                     metadata: Optional[Dict[str, Any]] = None) -> Document:
        doc = Document(
            content=content, title=title, source=source,
            content_type=content_type, metadata=metadata or {},
        )
        doc.chunks = self._chunk_text(content)
        self._documents[doc.doc_id] = doc
        return doc

    def add_file(self, path: str) -> Optional[Document]:
        p = Path(path)
        if not p.exists():
            return None
        content = p.read_text(encoding="utf-8")
        return self.add_document(content=content, title=p.stem,
                                 source=str(p), content_type=p.suffix)

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self._documents.get(doc_id)

    def list_documents(self) -> List[str]:
        return list(self._documents.keys())

    def remove_document(self, doc_id: str) -> bool:
        if doc_id in self._documents:
            del self._documents[doc_id]
            return True
        return False

    def clear(self) -> None:
        self._documents.clear()
        self._chunks.clear()

    def _chunk_text(self, text: str) -> List[str]:
        if self.chunk_strategy == ChunkStrategy.FIXED_SIZE:
            return self._chunk_fixed(text)
        elif self.chunk_strategy == ChunkStrategy.PARAGRAPH:
            return self._chunk_paragraph(text)
        elif self.chunk_strategy == ChunkStrategy.SENTENCE:
            return self._chunk_sentence(text)
        elif self.chunk_strategy == ChunkStrategy.TOKEN:
            return self._chunk_token(text)
        elif self.chunk_strategy == ChunkStrategy.RECURSIVE:
            return self._chunk_recursive(text)
        return self._chunk_paragraph(text)

    def _chunk_fixed(self, text: str) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        return chunks

    def _chunk_paragraph(self, text: str) -> List[str]:
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _chunk_sentence(self, text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current = ""
        for s in sentences:
            if len(current) + len(s) > self.chunk_size and current:
                chunks.append(current.strip())
                current = s
            else:
                current += " " + s if current else s
        if current.strip():
            chunks.append(current.strip())
        return chunks

    def _chunk_token(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        return chunks

    def _chunk_recursive(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]
        for sep in ["\n\n", "\n", ". "]:
            parts = text.split(sep)
            if len(parts) > 1:
                chunks = []
                current = ""
                for p in parts:
                    sep_len = len(sep)
                    if len(current) + len(p) + sep_len > self.chunk_size and current:
                        chunks.append(current.strip())
                        current = p
                    else:
                        current += (sep if current else "") + p
                if current.strip():
                    chunks.append(current.strip())
                return chunks
        return self._chunk_fixed(text)


class KeywordIndex:
    def __init__(self):
        self._inverted: Dict[str, Dict[str, float]] = {}
        self._doc_lengths: Dict[str, int] = {}
        self._total_docs: int = 0

    def index_document(self, doc_id: str, text: str) -> None:
        tokens = re.findall(r"\w+", text.lower())
        self._doc_lengths[doc_id] = len(tokens)
        self._total_docs += 1
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        for token, count in tf.items():
            if token not in self._inverted:
                self._inverted[token] = {}
            self._inverted[token][doc_id] = count / len(tokens) if tokens else 0

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        tokens = re.findall(r"\w+", query.lower())
        if not tokens:
            return []
        scores: Dict[str, float] = {}
        for token in tokens:
            posting = self._inverted.get(token, {})
            idf = math.log((self._total_docs + 1) / (len(posting) + 1)) + 1
            for doc_id, tf in posting.items():
                scores[doc_id] = scores.get(doc_id, 0) + tf * idf
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def count(self) -> int:
        return len(self._inverted)


class KnowledgeBase:
    def __init__(self, name: str = "default", storage_path: str = "./knowledge"):
        self.name = name
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.indexer = DocumentIndexer()
        self.keyword = KeywordIndex()
        self._lock = threading.RLock()

    def add_text(self, content: str, title: str = "", source: str = "",
                 metadata: Optional[Dict[str, Any]] = None) -> str:
        with self._lock:
            doc = self.indexer.add_document(content, title=title, source=source, metadata=metadata)
            self.keyword.index_document(doc.doc_id, content)
            return doc.doc_id

    def add_file(self, path: str) -> Optional[str]:
        doc = self.indexer.add_file(path)
        if doc:
            with self._lock:
                self.keyword.index_document(doc.doc_id, doc.content)
                return doc.doc_id
        return None

    def retrieve(self, query: str, strategy: RetrievalStrategy = RetrievalStrategy.HYBRID,
                 top_k: int = 5) -> List[RetrievalResult]:
        results = []

        kw_results = self.keyword.search(query, top_k=top_k)
        seen = set()
        for doc_id, score in kw_results:
            doc = self.indexer.get_document(doc_id)
            if doc and doc_id not in seen:
                seen.add(doc_id)
                results.append(RetrievalResult(
                    content=doc.content[:500],
                    doc_id=doc_id,
                    score=score * 0.5,
                    source=doc.source,
                    title=doc.title,
                    rank=len(results) + 1,
                ))

        if strategy == RetrievalStrategy.KEYWORD:
            return results[:top_k]

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def list(self) -> List[str]:
        return self.indexer.list_documents()

    def count(self) -> int:
        return len(self.indexer._documents)

    def clear(self) -> None:
        with self._lock:
            self.indexer.clear()
            self.keyword = KeywordIndex()


class CitationTracker:
    def __init__(self):
        self._citations: List[Dict[str, Any]] = []

    def add_citation(self, doc_id: str, source: str, content: str,
                     relevance: float = 1.0) -> str:
        cid = f"cit_{len(self._citations)}_{int(time.time())}"
        self._citations.append({
            "citation_id": cid,
            "doc_id": doc_id,
            "source": source,
            "content": content[:200],
            "relevance": relevance,
            "timestamp": time.time(),
        })
        return cid

    def format_citations(self, style: str = "inline") -> str:
        if not self._citations:
            return ""
        if style == "inline":
            parts = [f"[{c['citation_id']}] {c['source']}" for c in self._citations]
        elif style == "numbered":
            parts = [f"{i+1}. {c['source']}" for i, c in enumerate(self._citations)]
        else:
            parts = [f"- {c['source']}: {c['content'][:100]}" for c in self._citations]
        return "\n".join(parts)

    def clear(self) -> None:
        self._citations.clear()
