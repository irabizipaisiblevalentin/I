"""Security — prompt injection, content safety, bias monitoring, model verification, audit logs, policy enforcement."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    CONTENT_VIOLATION = "content_violation"
    BIAS_DETECTED = "bias_detected"
    DATA_LEAK = "data_leak"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MODEL_TAMPERING = "model_tampering"
    RATE_LIMIT = "rate_limit"
    POLICY_VIOLATION = "policy_violation"
    AUDIT_LOG = "audit_log"


@dataclass
class SecurityEvent:
    event_type: SecurityEventType = SecurityEventType.AUDIT_LOG
    severity: Severity = Severity.LOW
    message: str = ""
    source: str = ""
    user: str = ""
    model_id: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    event_id: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.event_id:
            import uuid
            self.event_id = f"sec_{uuid.uuid4().hex[:12]}"


class InjectionDetector:
    PATTERNS = [
        (r"ignore\s+(all\s+)?(previous|above|below)\s+instructions", "Ignore instruction override", Severity.HIGH),
        (r"forget\s+(everything|all)\s+(previous|prior)", "Forget instruction", Severity.HIGH),
        (r"you\s+are\s+(not\s+)?(required|obligated|bound)\s+to", "Role escape", Severity.HIGH),
        (r"system\s*(prompt|message|instruction)\s*:", "System prompt injection", Severity.CRITICAL),
        (r"(sudo|su\s+-|chmod|chown|rm\s+-rf\s+/|dd\s+if=)", "Shell command", Severity.CRITICAL),
        (r"<\s*(script|iframe|object|embed|form)", "HTML injection", Severity.HIGH),
        (r"!important|!critical|!urgent", "Urgency manipulation", Severity.MEDIUM),
        (r"(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\s+.*\s+(FROM|INTO|TABLE)", "SQL injection", Severity.CRITICAL),
        (r"(http|https):\/\/(evil|malicious|malware|phishing|attack)", "Malicious URL", Severity.HIGH),
        (r"base64\s*,\s*[A-Za-z0-9+/]{50,}={0,2}", "Encoded payload", Severity.MEDIUM),
        (r"bypass\s+(restrictions|filters|safety|security)", "Bypass attempt", Severity.HIGH),
        (r"role\s*:\s*system\s*(below|above)", "Role hijack", Severity.CRITICAL),
    ]

    def analyze(self, text: str) -> Tuple[bool, List[Dict[str, Any]]]:
        findings = []
        for pattern, desc, severity in self.PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                findings.append({
                    "pattern": pattern,
                    "description": desc,
                    "severity": severity.value,
                    "matched": self._extract_match(text, pattern),
                })
        return len(findings) > 0, findings

    def _extract_match(self, text: str, pattern: str) -> str:
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return m.group(0) if m else ""


class ContentSafetyChecker:
    CATEGORIES = {
        "hate_speech": [r"\b(hate|racist|nazi|white.supermac)", re.IGNORECASE],
        "violence": [r"\b(kill|murder|torture|bomb|attack|weapon)", re.IGNORECASE],
        "sexual": [r"\b(porn|explicit|nsfw|sexual\s+content)", re.IGNORECASE],
        "harassment": [r"\b(bully|harass|threaten|stalk)", re.IGNORECASE],
        "self_harm": [r"\b(suicide|self.harm|cutting)", re.IGNORECASE],
        "personal_info": [r"\b(\d{3}-\d{2}-\d{4}|\d{16}|\S+@\S+\.\S+)", re.IGNORECASE],
    }

    def check(self, text: str) -> Dict[str, Any]:
        violations = {}
        for category, (pattern, flags) in self.CATEGORIES.items():
            matches = re.findall(pattern, text, flags)
            if matches:
                violations[category] = matches[:5]
        return {
            "safe": len(violations) == 0,
            "violations": violations,
            "categories_flagged": list(violations.keys()),
        }


class BiasMonitor:
    BIAS_TYPES = [
        "gender", "race", "age", "religion", "nationality",
        "disability", "socioeconomic", "political",
    ]

    def analyze(self, text: str) -> Dict[str, Any]:
        biases = {}
        if re.search(r"\b(men|women|boys|girls)\b", text, re.IGNORECASE) and \
           re.search(r"\b(all|always|never|every)\b", text, re.IGNORECASE):
            biases["gender"] = Severity.MEDIUM.value
        if re.search(r"\b(white|black|asian|hispanic)\b", text, re.IGNORECASE) and \
           re.search(r"\b(better|worse|smarter|lazier)\b", text, re.IGNORECASE):
            biases["race"] = Severity.HIGH.value
        return {
            "has_bias": len(biases) > 0,
            "biases": biases,
            "bias_score": min(len(biases) / len(self.BIAS_TYPES), 1.0),
        }


class PolicyEnforcer:
    def __init__(self):
        self.policies: Dict[str, Dict[str, Any]] = {}

    def add_policy(self, name: str, rules: Dict[str, Any]) -> None:
        self.policies[name] = rules

    def check(self, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        for pname, rules in self.policies.items():
            denied_actions = rules.get("deny_actions", [])
            if action in denied_actions:
                return False, f"Policy '{pname}' denies action '{action}'"
            required_roles = rules.get("required_roles", [])
            user_role = context.get("role", "")
            if required_roles and user_role not in required_roles:
                return False, f"Policy '{pname}' requires role in {required_roles}"
        return True, ""


class AuditLogger:
    def __init__(self, log_path: str = "./logs/audit.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._events: List[SecurityEvent] = []

    def log(self, event: SecurityEvent) -> None:
        self._events.append(event)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "message": event.message,
                "source": event.source,
                "user": event.user,
                "model_id": event.model_id,
                "timestamp": event.timestamp,
            }) + "\n")

    def query(self, event_type: Optional[SecurityEventType] = None,
              severity: Optional[Severity] = None,
              limit: int = 100) -> List[SecurityEvent]:
        results = []
        for e in reversed(self._events):
            if event_type and e.event_type != event_type:
                continue
            if severity and e.severity != severity:
                continue
            results.append(e)
            if len(results) >= limit:
                break
        return results


_security_manager = None


class SecurityManager:
    def __init__(self):
        self.injection_detector = InjectionDetector()
        self.content_safety = ContentSafetyChecker()
        self.bias_monitor = BiasMonitor()
        self.policy_enforcer = PolicyEnforcer()
        self.audit_logger = AuditLogger()

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        injected, findings = self.injection_detector.analyze(prompt)
        safety = self.content_safety.check(prompt)
        bias = self.bias_monitor.analyze(prompt)

        if injected or not safety["safe"] or bias["has_bias"]:
            self.audit_logger.log(SecurityEvent(
                event_type=SecurityEventType.CONTENT_VIOLATION if not safety["safe"]
                else SecurityEventType.PROMPT_INJECTION if injected
                else SecurityEventType.BIAS_DETECTED,
                severity=Severity.HIGH if injected or not safety["safe"] else Severity.MEDIUM,
                message="Content policy violation detected",
                details={"injection": findings, "safety": safety, "bias": bias},
            ))

        return {
            "safe": not injected and safety["safe"] and not bias["has_bias"],
            "injection_detected": injected,
            "injection_findings": findings,
            "content_safe": safety["safe"],
            "content_violations": safety["violations"],
            "bias_detected": bias["has_bias"],
            "bias_details": bias["biases"],
        }

    def log_event(self, event: SecurityEvent) -> None:
        self.audit_logger.log(event)


def get_security() -> SecurityManager:
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager
