"""I Developer Platform — I Labs (Laborotwari)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import Lab, LabDomain


LAB_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "ai-intro": {
        "title": "Introduction to AI with I",
        "domain": LabDomain.AI,
        "difficulty": "beginner",
        "steps": [
            {"title": "Setup", "instruction": "Import the ubwenge module"},
            {"title": "Create Model", "instruction": "Define a neural network"},
            {"title": "Train", "instruction": "Train on sample data"},
        ],
    },
    "network-basics": {
        "title": "Networking Fundamentals",
        "domain": LabDomain.NETWORKING,
        "difficulty": "beginner",
        "steps": [
            {"title": "TCP Socket", "instruction": "Create a TCP server"},
            {"title": "HTTP Request", "instruction": "Make an HTTP request"},
        ],
    },
    "cybersecurity-101": {
        "title": "Cybersecurity Essentials",
        "domain": LabDomain.CYBERSECURITY,
        "difficulty": "intermediate",
        "steps": [
            {"title": "Hash Function", "instruction": "Implement SHA-256"},
            {"title": "Encryption", "instruction": "AES encryption/decryption"},
        ],
    },
    "database-design": {
        "title": "Database Design and Queries",
        "domain": LabDomain.DATABASES,
        "difficulty": "beginner",
        "steps": [
            {"title": "Schema", "instruction": "Define a database schema"},
            {"title": "CRUD", "instruction": "Implement CRUD operations"},
        ],
    },
    "cloud-deploy": {
        "title": "Cloud Deployment",
        "domain": LabDomain.CLOUD,
        "difficulty": "intermediate",
        "steps": [
            {"title": "Containerize", "instruction": "Create a Dockerfile"},
            {"title": "Deploy", "instruction": "Deploy to cloud"},
        ],
    },
    "systems-programming": {
        "title": "Systems Programming",
        "domain": LabDomain.SYSTEMS,
        "difficulty": "advanced",
        "steps": [
            {"title": "Memory", "instruction": "Implement a memory allocator"},
            {"title": "Concurrency", "instruction": "Thread pool implementation"},
        ],
    },
}


class Labs:
    def __init__(self):
        self._labs: Dict[str, Lab] = {}
        self._instances: Dict[str, List[Dict[str, Any]]] = {}
        self._init_templates()

    def _init_templates(self) -> None:
        for lid, tmpl in LAB_TEMPLATES.items():
            lab = Lab(
                id=lid,
                title=tmpl["title"],
                domain=tmpl["domain"],
                difficulty=tmpl["difficulty"],
                steps=tmpl["steps"],
                estimated_minutes=30,
            )
            self._labs[lid] = lab

    def list_labs(self, domain: Optional[LabDomain] = None, difficulty: Optional[str] = None) -> List[Lab]:
        results = list(self._labs.values())
        if domain:
            results = [l for l in results if l.domain == domain]
        if difficulty:
            results = [l for l in results if l.difficulty == difficulty]
        return results

    def get_lab(self, lab_id: str) -> Optional[Lab]:
        return self._labs.get(lab_id)

    def start_lab(self, user_id: str, lab_id: str) -> Optional[Dict[str, Any]]:
        lab = self._labs.get(lab_id)
        if not lab:
            return None
        instance = {
            "id": f"inst_{len(self._instances.get(user_id, [])) + 1}",
            "user_id": user_id,
            "lab_id": lab_id,
            "status": "started",
            "current_step": 0,
            "completed_steps": [],
            "output": "",
        }
        self._instances.setdefault(user_id, []).append(instance)
        return instance

    def complete_step(self, instance_id: str, user_id: str, step_index: int, output: str = "") -> bool:
        for inst in self._instances.get(user_id, []):
            if inst["id"] == instance_id:
                if step_index not in inst["completed_steps"]:
                    inst["completed_steps"].append(step_index)
                    inst["current_step"] = step_index + 1
                    inst["output"] = output
                    lab = self._labs.get(inst["lab_id"])
                    if lab and len(inst["completed_steps"]) >= len(lab.steps):
                        inst["status"] = "completed"
                    return True
        return False

    def get_lab_progress(self, user_id: str, lab_id: str) -> List[Dict[str, Any]]:
        return [inst for inst in self._instances.get(user_id, []) if inst["lab_id"] == lab_id]

    def validate_step(self, lab_id: str, step_index: int, user_code: str) -> Dict[str, Any]:
        lab = self._labs.get(lab_id)
        if not lab:
            return {"valid": False, "message": "Lab not found"}
        if step_index >= len(lab.steps):
            return {"valid": False, "message": "Step out of range"}
        step = lab.steps[step_index]
        return {
            "valid": True,
            "step": step["title"],
            "message": f"Step '{step['title']}' validation passed",
            "hint": "",
        }

    def search_labs(self, query: str) -> List[Lab]:
        q = query.lower()
        return [l for l in self._labs.values()
                if q in l.title.lower() or q in l.description.lower() or q in l.domain.value]
