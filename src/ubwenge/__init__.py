"""UBWENGE — The official Artificial Intelligence platform of the I Programming Language.

A complete platform for building AI applications: inference, agents, memory,
RAG, vision, speech, training, security, and performance optimization.
"""

from __future__ import annotations

from .ubwoko import (
    ModelArchitecture, ModelTask, ModelSource, InferenceMode,
    Precision, DeviceType, ModelConfig, ModelInfo,
    register_model, get_model, list_models, MODEL_REGISTRY,
)
from .iyerekana import (
    InferenceRequest, InferenceResult, InferenceStatus, InferencePipeline,
    BaseInferenceEngine, MockInferenceEngine,
    get_pipeline, infer,
)
from .ikorwa import (
    UbwengeEngine, RuntimeConfig, Pipeline, PipelineStep,
    get_engine,
)
from .umukozi import (
    Agent, AgentConfig, AgentRole, AgentState, AgentMessage,
    ToolSpec, ToolCall, AgentOrchestrator,
    create_agent,
)
from .urwibutso import (
    MemoryEntry, MemoryStore, ShortTermMemory, LongTermMemory,
    VectorMemory, KnowledgeGraph, ConversationMemory,
)
from .igitekerezo import (
    PromptTemplate, PromptRegistry, PromptTester,
    PromptOptimizer, PromptSecurity, PromptStatus,
    get_registry, create_prompt,
)
from .gushaka import (
    Document, Chunk, DocumentIndexer, KnowledgeBase,
    CitationTracker, RetrievalResult, RetrievalStrategy,
    ChunkStrategy, KeywordIndex,
)
from .amaso import (
    VisionEngine, VisionTask,
    ClassificationResult, DetectionResult, OCRResult,
    FaceResult, SegmentationResult, ImageEnhancementResult,
    BoundingBox,
    get_vision,
)
from .amajwi import (
    SpeechEngine, SpeechTask,
    RecognitionResult, SynthesisResult, DiarizationResult,
    VoiceIDResult, LanguageDetectionResult, NoiseReductionResult,
    get_speech,
)
from .amahugurwa import (
    Dataset, DatasetEntry, DatasetSplit,
    TrainingConfig, TrainingRun, TrainingStatus, TrainingEngine,
    get_training,
)
from .umutekano import (
    SecurityManager, InjectionDetector, ContentSafetyChecker,
    BiasMonitor, PolicyEnforcer, AuditLogger,
    SecurityEvent, SecurityEventType, Severity,
    get_security,
)
from .imikorere import (
    PerformanceOptimizer, ModelCache, Quantizer, Batcher,
    Profiler, PerformanceMetrics, OptimizationLevel,
    get_optimizer,
)
from .ibikoresho import (
    UwagaRegistry, AIError, ModelLoadError, InferenceError,
    ConfigError, TimeHelpers, Serialization,
)
from .itegeko import register_subcommands, genda

__all__ = [
    # Core
    "UbwengeEngine", "RuntimeConfig", "Pipeline", "PipelineStep",
    "get_engine",
    # Model types
    "ModelArchitecture", "ModelTask", "ModelSource", "InferenceMode",
    "Precision", "DeviceType", "ModelConfig", "ModelInfo",
    "register_model", "get_model", "list_models", "MODEL_REGISTRY",
    # Inference
    "InferenceRequest", "InferenceResult", "InferenceStatus",
    "InferencePipeline", "BaseInferenceEngine", "MockInferenceEngine",
    "get_pipeline", "infer",
    # Agents
    "Agent", "AgentConfig", "AgentRole", "AgentState", "AgentMessage",
    "ToolSpec", "ToolCall", "AgentOrchestrator", "create_agent",
    # Memory
    "MemoryEntry", "MemoryStore", "ShortTermMemory", "LongTermMemory",
    "VectorMemory", "KnowledgeGraph", "ConversationMemory",
    # Prompts
    "PromptTemplate", "PromptRegistry", "PromptTester",
    "PromptOptimizer", "PromptSecurity", "PromptStatus",
    "get_registry", "create_prompt",
    # RAG
    "Document", "Chunk", "DocumentIndexer", "KnowledgeBase",
    "CitationTracker", "RetrievalResult", "RetrievalStrategy",
    "ChunkStrategy", "KeywordIndex",
    # Vision
    "VisionEngine", "VisionTask",
    "ClassificationResult", "DetectionResult", "OCRResult",
    "FaceResult", "SegmentationResult", "ImageEnhancementResult",
    "BoundingBox", "get_vision",
    # Speech
    "SpeechEngine", "SpeechTask",
    "RecognitionResult", "SynthesisResult", "DiarizationResult",
    "VoiceIDResult", "LanguageDetectionResult", "NoiseReductionResult",
    "get_speech",
    # Training
    "Dataset", "DatasetEntry", "DatasetSplit",
    "TrainingConfig", "TrainingRun", "TrainingStatus", "TrainingEngine",
    "get_training",
    # Security
    "SecurityManager", "InjectionDetector", "ContentSafetyChecker",
    "BiasMonitor", "PolicyEnforcer", "AuditLogger",
    "SecurityEvent", "SecurityEventType", "Severity", "get_security",
    # Performance
    "PerformanceOptimizer", "ModelCache", "Quantizer", "Batcher",
    "Profiler", "PerformanceMetrics", "OptimizationLevel",
    "get_optimizer",
    # Utilities
    "UwagaRegistry", "AIError", "ModelLoadError", "InferenceError",
    "ConfigError", "TimeHelpers", "Serialization",
    # CLI
    "register_subcommands", "genda",
]
