"""I Developer Platform — Open Source / Project Hosting (Isoko)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class OpenSourcePlatform:
    def __init__(self):
        self._projects: Dict[str, Dict[str, Any]] = {}
        self._issues: Dict[str, List[Dict[str, Any]]] = {}
        self._reviews: Dict[str, List[Dict[str, Any]]] = {}
        self._templates: List[Dict[str, Any]] = []
        self._contributor_dashboards: Dict[str, Dict[str, Any]] = {}
        self._funding: List[Dict[str, Any]] = []

    def create_project(self, name: str, owner_id: str, description: str = "", visibility: str = "public") -> Dict[str, Any]:
        project = {
            "id": f"proj_{len(self._projects) + 1}",
            "name": name,
            "owner_id": owner_id,
            "description": description,
            "visibility": visibility,
            "stars": 0,
            "forks": 0,
            "created_at": "",
            "language": "i",
            "topics": [],
            "license": "MIT",
        }
        self._projects[project["id"]] = project
        return project

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        return self._projects.get(project_id)

    def search_projects(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        return [p for p in self._projects.values() if q in p["name"].lower() or q in p["description"].lower()]

    def create_issue(self, project_id: str, title: str, description: str, author_id: str) -> Optional[Dict[str, Any]]:
        if project_id not in self._projects:
            return None
        issue = {
            "id": f"issue_{len(self._issues.get(project_id, [])) + 1}",
            "project_id": project_id,
            "title": title,
            "description": description,
            "author_id": author_id,
            "status": "open",
            "labels": [],
            "comments": [],
            "created_at": "",
        }
        self._issues.setdefault(project_id, []).append(issue)
        return issue

    def get_issues(self, project_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        issues = self._issues.get(project_id, [])
        if status:
            return [i for i in issues if i["status"] == status]
        return list(issues)

    def create_review(self, project_id: str, title: str, author_id: str, changes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if project_id not in self._projects:
            return None
        review = {
            "id": f"review_{len(self._reviews.get(project_id, [])) + 1}",
            "project_id": project_id,
            "title": title,
            "author_id": author_id,
            "changes": changes,
            "status": "open",
            "comments": [],
            "approvals": 0,
        }
        self._reviews.setdefault(project_id, []).append(review)
        return review

    def approve_review(self, project_id: str, review_id: str, reviewer_id: str) -> bool:
        for review in self._reviews.get(project_id, []):
            if review["id"] == review_id:
                review["approvals"] += 1
                if review["approvals"] >= 2:
                    review["status"] = "approved"
                return True
        return False

    def add_project_template(self, name: str, description: str, files: Dict[str, str]) -> Dict[str, Any]:
        template = {"id": f"template_{len(self._templates) + 1}", "name": name, "description": description, "files": files}
        self._templates.append(template)
        return template

    def get_project_templates(self) -> List[Dict[str, Any]]:
        return list(self._templates)

    def get_contributor_dashboard(self, project_id: str) -> Dict[str, Any]:
        if project_id not in self._contributor_dashboards:
            self._contributor_dashboards[project_id] = {
                "project_id": project_id,
                "total_contributors": 0,
                "total_commits": 0,
                "open_issues": len(self._issues.get(project_id, [])),
                "recent_activity": [],
            }
        return self._contributor_dashboards[project_id]

    def add_funding(self, project_id: str, sponsor_id: str, amount: float, message: str = "") -> Optional[Dict[str, Any]]:
        if project_id not in self._projects:
            return None
        funding = {"id": f"fund_{len(self._funding) + 1}", "project_id": project_id, "sponsor_id": sponsor_id, "amount": amount, "message": message}
        self._funding.append(funding)
        return funding

    def get_community_governance(self, project_id: str) -> Dict[str, Any]:
        return {
            "project_id": project_id,
            "maintainers": [],
            "contributors": [],
            "code_of_conduct": "I Community Code of Conduct",
            "contribution_guide": "See CONTRIBUTING.md",
        }
