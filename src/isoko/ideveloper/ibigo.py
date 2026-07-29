"""I Developer Platform — Enterprise Services (Ibigo)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import EnterprisePlan, SupportPriority, SupportTicket


ENTERPRISE_PLANS = [
    EnterprisePlan(
        id="starter", name="Starter", description="For small teams getting started with I",
        price_monthly=0, max_users=5, max_projects=10, support_level=SupportPriority.NORMAL,
        features=["Public packages", "Community support", "Basic documentation"],
    ),
    EnterprisePlan(
        id="team", name="Team", description="For growing development teams",
        price_monthly=99, max_users=25, max_projects=50, support_level=SupportPriority.NORMAL,
        features=["Private packages", "Email support", "Team management", "Audit logging"],
        private_registry=True, audit_logging=True,
    ),
    EnterprisePlan(
        id="business", name="Business", description="For organisations at scale",
        price_monthly=499, max_users=100, max_projects=200, support_level=SupportPriority.HIGH,
        features=["Enterprise registry", "Priority support", "SSO", "Custom SLAs", "Training sessions"],
        private_registry=True, audit_logging=True, sso=True, sla_hours=4,
    ),
    EnterprisePlan(
        id="enterprise", name="Enterprise", description="For large enterprises with custom needs",
        price_monthly=0, max_users=0, max_projects=0, support_level=SupportPriority.CRITICAL,
        features=["Dedicated support", "Custom integrations", "On-premise option", "SLA guarantee",
                   "Dedicated account manager", "Compliance reporting", "Custom training"],
        private_registry=True, audit_logging=True, sso=True, sla_hours=1,
    ),
]


class EnterprisePlatform:
    def __init__(self):
        self._plans: Dict[str, EnterprisePlan] = {p.id: p for p in ENTERPRISE_PLANS}
        self._subscriptions: Dict[str, str] = {}
        self._tickets: Dict[str, SupportTicket] = {}
        self._training: List[Dict[str, Any]] = []
        self._consulting: List[Dict[str, Any]] = []
        self._security_advisories: List[Dict[str, Any]] = []

    def get_plans(self) -> List[EnterprisePlan]:
        return list(self._plans.values())

    def get_plan(self, plan_id: str) -> Optional[EnterprisePlan]:
        return self._plans.get(plan_id)

    def subscribe(self, organisation_id: str, plan_id: str) -> bool:
        if plan_id not in self._plans:
            return False
        self._subscriptions[organisation_id] = plan_id
        return True

    def get_subscription(self, organisation_id: str) -> Optional[EnterprisePlan]:
        plan_id = self._subscriptions.get(organisation_id)
        return self._plans.get(plan_id) if plan_id else None

    def create_ticket(self, ticket: SupportTicket) -> str:
        if not ticket.id:
            ticket.id = f"ticket_{len(self._tickets) + 1}"
        self._tickets[ticket.id] = ticket
        return ticket.id

    def get_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        return self._tickets.get(ticket_id)

    def update_ticket_status(self, ticket_id: str, status: str, resolution: str = "") -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return False
        ticket.status = status
        if resolution:
            ticket.resolution = resolution
        return True

    def get_tickets(self, organisation_id: str) -> List[SupportTicket]:
        return [t for t in self._tickets.values() if t.user_id == organisation_id]

    def add_training(self, title: str, description: str, duration_days: int, price_usd: float) -> Dict[str, Any]:
        training = {"id": f"training_{len(self._training) + 1}", "title": title, "description": description, "duration_days": duration_days, "price_usd": price_usd}
        self._training.append(training)
        return training

    def add_consulting(self, title: str, description: str, rate_usd: float) -> Dict[str, Any]:
        service = {"id": f"consult_{len(self._consulting) + 1}", "title": title, "description": description, "rate_usd": rate_usd}
        self._consulting.append(service)
        return service

    def add_security_advisory(self, advisory_id: str, title: str, severity: str, description: str) -> Dict[str, Any]:
        advisory = {"id": advisory_id, "title": title, "severity": severity, "description": description, "published_at": "", "affected_versions": []}
        self._security_advisories.append(advisory)
        return advisory

    def get_security_advisories(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        if severity:
            return [a for a in self._security_advisories if a["severity"] == severity]
        return list(self._security_advisories)

    def get_compliance_resources(self) -> Dict[str, List[str]]:
        return {
            "GDPR": ["Data processing agreement", "Privacy policy template"],
            "SOC2": ["Audit report", "Security overview"],
            "ISO27001": ["Certificate", "Scope document"],
            "HIPAA": ["BA agreement", "Security controls"],
        }

    def get_migration_assistance(self) -> Dict[str, Any]:
        return {
            "from_python": {"guide": "Python to I migration guide", "tools": ["i-py-transpiler"]},
            "from_javascript": {"guide": "JS to I migration guide", "tools": ["i-js-transpiler"]},
            "from_rust": {"guide": "Rust to I migration guide", "tools": ["i-rust-bridge"]},
        }
