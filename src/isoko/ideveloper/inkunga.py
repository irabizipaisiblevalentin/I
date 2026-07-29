"""I Developer Platform — I Scholarships (Inkunga)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import Scholarship, ScholarshipStatus


class Scholarships:
    def __init__(self):
        self._scholarships: Dict[str, Scholarship] = {}
        self._reviews: Dict[str, List[Dict[str, Any]]] = {}
        self._disbursements: List[Dict[str, Any]] = []

    def create_scholarship(self, scholarship: Scholarship) -> str:
        if not scholarship.id:
            scholarship.id = f"scho_{len(self._scholarships) + 1}"
        self._scholarships[scholarship.id] = scholarship
        return scholarship.id

    def get_scholarship(self, scholarship_id: str) -> Optional[Scholarship]:
        return self._scholarships.get(scholarship_id)

    def list_scholarships(self, status: Optional[ScholarshipStatus] = None) -> List[Scholarship]:
        if status:
            return [s for s in self._scholarships.values() if s.status == status]
        return list(self._scholarships.values())

    def search_scholarships(self, query: str) -> List[Scholarship]:
        q = query.lower()
        return [s for s in self._scholarships.values()
                if q in s.title.lower() or q in s.description.lower()]

    def apply(self, scholarship_id: str, applicant_id: str, proposal: str, documents: Optional[List[str]] = None) -> bool:
        scholarship = self._scholarships.get(scholarship_id)
        if not scholarship or scholarship.status != ScholarshipStatus.OPEN:
            return False
        application = {
            "id": f"app_{len(scholarship.applications) + 1}",
            "applicant_id": applicant_id,
            "proposal": proposal,
            "documents": documents or [],
            "status": "submitted",
            "submitted_at": "",
            "score": None,
        }
        scholarship.applications.append(application)
        return True

    def review_application(self, scholarship_id: str, application_id: str, reviewer_id: str, score: int, notes: str) -> bool:
        scholarship = self._scholarships.get(scholarship_id)
        if not scholarship:
            return False
        for app in scholarship.applications:
            if app["id"] == application_id:
                app["score"] = score
                review = {
                    "reviewer_id": reviewer_id,
                    "application_id": application_id,
                    "score": score,
                    "notes": notes,
                    "reviewed_at": "",
                }
                self._reviews.setdefault(scholarship_id, []).append(review)
                return True
        return False

    def award_scholarship(self, scholarship_id: str, application_id: str) -> bool:
        scholarship = self._scholarships.get(scholarship_id)
        if not scholarship:
            return False
        for app in scholarship.applications:
            if app["id"] == application_id:
                app["status"] = "awarded"
                scholarship.status = ScholarshipStatus.AWARDED
                self._disbursements.append({
                    "scholarship_id": scholarship_id,
                    "application_id": application_id,
                    "applicant_id": app["applicant_id"],
                    "amount": scholarship.amount_usd,
                    "status": "pending",
                })
                return True
        return False

    def get_applications(self, scholarship_id: str) -> List[Dict[str, Any]]:
        scholarship = self._scholarships.get(scholarship_id)
        if not scholarship:
            return []
        return list(scholarship.applications)

    def get_disbursements(self) -> List[Dict[str, Any]]:
        return list(self._disbursements)

    def mark_disbursed(self, scholarship_id: str, application_id: str) -> bool:
        for d in self._disbursements:
            if d["scholarship_id"] == scholarship_id and d["application_id"] == application_id:
                d["status"] = "disbursed"
                return True
        return False

    def get_reviews(self, scholarship_id: str) -> List[Dict[str, Any]]:
        return self._reviews.get(scholarship_id, [])

    def get_applicant_dashboard(self, applicant_id: str) -> Dict[str, Any]:
        applications = []
        awarded = []
        for s in self._scholarships.values():
            for app in s.applications:
                if app["applicant_id"] == applicant_id:
                    entry = {"scholarship_title": s.title, "status": app["status"], "score": app.get("score")}
                    applications.append(entry)
                    if app["status"] == "awarded":
                        awarded.append(entry)
        return {
            "applicant_id": applicant_id,
            "total_applications": len(applications),
            "awarded": len(awarded),
            "applications": applications,
        }
