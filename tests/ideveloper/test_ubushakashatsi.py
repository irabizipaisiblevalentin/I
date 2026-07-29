"""Tests for isoko.ideveloper.ubushakashatsi — Research Platform."""

from __future__ import annotations

from isoko.ideveloper.ubushakashatsi import ResearchPlatform
from isoko.ideveloper.ibikoreshingiro import ResearchPaper


def test_research_init():
    rp = ResearchPlatform()
    assert rp.search_papers("") == []


def test_submit_paper():
    rp = ResearchPlatform()
    paper = ResearchPaper(title="I Compiler", authors=["Alice"], abstract="Novel compiler design")
    pid = rp.submit_paper(paper)
    assert rp.get_paper(pid) is not None


def test_search_papers():
    rp = ResearchPlatform()
    rp.submit_paper(ResearchPaper(title="Compiler Optimisation", authors=["A"], category="compilers"))
    rp.submit_paper(ResearchPaper(title="AI Models", authors=["B"], category="ai"))
    results = rp.search_papers("compiler")
    assert len(results) == 1


def test_search_by_category():
    rp = ResearchPlatform()
    rp.submit_paper(ResearchPaper(title="Kernel Design", authors=["C"], category="systems"))
    rp.submit_paper(ResearchPaper(title="Cloud Architecture", authors=["D"], category="systems"))
    results = rp.search_papers("", category="systems")
    assert len(results) == 2


def test_benchmarks():
    rp = ResearchPlatform()
    rp.add_benchmark("Compilation Speed", "performance", {"i": 100, "rust": 80})
    assert len(rp.get_benchmarks("performance")) == 1


def test_compiler_research():
    rp = ResearchPlatform()
    research = rp.get_compiler_research()
    assert "optimisation" in research["areas"]


def test_ai_research():
    rp = ResearchPlatform()
    research = rp.get_ai_research()
    assert "Ubwenge ML Framework" in [p["name"] for p in research["projects"]]


def test_systems_research():
    rp = ResearchPlatform()
    research = rp.get_systems_research()
    assert "distributed systems" in research["areas"]


def test_university_partnerships():
    rp = ResearchPlatform()
    rp.add_university_partnership("MIT", ["compilers", "AI"])
    assert len(rp.get_partnerships()) == 1


def test_grant_proposal():
    rp = ResearchPlatform()
    grant = rp.submit_grant_proposal("Research Grant", "researcher1", 50000.0, "Study")
    assert grant["status"] == "submitted"


def test_performance_reports():
    rp = ResearchPlatform()
    reports = rp.get_performance_reports()
    assert len(reports) >= 3
