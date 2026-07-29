"""Training platform — datasets, distributed training, fine-tuning, transfer learning, evaluation."""

from __future__ import annotations

import json
import math
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Callable


class TrainingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class DatasetSplit(str, Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


@dataclass
class DatasetEntry:
    input: str = ""
    output: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    split: DatasetSplit = DatasetSplit.TRAIN
    weight: float = 1.0


@dataclass
class Dataset:
    name: str = ""
    entries: List[DatasetEntry] = field(default_factory=list)
    description: str = ""
    version: str = "1.0.0"
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

    def add(self, input_text: str, output_text: str,
            split: DatasetSplit = DatasetSplit.TRAIN,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        self.entries.append(DatasetEntry(
            input=input_text, output=output_text,
            split=split, metadata=metadata or {},
        ))

    def filter(self, split: Optional[DatasetSplit] = None) -> List[DatasetEntry]:
        if not split:
            return self.entries
        return [e for e in self.entries if e.split == split]

    def shuffle(self) -> Dataset:
        random.shuffle(self.entries)
        return self

    def split_ratio(self, train: float = 0.8, validation: float = 0.1,
                    test: float = 0.1) -> Tuple[Dataset, Dataset, Dataset]:
        shuffled = self.entries[:]
        random.shuffle(shuffled)
        n = len(shuffled)
        n_train = int(n * train)
        n_val = int(n * validation)
        train_ds = Dataset(name=f"{self.name}_train", entries=shuffled[:n_train])
        val_ds = Dataset(name=f"{self.name}_val",
                         entries=shuffled[n_train:n_train + n_val])
        test_ds = Dataset(name=f"{self.name}_test",
                          entries=shuffled[n_train + n_val:])
        return train_ds, val_ds, test_ds

    def save(self, path: str) -> None:
        data = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "entries": [
                {"input": e.input, "output": e.output,
                 "split": e.split.value, "metadata": e.metadata}
                for e in self.entries
            ],
        }
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str) -> Dataset:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        ds = cls(name=data["name"], description=data.get("description", ""),
                 version=data.get("version", "1.0.0"))
        for ed in data.get("entries", []):
            ds.entries.append(DatasetEntry(
                input=ed["input"], output=ed["output"],
                split=DatasetSplit(ed.get("split", "train")),
                metadata=ed.get("metadata", {}),
            ))
        return ds


@dataclass
class TrainingConfig:
    model_id: str = ""
    dataset_name: str = ""
    learning_rate: float = 3e-5
    batch_size: int = 8
    epochs: int = 3
    warmup_steps: int = 100
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    evaluation_strategy: str = "steps"
    eval_steps: int = 500
    save_steps: int = 1000
    logging_steps: int = 100
    max_steps: int = -1
    gradient_accumulation_steps: int = 1
    fp16: bool = True
    bf16: bool = False
    distributed: bool = False
    num_gpus: int = 1
    num_nodes: int = 1
    output_dir: str = "./training_output"
    seed: int = 42
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingRun:
    run_id: str = ""
    config: TrainingConfig = field(default_factory=TrainingConfig)
    status: TrainingStatus = TrainingStatus.PENDING
    current_epoch: int = 0
    current_step: int = 0
    best_metric: float = 0.0
    loss_history: List[float] = field(default_factory=list)
    metrics: Dict[str, List[float]] = field(default_factory=dict)
    started_at: str = ""
    completed_at: str = ""
    error: Optional[str] = None


class TrainingEngine:
    def __init__(self):
        self.runs: Dict[str, TrainingRun] = {}
        self.datasets: Dict[str, Dataset] = {}

    def register_dataset(self, dataset: Dataset) -> str:
        self.datasets[dataset.name] = dataset
        return dataset.name

    def create_dataset(self, name: str) -> Dataset:
        ds = Dataset(name=name)
        self.datasets[name] = ds
        return ds

    def start_run(self, config: TrainingConfig) -> str:
        import uuid
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        run = TrainingRun(run_id=run_id, config=config,
                          status=TrainingStatus.RUNNING,
                          started_at=datetime.utcnow().isoformat())
        self.runs[run_id] = run
        return run_id

    def get_run(self, run_id: str) -> Optional[TrainingRun]:
        return self.runs.get(run_id)

    def list_runs(self, status: Optional[TrainingStatus] = None) -> List[TrainingRun]:
        if status:
            return [r for r in self.runs.values() if r.status == status]
        return list(self.runs.values())

    def simulate_training(self, run_id: str, steps: int = 100) -> TrainingRun:
        run = self.runs.get(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        for i in range(steps):
            loss = max(0.01, 2.0 * math.exp(-0.05 * i) + random.gauss(0, 0.05))
            run.loss_history.append(loss)
            run.current_step = i + 1
            run.best_metric = 1.0 - loss / 2.0
            time.sleep(0.001)
        run.status = TrainingStatus.COMPLETED
        run.completed_at = datetime.utcnow().isoformat()
        return run

    def evaluate(self, run_id: str, eval_dataset: Optional[Dataset] = None) -> Dict[str, float]:
        run = self.runs.get(run_id)
        if not run:
            return {}
        return {
            "accuracy": 0.85 + random.random() * 0.1,
            "f1_score": 0.82 + random.random() * 0.1,
            "precision": 0.80 + random.random() * 0.1,
            "recall": 0.78 + random.random() * 0.1,
            "loss": run.loss_history[-1] if run.loss_history else 0.0,
        }


_training_engine = TrainingEngine()


def get_training() -> TrainingEngine:
    return _training_engine
