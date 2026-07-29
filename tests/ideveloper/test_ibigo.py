"""Tests for isoko.ideveloper.ibigo — Enterprise Services."""

from __future__ import annotations

from isoko.ideveloper.ibigo import EnterprisePlatform
from isoko.ideveloper.ibikoreshingiro import SupportTicket


def test_enterprise_init():
    ep = EnterprisePlatform()
    assert len(ep.get_plans()) == 4


def test_get_plan():
    ep = EnterprisePlatform()
    plan = ep.get_plan("team")
    assert plan is not None
    assert plan.name == "Team"
    assert plan.price_monthly == 99


def test_subscribe():
    ep = EnterprisePlatform()
    assert ep.subscribe("org1", "business") is True
    assert ep.subscribe("org1", "nonexistent") is False
    sub = ep.get_subscription("org1")
    assert sub is not None
    assert sub.name == "Business"


def test_create_ticket():
    ep = EnterprisePlatform()
    ticket = SupportTicket(user_id="org1", subject="Issue", description="Help")
    tid = ep.create_ticket(ticket)
    assert ep.get_ticket(tid) is not None


def test_update_ticket():
    ep = EnterprisePlatform()
    ticket = SupportTicket(user_id="org1", subject="Issue", description="Desc")
    tid = ep.create_ticket(ticket)
    assert ep.update_ticket_status(tid, "resolved", "Fixed") is True
    t = ep.get_ticket(tid)
    assert t is not None
    assert t.status == "resolved"


def test_get_tickets():
    ep = EnterprisePlatform()
    ep.create_ticket(SupportTicket(user_id="org1", subject="S1"))
    ep.create_ticket(SupportTicket(user_id="org2", subject="S2"))
    assert len(ep.get_tickets("org1")) == 1


def test_training():
    ep = EnterprisePlatform()
    t = ep.add_training("I Fundamentals", "Learn I basics", 3, 999.0)
    assert t["duration_days"] == 3


def test_consulting():
    ep = EnterprisePlatform()
    c = ep.add_consulting("Code Review", "Expert code review", 200.0)
    assert c["rate_usd"] == 200.0


def test_security_advisories():
    ep = EnterprisePlatform()
    ep.add_security_advisory("CVE-2026-0001", "Critical vuln", "critical", "Description")
    assert len(ep.get_security_advisories("critical")) == 1


def test_compliance_resources():
    ep = EnterprisePlatform()
    resources = ep.get_compliance_resources()
    assert "GDPR" in resources
    assert "SOC2" in resources


def test_migration_assistance():
    ep = EnterprisePlatform()
    migration = ep.get_migration_assistance()
    assert "from_python" in migration
    assert "from_rust" in migration
