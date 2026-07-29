# RAG Guide — Retrieval-Augmented Generation

## Document Indexing

```python
from ubwenge.gushaka import DocumentIndexer, ChunkStrategy

indexer = DocumentIndexer(chunk_strategy=ChunkStrategy.PARAGRAPH)
doc = indexer.add_document(
    content="Long document content...",
    title="AI Overview",
    source="ai.txt",
)
```

## Knowledge Base

```python
from ubwenge.gushaka import KnowledgeBase, RetrievalStrategy

kb = KnowledgeBase(name="my_kb")
kb.add_text("Artificial Intelligence is transforming the world.", title="AI")
kb.add_text("Machine Learning is a subset of AI.", title="ML")

results = kb.retrieve("What is AI?", strategy=RetrievalStrategy.HYBRID, top_k=5)
for r in results:
    print(f"[{r.score:.2f}] {r.content[:100]}...")
```

## Citations

```python
from ubwenge.gushaka import CitationTracker

ct = CitationTracker()
ct.add_citation("doc1", "AI Paper 2024", "AI is...", relevance=0.95)
print(ct.format_citations(style="numbered"))
```
