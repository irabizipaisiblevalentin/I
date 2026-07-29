from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ModelArchitecture(str, Enum):
    TRANSFORMER = "transformer"
    DIFFUSION = "diffusion"
    VISION = "vision"
    AUDIO = "audio"
    TIME_SERIES = "time_series"
    GRAPH_NEURAL = "graph_neural"
    CLASSICAL_ML = "classical_ml"
    FUTURE = "future"
    CUSTOM = "custom"
    ENSEMBLE = "ensemble"
    MIXTURE_OF_EXPERTS = "mixture_of_experts"
    STATE_SPACE = "state_space"


class ModelTask(str, Enum):
    TEXT_GENERATION = "text_generation"
    TEXT_CLASSIFICATION = "text_classification"
    TEXT_EMBEDDING = "text_embedding"
    QUESTION_ANSWERING = "question_answering"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    IMAGE_SEGMENTATION = "image_segmentation"
    IMAGE_GENERATION = "image_generation"
    OCR = "ocr"
    FACE_DETECTION = "face_detection"
    SPEECH_RECOGNITION = "speech_recognition"
    SPEECH_SYNTHESIS = "speech_synthesis"
    SPEECH_DIARIZATION = "speech_diarization"
    AUDIO_CLASSIFICATION = "audio_classification"
    MUSIC_GENERATION = "music_generation"
    TIME_SERIES_FORECAST = "time_series_forecast"
    TIME_SERIES_ANOMALY = "time_series_anomaly"
    RECOMMENDATION = "recommendation"
    RERANKING = "reranking"
    EMBEDDING = "embedding"
    REWARD_MODEL = "reward_model"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    CUSTOM = "custom"


class ModelSource(str, Enum):
    LOCAL = "local"
    HUGGINGFACE = "huggingface"
    OFFICIAL_I = "official_i"
    CLOUD = "cloud"
    ENTERPRISE = "enterprise"
    OFFLINE = "offline"
    EDGE = "edge"
    COMMUNITY = "community"
    CUSTOM = "custom"


class InferenceMode(str, Enum):
    STREAMING = "streaming"
    BATCH = "batch"
    REAL_TIME = "real_time"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"
    EDGE = "edge"


class Precision(str, Enum):
    FP32 = "fp32"
    FP16 = "fp16"
    BF16 = "bf16"
    INT8 = "int8"
    INT4 = "int4"
    MIXED = "mixed"
    AUTO = "auto"


class DeviceType(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    MPS = "mps"
    XPU = "xpu"
    NPU = "npu"
    TPU = "tpu"
    WEBGPU = "webgpu"
    VULKAN = "vulkan"
    OPENCL = "opencl"
    AUTO = "auto"


@dataclass
class ModelConfig:
    model_id: str = ""
    architecture: ModelArchitecture = ModelArchitecture.TRANSFORMER
    task: ModelTask = ModelTask.TEXT_GENERATION
    source: ModelSource = ModelSource.LOCAL
    path: str = ""
    revision: str = "main"
    precision: Precision = Precision.AUTO
    device: DeviceType = DeviceType.AUTO
    max_length: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repetition_penalty: float = 1.0
    stop_sequences: List[str] = field(default_factory=list)
    system_prompt: str = ""
    context_length: int = 4096
    batch_size: int = 1
    num_gpus: int = 0
    quantized: bool = False
    use_cache: bool = True
    trust_remote_code: bool = False
    api_key: str = ""
    endpoint: str = ""
    timeout: int = 30
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "architecture": self.architecture.value,
            "task": self.task.value,
            "source": self.source.value,
            "path": self.path,
            "precision": self.precision.value,
            "device": self.device.value,
            "max_length": self.max_length,
            "temperature": self.temperature,
            "context_length": self.context_length,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ModelConfig:
        return cls(
            model_id=data.get("model_id", ""),
            architecture=ModelArchitecture(data.get("architecture", "transformer")),
            task=ModelTask(data.get("task", "text_generation")),
            source=ModelSource(data.get("source", "local")),
            path=data.get("path", ""),
            precision=Precision(data.get("precision", "auto")),
            device=DeviceType(data.get("device", "auto")),
            max_length=data.get("max_length", 2048),
            temperature=data.get("temperature", 0.7),
            context_length=data.get("context_length", 4096),
            tags=data.get("tags", []),
        )


@dataclass
class ModelInfo:
    config: ModelConfig = field(default_factory=ModelConfig)
    loaded: bool = False
    loaded_at: str = ""
    memory_usage_mb: float = 0.0
    inference_count: int = 0
    total_inference_time_ms: float = 0.0
    error_count: int = 0
    status: str = "unloaded"
    capabilities: List[str] = field(default_factory=list)

    @property
    def avg_inference_time_ms(self) -> float:
        if self.inference_count == 0:
            return 0.0
        return self.total_inference_time_ms / self.inference_count


MODEL_REGISTRY: Dict[str, ModelInfo] = {}


def register_model(config: ModelConfig) -> str:
    model_id = config.model_id or f"{config.architecture.value}_{config.task.value}_{len(MODEL_REGISTRY)}"
    config.model_id = model_id
    MODEL_REGISTRY[model_id] = ModelInfo(config=config)
    return model_id


def get_model(model_id: str) -> Optional[ModelInfo]:
    return MODEL_REGISTRY.get(model_id)


def list_models(task: Optional[ModelTask] = None,
                architecture: Optional[ModelArchitecture] = None) -> List[str]:
    results = []
    for mid, info in MODEL_REGISTRY.items():
        if task and info.config.task != task:
            continue
        if architecture and info.config.architecture != architecture:
            continue
        results.append(mid)
    return results
