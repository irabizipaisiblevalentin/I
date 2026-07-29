# AI Guide — Core Inference

## Basic Inference

```python
from ubwenge import get_engine, InferenceRequest
from ubwenge.ubwoko import ModelConfig, ModelArchitecture, ModelTask

engine = get_engine()

config = ModelConfig(
    model_id="my_model",
    architecture=ModelArchitecture.TRANSFORMER,
    task=ModelTask.TEXT_GENERATION,
)
engine.load_model(config)

result = engine.infer("What is the capital of France?", model_id="my_model")
print(result.text)
```

## Streaming Inference

```python
for chunk in engine.infer("Tell me a story about AI", model_id="my_model", stream=True):
    print(chunk.text, end="", flush=True)
```

## Batch Inference

```python
from ubwenge.iyerekana import InferenceRequest, InferencePipeline

pipeline = InferencePipeline()
requests = [
    InferenceRequest(prompt="Question 1?", model_id="my_model"),
    InferenceRequest(prompt="Question 2?", model_id="my_model"),
    InferenceRequest(prompt="Question 3?", model_id="my_model"),
]
results = pipeline.infer_batch(requests)
```

## Concurrent Inference

```python
results = pipeline.infer_concurrent(requests, max_workers=4)
```

## Pipeline Orchestration

```python
from ubwenge.ikorwa import Pipeline

pipe = Pipeline(name="qa_pipeline")
pipe.add_step_fn("validate", lambda ctx: {"valid": True})
pipe.add_step_fn("infer", lambda ctx: {"output": "Answer"})
pipe.add_step_fn("format", lambda ctx: {"result": f"Q: ... A: ..."})

context = pipe.run({"question": "What is AI?"})
```
