"""Prompt platform — templates, versioning, testing, benchmarking, optimization, security, analytics, registry."""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum


class PromptStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class PromptTemplate:
    name: str = ""
    template: str = ""
    description: str = ""
    variables: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    status: PromptStatus = PromptStatus.DRAFT
    system_prompt: str = ""
    expected_output_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, str]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if self.template:
            self.variables = re.findall(r"\{(\w+)\}", self.template)

    def render(self, **kwargs: Any) -> str:
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def validate(self, **kwargs: Any) -> Tuple[bool, List[str]]:
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            return False, [f"Missing variable: {v}" for v in missing]
        return True, []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
            "variables": self.variables,
            "version": self.version,
            "status": self.status.value,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class PromptRegistry:
    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._versions: Dict[str, List[PromptTemplate]] = {}

    def register(self, template: PromptTemplate) -> str:
        self._templates[template.name] = template
        if template.name not in self._versions:
            self._versions[template.name] = []
        self._versions[template.name].append(template)
        return template.name

    def get(self, name: str, version: Optional[str] = None) -> Optional[PromptTemplate]:
        if version:
            for t in self._versions.get(name, []):
                if t.version == version:
                    return t
            return None
        return self._templates.get(name)

    def list(self, tag: Optional[str] = None, status: Optional[PromptStatus] = None) -> List[str]:
        results = []
        for name, t in self._templates.items():
            if tag and tag not in t.tags:
                continue
            if status and t.status != status:
                continue
            results.append(name)
        return results

    def archive(self, name: str) -> bool:
        t = self._templates.get(name)
        if t:
            t.status = PromptStatus.ARCHIVED
            return True
        return False

    def save(self, path: str) -> None:
        data = {name: t.to_dict() for name, t in self._templates.items()}
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self, path: str) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for name, tdata in data.items():
            tdata["status"] = PromptStatus(tdata.get("status", "draft"))
            self._templates[name] = PromptTemplate(**tdata)


class PromptTester:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def test(self, template: PromptTemplate, test_cases: List[Dict[str, Any]],
             evaluator: Optional[Callable[[str], float]] = None) -> Dict[str, Any]:
        scores = []
        for case in test_cases:
            rendered = template.render(**case.get("variables", {}))
            expected = case.get("expected", "")
            if evaluator:
                score = evaluator(rendered)
            else:
                score = 1.0 if expected in rendered else 0.0
            scores.append({
                "case": case,
                "rendered": rendered,
                "score": score,
                "pass": score >= (case.get("threshold", 0.8)),
            })
        avg_score = sum(s["score"] for s in scores) / len(scores) if scores else 0.0
        result = {
            "template": template.name,
            "version": template.version,
            "test_count": len(scores),
            "pass_count": sum(1 for s in scores if s["pass"]),
            "average_score": avg_score,
            "results": scores,
        }
        self.results.append(result)
        return result


class PromptOptimizer:
    @staticmethod
    def optimize_length(template: PromptTemplate, max_chars: int = 2000) -> PromptTemplate:
        if len(template.template) <= max_chars:
            return template
        shortened = template.template[:max_chars]
        last_space = shortened.rfind(" ")
        if last_space > 0:
            shortened = shortened[:last_space]
        optimized = PromptTemplate(
            name=template.name, template=shortened + "...",
            description=template.description, version=template.version,
            tags=template.tags,
        )
        return optimized

    @staticmethod
    def suggest_improvements(template: PromptTemplate) -> List[str]:
        suggestions = []
        if len(template.template) < 50:
            suggestions.append("Template is too short; add more specific instructions")
        if not template.system_prompt:
            suggestions.append("Consider adding a system prompt")
        if len(template.variables) > 10:
            suggestions.append("Reduce number of variables for better maintainability")
        if "example" not in template.template.lower():
            suggestions.append("Add few-shot examples to improve output quality")
        return suggestions


class PromptSecurity:
    @staticmethod
    def detect_injection(text: str) -> Tuple[bool, List[str]]:
        patterns = [
            (r"ignore\s+(all\s+)?(previous|above|below)", "Ignore previous instructions"),
            (r"forget\s+(everything|all)", "Forget instructions"),
            (r"you\s+are\s+(not|free|now)", "Role manipulation"),
            (r"system\s*:\s*", "System prompt injection"),
            (r"<\s*(script|iframe|img)", "HTML/JS injection"),
            (r"\!(important|critical|urgent)", "Urgency manipulation"),
            (r"(sudo|su\s+|chmod|rm\s+-rf)", "Command injection"),
        ]
        detected = []
        for pattern, desc in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(desc)
        return len(detected) > 0, detected

    @staticmethod
    def sanitize(text: str) -> str:
        text = re.sub(r"ignore\s+(all\s+)?(previous|above|below).*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"system\s*:\s*", "", text, flags=re.IGNORECASE)
        return text.strip()


_prompt_registry = PromptRegistry()


def get_registry() -> PromptRegistry:
    return _prompt_registry


def create_prompt(name: str, template: str, **kwargs: Any) -> PromptTemplate:
    pt = PromptTemplate(name=name, template=template, **kwargs)
    _prompt_registry.register(pt)
    return pt
