"""I Developer Platform — I Global Conference (Inama)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import Conference, ConferenceSessionType


class GlobalConference:
    def __init__(self):
        self._conferences: Dict[str, Conference] = {}
        self._cfp_submissions: List[Dict[str, Any]] = []

    def create_conference(self, conference: Conference) -> str:
        if not conference.id:
            conference.id = f"conf_{len(self._conferences) + 1}"
        self._conferences[conference.id] = conference
        return conference.id

    def get_conference(self, conference_id: str) -> Optional[Conference]:
        return self._conferences.get(conference_id)

    def list_conferences(self, year: Optional[int] = None) -> List[Conference]:
        if year:
            return [c for c in self._conferences.values() if c.year == year]
        return list(self._conferences.values())

    def add_session(self, conference_id: str, title: str, speaker_id: str, session_type: ConferenceSessionType,
                    duration_minutes: int = 30, description: str = "") -> bool:
        conf = self._conferences.get(conference_id)
        if not conf:
            return False
        session = {
            "id": f"session_{len(conf.sessions) + 1}",
            "title": title,
            "speaker_id": speaker_id,
            "type": session_type.value,
            "duration_minutes": duration_minutes,
            "description": description,
            "status": "scheduled",
        }
        conf.sessions.append(session)
        return True

    def get_sessions(self, conference_id: str, session_type: Optional[ConferenceSessionType] = None) -> List[Dict[str, Any]]:
        conf = self._conferences.get(conference_id)
        if not conf:
            return []
        if session_type:
            return [s for s in conf.sessions if s["type"] == session_type.value]
        return list(conf.sessions)

    def add_speaker(self, conference_id: str, name: str, bio: str, photo_url: str = "",
                    social_links: Optional[Dict[str, str]] = None) -> bool:
        conf = self._conferences.get(conference_id)
        if not conf:
            return False
        speaker = {
            "id": f"speaker_{len(conf.speakers) + 1}",
            "name": name,
            "bio": bio,
            "photo_url": photo_url,
            "social_links": social_links or {},
        }
        conf.speakers.append(speaker)
        return True

    def get_speakers(self, conference_id: str) -> List[Dict[str, Any]]:
        conf = self._conferences.get(conference_id)
        return list(conf.speakers) if conf else []

    def add_sponsor(self, conference_id: str, name: str, tier: str, amount: float = 0.0) -> bool:
        conf = self._conferences.get(conference_id)
        if not conf:
            return False
        sponsor = {"id": f"sponsor_{len(conf.sponsors) + 1}", "name": name, "tier": tier, "amount": amount}
        conf.sponsors.append(sponsor)
        return True

    def get_sponsors(self, conference_id: str) -> List[Dict[str, Any]]:
        conf = self._conferences.get(conference_id)
        return list(conf.sponsors) if conf else []

    def open_cfp(self, conference_id: str, deadline: str) -> bool:
        conf = self._conferences.get(conference_id)
        if not conf:
            return False
        conf.cfp_open = True
        return True

    def close_cfp(self, conference_id: str) -> bool:
        conf = self._conferences.get(conference_id)
        if not conf:
            return False
        conf.cfp_open = False
        return True

    def submit_proposal(self, conference_id: str, speaker_name: str, email: str, title: str,
                        abstract: str, session_type: str = "talk") -> Optional[Dict[str, Any]]:
        conf = self._conferences.get(conference_id)
        if not conf or not conf.cfp_open:
            return None
        proposal = {
            "id": f"cfp_{len(self._cfp_submissions) + 1}",
            "conference_id": conference_id,
            "speaker_name": speaker_name,
            "email": email,
            "title": title,
            "abstract": abstract,
            "session_type": session_type,
            "status": "submitted",
        }
        self._cfp_submissions.append(proposal)
        return proposal

    def review_proposal(self, proposal_id: str, decision: str, feedback: str = "") -> bool:
        for p in self._cfp_submissions:
            if p["id"] == proposal_id:
                p["status"] = decision
                p["feedback"] = feedback
                return True
        return False

    def get_cfp_submissions(self, conference_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        results = [p for p in self._cfp_submissions if p["conference_id"] == conference_id]
        if status:
            results = [p for p in results if p["status"] == status]
        return results

    def get_conference_schedule(self, conference_id: str) -> Dict[str, Any]:
        conf = self._conferences.get(conference_id)
        if not conf:
            return {"error": "Conference not found"}
        return {
            "conference": conf.name,
            "year": conf.year,
            "location": conf.location,
            "dates": f"{conf.start_date} - {conf.end_date}",
            "sessions": len(conf.sessions),
            "speakers": len(conf.speakers),
            "sponsors": len(conf.sponsors),
        }
