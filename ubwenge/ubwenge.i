/// ubwenge.i — The official Artificial Intelligence framework of the I Language
///
/// UBWENGE provides first-class support for:
///   - Inference (streaming, batch, distributed)
///   - AI Agents (single, multi-agent, tools, planning)
///   - Memory (short/long-term, vector, knowledge graph)
///   - Prompt management (templates, versioning, testing)
///   - RAG (document indexing, hybrid search, citations)
///   - Computer Vision (classification, detection, OCR)
///   - Speech (recognition, synthesis, diarization)
///   - Training (datasets, fine-tuning, distributed)
///   - Security (injection detection, content safety, bias monitoring)
///   - Performance (caching, quantization, profiling)

pub enum ModelArchitecture {
    Transformer = "transformer",
    Diffusion = "diffusion",
    Vision = "vision",
    Audio = "audio",
    TimeSeries = "time_series",
    GraphNeural = "graph_neural",
    ClassicalML = "classical_ml",
    Future = "future",
}

pub enum InferenceMode {
    Streaming = "streaming",
    Batch = "batch",
    RealTime = "real_time",
    Distributed = "distributed",
    Edge = "edge",
}

pub enum AgentRole {
    Assistant = "assistant",
    Researcher = "researcher",
    Coder = "coder",
    Planner = "planner",
    Critic = "critic",
    Custom = "custom",
}

pub struct ModelConfig {
    model_id: String,
    architecture: ModelArchitecture = ModelArchitecture.Transformer,
    path: String,
    precision: String = "auto",
    device: String = "auto",
    max_length: Int = 2048,
    temperature: Float = 0.7,
    system_prompt: String = "",
}

pub struct InferenceRequest {
    prompt: String,
    model_id: String,
    max_tokens: Int = 1024,
    temperature: Float = 0.7,
    stream: Bool = false,
}

pub struct InferenceResult {
    text: String,
    tokens: Int = 0,
    prompt_tokens: Int = 0,
    finish_reason: String = "stop",
    latency_ms: Float = 0.0,
}

pub struct Agent {
    name: String,
    role: AgentRole = AgentRole.Assistant,
    model_id: String = "default",
    system_prompt: String = "",
    tools: [ToolSpec] = [],
}

pub struct ToolSpec {
    name: String,
    description: String,
    parameters: {String: Any} = {},
}

pub fn infer(request: InferenceRequest) -> InferenceResult
pub fn infer_stream(request: InferenceRequest) -> Stream<InferenceResult>
pub fn create_agent(config: AgentConfig) -> Agent
pub fn agent_run(agent: Agent, task: String) -> String
pub fn train(model_id: String, dataset: Dataset) -> TrainingRun
pub fn load_model(config: ModelConfig) -> String
pub fn memory_store(key: String, content: String)
pub fn memory_search(query: String) -> [MemoryEntry]
pub fn prompt_render(template: String, vars: {String: Any}) -> String
pub fn rag_retrieve(query: String, knowledge_base: String) -> [Document]
pub fn vision_classify(image: String) -> ClassificationResult
pub fn speech_recognize(audio: String) -> RecognitionResult
