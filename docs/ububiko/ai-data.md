# AI Data Guide (Ubushakashatsi)

## Embedding Service

```python
from ububiko.ubushakashatsi import EmbeddingService

emb = EmbeddingService(dimensions=384)
vector = emb.embed("I Programming Language")
batch = emb.embed_batch(["text1", "text2", "text3"])
sim = emb.similarity(vector_a, vector_b)
```

## Vector Index

```python
from ububiko.ubushakashatsi import VectorIndex, Document

index = VectorIndex(dimensions=384)
doc = Document(content="UBUBIKO is the data platform of I Language")
doc.embedding = emb.embed(doc.content)
index.add(doc)

query_vec = emb.embed("data platform")
results = index.search(query_vec, top_k=5)
```

## Semantic Search

```python
from ububiko.ubushakashatsi import SemanticSearch

search = SemanticSearch(embedding_service=emb)
search.index_document(doc)
search.index_documents(docs)

results = search.search("I Language data", top_k=5)
hybrid = search.hybrid_search("I Language data", keyword_weight=0.3)
```

## Knowledge Base

```python
from ububiko.ubushakashatsi import KnowledgeBase

kb = KnowledgeBase("my-knowledge")
kb.add_document(doc, category="documentation")
docs = kb.get_by_category("documentation")
```

## RAG Pipeline

```python
from ububiko.ubushakashatsi import RAGPipeline

rag = RAGPipeline(retriever=search, knowledge_base=kb)
rag.set_max_docs(5)
rag.set_max_chars(4000)

context = rag.build_context("What is UBUBIKO?")
print(context.prompt)  # Ready for LLM
```
