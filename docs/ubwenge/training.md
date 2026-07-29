# Training Guide — Model Training

## Creating a Dataset

```python
from ubwenge.amahugurwa import Dataset, DatasetSplit

ds = Dataset(name="qa_pairs")
ds.add("What is AI?", "AI is artificial intelligence.")
ds.add("What is ML?", "ML is machine learning.", split=DatasetSplit.VALIDATION)
ds.add("What is deep learning?", "Deep learning uses neural networks.", split=DatasetSplit.TEST)
```

## Training Configuration

```python
from ubwenge.amahugurwa import TrainingConfig, TrainingEngine

engine = TrainingEngine()
engine.register_dataset(ds)

config = TrainingConfig(
    model_id="my_model",
    dataset_name="qa_pairs",
    learning_rate=3e-5,
    batch_size=8,
    epochs=3,
    fp16=True,
)

run_id = engine.start_run(config)
engine.simulate_training(run_id, steps=50)

run = engine.get_run(run_id)
print(f"Final loss: {run.loss_history[-1]:.4f}")
```

## Evaluation

```python
metrics = engine.evaluate(run_id)
print(f"Accuracy: {metrics['accuracy']:.2f}")
print(f"F1: {metrics['f1_score']:.2f}")
```
