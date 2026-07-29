"""I Developer Platform — Research Platform (Ubushakashatsi)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import ResearchPaper


class ResearchPlatform:
    def __init__(self):
        self._papers: Dict[str, ResearchPaper] = {}
        self._benchmarks: List[Dict[str, Any]] = []
        self._partnerships: List[Dict[str, Any]] = []
        self._grants: List[Dict[str, Any]] = []
        self._research_groups: List[Dict[str, Any]] = []

    def submit_paper(self, paper: ResearchPaper) -> str:
        if not paper.id:
            paper.id = f"paper_{len(self._papers) + 1}"
        self._papers[paper.id] = paper
        return paper.id

    def get_paper(self, paper_id: str) -> Optional[ResearchPaper]:
        return self._papers.get(paper_id)

    def search_papers(self, query: str, category: Optional[str] = None) -> List[ResearchPaper]:
        q = query.lower()
        results = []
        for paper in self._papers.values():
            if category and paper.category != category:
                continue
            if q in paper.title.lower() or q in paper.abstract.lower() or any(q in kw.lower() for kw in paper.keywords):
                results.append(paper)
        return results

    def add_benchmark(self, name: str, category: str, results: Dict[str, float]) -> Dict[str, Any]:
        benchmark = {
            "id": f"bench_{len(self._benchmarks) + 1}",
            "name": name,
            "category": category,
            "results": results,
            "submitted_at": "",
        }
        self._benchmarks.append(benchmark)
        return benchmark

    def get_benchmarks(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        if category:
            return [b for b in self._benchmarks if b["category"] == category]
        return list(self._benchmarks)

    def get_compiler_research(self) -> Dict[str, Any]:
        return {
            "areas": ["optimisation", "type inference", "code generation", "parallelisation"],
            "projects": [
                {"name": "I JIT Compiler", "status": "active", "description": "Just-in-time compilation for I"},
                {"name": "I AOT Compiler", "status": "active", "description": "Ahead-of-time native compilation"},
            ],
        }

    def get_ai_research(self) -> Dict[str, Any]:
        return {
            "areas": ["model optimisation", "automated ML", "AI safety", "explainable AI"],
            "projects": [
                {"name": "Ubwenge ML Framework", "status": "active", "description": "Native ML framework for I"},
            ],
        }

    def get_systems_research(self) -> Dict[str, Any]:
        return {
            "areas": ["distributed systems", "operating systems", "networking", "security"],
            "projects": [
                {"name": "I OS Kernel", "status": "research", "description": "Research OS written in I"},
            ],
        }

    def add_university_partnership(self, university_name: str, focus_areas: List[str]) -> Dict[str, Any]:
        partnership = {
            "id": f"partner_{len(self._partnerships) + 1}",
            "university": university_name,
            "focus_areas": focus_areas,
            "established_at": "",
        }
        self._partnerships.append(partnership)
        return partnership

    def get_partnerships(self) -> List[Dict[str, Any]]:
        return list(self._partnerships)

    def submit_grant_proposal(self, title: str, researcher_id: str, amount: float, description: str) -> Dict[str, Any]:
        grant = {
            "id": f"grant_{len(self._grants) + 1}",
            "title": title,
            "researcher_id": researcher_id,
            "amount": amount,
            "description": description,
            "status": "submitted",
        }
        self._grants.append(grant)
        return grant

    def get_performance_reports(self) -> List[Dict[str, Any]]:
        return [
            {"category": "compilation", "metric": "lines_per_second", "value": 50000},
            {"category": "runtime", "metric": "operations_per_second", "value": 1000000},
            {"category": "memory", "metric": "heap_allocation_rate", "value": "10MB/s"},
        ]

    # ── I Research: Academic Collaboration ─────────────────────────────

    def create_research_group(self, name: str, lead_id: str, focus: str) -> Dict[str, Any]:
        group = {
            "id": f"rgroup_{len(self._research_groups) + 1}",
            "name": name,
            "lead_id": lead_id,
            "focus": focus,
            "members": [lead_id],
            "papers": [],
            "created_at": "",
        }
        self._research_groups.append(group)
        return group

    def get_research_groups(self, focus: Optional[str] = None) -> List[Dict[str, Any]]:
        if focus:
            return [g for g in self._research_groups if focus.lower() in g["focus"].lower()]
        return list(self._research_groups)

    def join_research_group(self, group_id: str, researcher_id: str) -> bool:
        for g in self._research_groups:
            if g["id"] == group_id and researcher_id not in g["members"]:
                g["members"].append(researcher_id)
                return True
        return False

    def submit_joint_paper(self, group_id: str, title: str, authors: List[str], abstract: str) -> Optional[Dict[str, Any]]:
        for g in self._research_groups:
            if g["id"] == group_id:
                paper = ResearchPaper(title=title, authors=authors, abstract=abstract, category="collaborative")
                pid = self.submit_paper(paper)
                g["papers"].append(pid)
                return {"paper_id": pid, "title": title}
        return None

    def get_collaboration_network(self, researcher_id: str) -> Dict[str, Any]:
        groups = [g for g in self._research_groups if researcher_id in g["members"]]
        collaborators = set()
        for g in groups:
            collaborators.update(g["members"])
        collaborators.discard(researcher_id)
        return {
            "researcher_id": researcher_id,
            "groups": len(groups),
            "collaborators": list(collaborators),
            "joint_papers": sum(len(g["papers"]) for g in groups),
        }
