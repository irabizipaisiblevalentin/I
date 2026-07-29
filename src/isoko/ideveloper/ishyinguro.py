"""I Developer Platform — I Foundation (Ishyinguro)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import FoundationMember


FOUNDATION_CHARTER = {
    "name": "I Foundation",
    "mission": "Govern the I Programming Language independently for the long term, "
               "fostering education, research, community, and innovation across the global ecosystem.",
    "values": ["Openness", "Inclusivity", "Excellence", "Sustainability", "Community-driven"],
    "established": "2026",
}


class Foundation:
    def __init__(self):
        self._members: Dict[str, FoundationMember] = {}
        self._board: List[str] = []
        self._charter = dict(FOUNDATION_CHARTER)
        self._transparency_reports: List[Dict[str, Any]] = []
        self._policies: Dict[str, str] = {}
        self._init_default_members()

    def _init_default_members(self) -> None:
        self.add_member(FoundationMember(
            id="founder", name="I Language Creator", role="founder",
            contributions=["Language design", "Core compiler"],
        ))

    def get_charter(self) -> Dict[str, Any]:
        return dict(self._charter)

    def add_member(self, member: FoundationMember) -> str:
        if not member.id:
            member.id = f"member_{len(self._members) + 1}"
        self._members[member.id] = member
        return member.id

    def get_member(self, member_id: str) -> Optional[FoundationMember]:
        return self._members.get(member_id)

    def list_members(self, role: Optional[str] = None) -> List[FoundationMember]:
        if role:
            return [m for m in self._members.values() if m.role == role]
        return list(self._members.values())

    def appoint_board_member(self, member_id: str) -> bool:
        if member_id not in self._members:
            return False
        if member_id not in self._board:
            self._board.append(member_id)
            self._members[member_id].role = "board"
        return True

    def remove_board_member(self, member_id: str) -> bool:
        if member_id in self._board:
            self._board.remove(member_id)
            return True
        return False

    def get_board(self) -> List[FoundationMember]:
        return [self._members[mid] for mid in self._board if mid in self._members]

    def set_policy(self, name: str, content: str) -> None:
        self._policies[name] = content

    def get_policy(self, name: str) -> Optional[str]:
        return self._policies.get(name)

    def list_policies(self) -> Dict[str, str]:
        return dict(self._policies)

    def add_transparency_report(self, year: int, content: str) -> Dict[str, Any]:
        report = {
            "id": f"report_{year}",
            "year": year,
            "content": content,
            "published_at": "",
        }
        self._transparency_reports.append(report)
        return report

    def get_transparency_reports(self) -> List[Dict[str, Any]]:
        return list(self._transparency_reports)

    def submit_board_proposal(self, title: str, description: str, proposer_id: str) -> Dict[str, Any]:
        return {
            "id": f"prop_{len(self._transparency_reports) + 1}",
            "title": title,
            "description": description,
            "proposer_id": proposer_id,
            "status": "draft",
            "votes_for": 0,
            "votes_against": 0,
        }

    def get_trademark_policy(self) -> Dict[str, str]:
        return {
            "policy": "The 'I' name and logo are trademarks of the I Foundation. "
                      "Use is permitted for community and educational purposes.",
            "license": "Trademark guidelines v1.0",
        }

    def get_governance_model(self) -> Dict[str, Any]:
        return {
            "structure": "Non-profit foundation with elected board",
            "board_size": "5-11 members",
            "term_length": "2 years",
            "decision_process": "Consensus-seeking with majority vote",
            "committees": ["Technical", "Community", "Education", "Finance"],
        }
