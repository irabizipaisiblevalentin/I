# UBWENGE Architecture — The Official AI Platform of the I Language

## Overview

UBWENGE (Kinyarwanda: "intelligence/knowledge") is the official Artificial
Intelligence platform of the I Programming Language. It provides a unified,
first-class AI capability across the entire I ecosystem — from inference
and agents to vision, speech, training, and security.

## Design Principles

1. **AI is a first-class capability** — not an optional library or add-on
2. **Unified architecture** — all AI domains share common patterns and APIs
3. **Security by default** — every input is validated, every output is safe
4. **Performance at every layer** — caching, quantization, batching, profiling
5. **Extensible by design** — custom models, tools, memories, and generators

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UBWENGE Platform                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────┐  │
│  │  Inference   │  │    Agents    │  │   Memory   │  │  Prompts  │  │
│  │  (iyerekana) │  │  (umukozi)   │  │ (urwibutso)│  │(igiteke.) │  │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘  └─────┬─────┘  │
│         │                 │                 │               │        │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐  ┌───┴──────┐ │
│  │     RAG      │  │    Vision   │  │   Speech    │  │ Training │ │
│  │  (gushaka)   │  │   (amaso)   │  │  (amajwi)   │  │(amahug.)│ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │                 │               │        │
│  ┌──────┴──────────────────┴─────────────────┴───────────────┴─────┐ │
│  │                    Security (umutekano)                          │ │
│  │     Injection · Content Safety · Bias · Audit · Policy          │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │              Performance (imikorere)                              │ │
│  │     Cache · Quantize · Batch · Profile · Optimize                │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │              Runtime (ikorwa)                                     │ │
│  │     Engine · Pipeline · Hooks · Model Registry                   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│              CLI (itegeko) — isoko ubwenge [...]                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Modules

| Module | File | Purpose |
|--------|------|---------|
| ikorwa | `ikorwa.py` | Core runtime, model lifecycle, pipeline orchestration |
| ubwoko | `ubwoko.py` | Model types, configurations, registry |
| iyerekana | `iyerekana.py` | Inference engine: streaming, batch, distributed |
| umukozi | `umukozi.py` | Agent platform: single, multi-agent, tools |
| urwibutso | `urwibutso.py` | Memory: short-term, long-term, vector, knowledge graph |
| igitekerezo | `igitekerezo.py` | Prompt templates, versioning, testing, security |
| gushaka | `gushaka.py` | RAG: indexing, hybrid search, knowledge bases |
| amaso | `amaso.py` | Computer vision: classification, detection, OCR |
| amajwi | `amajwi.py` | Speech: recognition, synthesis, diarization |
| amahugurwa | `amahugurwa.py` | Training: datasets, fine-tuning, distributed |
| umutekano | `umutekano.py` | Security: injection, content safety, bias, audit |
| imikorere | `imikorere.py` | Performance: cache, quantization, profiling |
| ibikoresho | `ibikoresho.py` | Utilities, errors, registry, serialization |
| itegeko | `itegeko.py` | CLI: isoko ubwenge subcommands |

## Key Features

### Inference
- Streaming, batch, real-time, and distributed inference modes
- Model caching, quantization (INT8, INT4, FP16), batching
- Profiling and performance metrics

### Agents
- Single-agent with tool calling and planning
- Multi-agent orchestration and debate
- Reflection, memory, and self-evaluation

### Memory
- Short-term (conversation context window)
- Long-term (SQLite-backed persistent storage)
- Vector memory (cosine similarity search)
- Knowledge graphs (nodes, edges, traversal)

### RAG
- Document indexing with 5 chunking strategies
- Keyword (TF-IDF) and hybrid search
- Citation tracking and formatting

### Vision
- Classification, object detection, OCR, face detection
- Segmentation, image enhancement
- Support for medical and industrial imaging

### Speech
- Recognition, synthesis (TTS), diarization
- Voice identification, language detection
- Noise reduction

### Training
- Dataset management with train/validation/test splits
- Fine-tuning configuration
- Training run tracking with loss history
- Evaluation metrics

### Security
- Prompt injection detection (12+ attack patterns)
- Content safety (6 categories)
- Bias monitoring (8 bias types)
- Policy enforcement and audit logging

### Performance
- LRU model cache with TTL and size limits
- INT8/INT4 quantization estimators
- Request batching
- Profiling with p50/p95/p99 latency

## CLI Usage

```bash
# Model inference
isoko ubwenge infer "What is AI?" --model default

# Streaming inference
isoko ubwenge infer "Tell me a story" --stream

# Benchmark
isoko ubwenge benchmark --model default --iterations 20

# Train a model
isoko ubwenge train --model my_model --dataset my_data --epochs 5

# Run an agent
isoko ubwenge agent "Research quantum computing" --name researcher

# Manage prompt templates
isoko ubwenge prompt create my_template --template "Hello {name}!"
isoko ubwenge prompt render my_template --vars name=World

# Inspect loaded models
isoko ubwenge inspect
isoko ubwenge inspect my_model

# Publish a model
isoko ubwenge publish my_model --version 2.0.0

# Create a new project
isoko ubwenge new my_ai_project --type project
```

## Domain-Specific Guides

See [docs/ubwenge/](docs/ubwenge/) for:
- [AI Guide](docs/ubwenge/ai.md) — Core AI concepts and inference
- [Agent Guide](docs/ubwenge/agent.md) — Building AI agents
- [Vision Guide](docs/ubwenge/vision.md) — Computer vision
- [Speech Guide](docs/ubwenge/speech.md) — Speech processing
- [Training Guide](docs/ubwenge/training.md) — Model training
- [Security Guide](docs/ubwenge/security.md) — AI security
- [Performance Guide](docs/ubwenge/performance.md) — Optimization
- [Enterprise Guide](docs/ubwenge/enterprise.md) — Production deployment
