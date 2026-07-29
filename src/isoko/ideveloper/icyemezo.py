"""I Developer Platform — Certification Programme (Icyemezo)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import Certification, CertificationExam, CertificationLevel


CERTIFICATION_DEFS: Dict[str, Dict[str, Any]] = {
    "i-certified-developer": {
        "title": "I Certified Developer",
        "description": "Core proficiency in the I Programming Language",
        "level": CertificationLevel.ASSOCIATE,
        "duration": 60,
        "passing_score": 70,
        "skills": ["syntax", "types", "functions", "control flow", "data structures"],
    },
    "i-certified-web-developer": {
        "title": "I Certified Web Developer",
        "description": "Build web applications with the I ecosystem",
        "level": CertificationLevel.PROFESSIONAL,
        "duration": 90,
        "passing_score": 75,
        "skills": ["web frameworks", "routing", "templating", "APIs", "databases"],
    },
    "i-certified-ai-engineer": {
        "title": "I Certified AI Engineer",
        "description": "Machine learning and AI development with I",
        "level": CertificationLevel.PROFESSIONAL,
        "duration": 120,
        "passing_score": 80,
        "skills": ["ML pipelines", "neural networks", "data processing", "model deployment"],
    },
    "i-certified-systems-engineer": {
        "title": "I Certified Systems Engineer",
        "description": "Systems programming and OS development",
        "level": CertificationLevel.EXPERT,
        "duration": 120,
        "passing_score": 80,
        "skills": ["memory management", "concurrency", "drivers", "kernel"],
    },
    "i-certified-cloud-engineer": {
        "title": "I Certified Cloud Engineer",
        "description": "Cloud-native development with I",
        "level": CertificationLevel.PROFESSIONAL,
        "duration": 90,
        "passing_score": 75,
        "skills": ["microservices", "containers", "serverless", "cloud APIs"],
    },
    "i-certified-game-developer": {
        "title": "I Certified Game Developer",
        "description": "Game development with the Imikino engine",
        "level": CertificationLevel.PROFESSIONAL,
        "duration": 90,
        "passing_score": 75,
        "skills": ["game loop", "physics", "rendering", "asset management"],
    },
    "i-certified-instructor": {
        "title": "I Certified Instructor",
        "description": "Teach the I Programming Language effectively",
        "level": CertificationLevel.INSTRUCTOR,
        "duration": 60,
        "passing_score": 85,
        "skills": ["pedagogy", "curriculum design", "assessment", "mentoring"],
    },
    "i-certified-architect": {
        "title": "I Certified Architect",
        "description": "Design large-scale systems with I",
        "level": CertificationLevel.ARCHITECT,
        "duration": 150,
        "passing_score": 85,
        "skills": ["system design", "architecture patterns", "scalability", "security"],
    },
}


class CertificationProgramme:
    def __init__(self):
        self._certifications: Dict[str, Certification] = {}
        self._exams: Dict[str, CertificationExam] = {}
        self._issued: Dict[str, List[Dict[str, Any]]] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        for cid, cfg in CERTIFICATION_DEFS.items():
            level = cfg["level"]
            exam = CertificationExam(
                id=f"exam_{cid}",
                title=f"{cfg['title']} Exam",
                description=cfg["description"],
                level=level,
                duration_minutes=cfg["duration"],
                passing_score=cfg["passing_score"],
                questions=self._generate_questions(cfg["skills"]),
            )
            cert = Certification(
                id=cid,
                title=cfg["title"],
                description=cfg["description"],
                level=level,
                exam=exam,
                skills=cfg["skills"],
            )
            self._certifications[cid] = cert
            self._exams[exam.id] = exam

    def _generate_questions(self, skills: List[str]) -> List[Dict[str, Any]]:
        return [
            {"id": f"q_{i}", "skill": skill, "question": f"Sample question for {skill}", "options": ["A", "B", "C", "D"], "answer": "A"}
            for i, skill in enumerate(skills)
        ]

    def list_certifications(self) -> List[Certification]:
        return list(self._certifications.values())

    def get_certification(self, cert_id: str) -> Optional[Certification]:
        return self._certifications.get(cert_id)

    def get_exam(self, exam_id: str) -> Optional[CertificationExam]:
        return self._exams.get(exam_id)

    def take_exam(self, user_id: str, exam_id: str, answers: Dict[str, str]) -> Dict[str, Any]:
        exam = self._exams.get(exam_id)
        if not exam:
            return {"error": "Exam not found", "passed": False}
        correct = sum(1 for q in exam.questions if answers.get(q["id"]) == q["answer"])
        total = len(exam.questions)
        score = int((correct / total) * 100) if total > 0 else 0
        passed = score >= exam.passing_score
        result = {
            "user_id": user_id,
            "exam_id": exam_id,
            "score": score,
            "correct": correct,
            "total": total,
            "passed": passed,
            "certification_id": "",
        }
        if passed:
            for cid, cert in self._certifications.items():
                if cert.exam and cert.exam.id == exam_id:
                    result["certification_id"] = cid
                    self.issue_certificate(user_id, cid)
                    break
        return result

    def issue_certificate(self, user_id: str, cert_id: str) -> Optional[Dict[str, Any]]:
        cert = self._certifications.get(cert_id)
        if not cert:
            return None
        issued = {
            "user_id": user_id,
            "certification_id": cert_id,
            "title": cert.title,
            "issued_at": "",
            "valid_until": "",
            "badge_url": cert.badge_url,
        }
        self._issued.setdefault(user_id, []).append(issued)
        return issued

    def get_user_certifications(self, user_id: str) -> List[Dict[str, Any]]:
        return self._issued.get(user_id, [])

    def verify_certificate(self, user_id: str, cert_id: str) -> bool:
        return any(
            c["certification_id"] == cert_id
            for c in self._issued.get(user_id, [])
        )
