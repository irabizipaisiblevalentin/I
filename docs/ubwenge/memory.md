# Memory Guide

## Short-Term Memory

```python
from ubwenge.urwibutso import ShortTermMemory

stm = ShortTermMemory(capacity=50)
stm.add("user", "What is AI?")
stm.add("assistant", "AI is artificial intelligence.")
context = stm.get_context(max_tokens=4000)
```

## Long-Term Memory (SQLite)

```python
from ubwenge.urwibutso import LongTermMemory

ltm = LongTermMemory(storage_path="./memory/ltm")
ltm.store(MemoryEntry(content="Important fact about AI", importance=0.9))
results = ltm.search("AI")
```

## Vector Memory

```python
from ubwenge.urwibutso import VectorMemory

vm = VectorMemory(dimension=384)
vm.store(MemoryEntry(content="AI is transforming industries", embedding=[0.1]*384))
results = vm.search(query_embedding=[0.1]*384, top_k=5)
```

## Knowledge Graph

```python
from ubwenge.urwibutso import KnowledgeGraph

kg = KnowledgeGraph()
kg.add_node("ai", label="concept", properties={"description": "Artificial Intelligence"})
kg.add_node("ml", label="concept")
kg.add_edge("ai", "ml", "includes")
neighbors = kg.get_neighbors("ai", max_depth=2)
```

## Conversation Memory

```python
from ubwenge.urwibutso import ConversationMemory

cm = ConversationMemory(max_turns=100)
cm.add_turn("Hello", "Hi! How can I help?")
history = cm.get_history(limit=5)
summary = cm.summarize(max_turns=3)
```
