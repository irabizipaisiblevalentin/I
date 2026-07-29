"""I Developer Platform — Community Platform (Umuryango)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import CommunityPost, Discussion, Event, EventType


class CommunityPlatform:
    def __init__(self):
        self._discussions: Dict[str, Discussion] = {}
        self._posts: Dict[str, CommunityPost] = {}
        self._events: Dict[str, Event] = {}
        self._forums: Dict[str, List[str]] = {}
        self._user_groups: Dict[str, Dict[str, Any]] = {}
        self._mentorships: List[Dict[str, str]] = []
        self._rfc_items: List[Dict[str, Any]] = []

    def create_discussion(self, discussion: Discussion) -> str:
        if not discussion.id:
            discussion.id = f"disc_{len(self._discussions) + 1}"
        self._discussions[discussion.id] = discussion
        return discussion.id

    def get_discussion(self, discussion_id: str) -> Optional[Discussion]:
        return self._discussions.get(discussion_id)

    def search_discussions(self, query: str) -> List[Discussion]:
        q = query.lower()
        return [d for d in self._discussions.values() if q in d.title.lower() or q in d.content.lower()]

    def add_reply(self, discussion_id: str, post: CommunityPost) -> bool:
        disc = self._discussions.get(discussion_id)
        if not disc:
            return False
        disc.replies.append(post)
        return True

    def create_event(self, event: Event) -> str:
        if not event.id:
            event.id = f"event_{len(self._events) + 1}"
        self._events[event.id] = event
        return event.id

    def get_event(self, event_id: str) -> Optional[Event]:
        return self._events.get(event_id)

    def list_events(self, event_type: Optional[EventType] = None) -> List[Event]:
        if event_type:
            return [e for e in self._events.values() if e.type == event_type]
        return list(self._events.values())

    def register_for_event(self, event_id: str, user_id: str) -> bool:
        event = self._events.get(event_id)
        if not event:
            return False
        event.attendees_count += 1
        return True

    def create_forum(self, name: str, description: str) -> Dict[str, Any]:
        forum = {"id": f"forum_{len(self._forums) + 1}", "name": name, "description": description, "posts": []}
        self._forums[forum["id"]] = forum
        return forum

    def create_user_group(self, name: str, owner_id: str, description: str = "") -> Dict[str, Any]:
        group = {"id": f"group_{len(self._user_groups) + 1}", "name": name, "owner": owner_id, "description": description, "members": [owner_id]}
        self._user_groups[group["id"]] = group
        return group

    def request_mentorship(self, mentor_id: str, mentee_id: str) -> Dict[str, str]:
        match = {"mentor_id": mentor_id, "mentee_id": mentee_id, "status": "pending"}
        self._mentorships.append(match)
        return match

    def submit_rfc(self, title: str, content: str, author_id: str) -> Dict[str, Any]:
        rfc = {
            "id": f"rfc_{len(self._rfc_items) + 1}",
            "title": title,
            "content": content,
            "author_id": author_id,
            "status": "draft",
            "comments": [],
        }
        self._rfc_items.append(rfc)
        return rfc

    def get_developer_profile(self, user_id: str, username: str = "") -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "username": username or f"user_{user_id}",
            "reputation": 0,
            "posts_count": sum(1 for p in self._posts.values() if p.author_id == user_id),
            "events_attended": 0,
            "groups": [g["name"] for g in self._user_groups.values() if user_id in g["members"]],
        }

    def get_recognition_programme(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "badges": [
                {"name": "Early Adopter", "description": "Joined the I community in the first year"},
                {"name": "Top Contributor", "description": "Made significant contributions to the ecosystem"},
                {"name": "Package Publisher", "description": "Published a package to the registry"},
            ],
            "top_contributors": [],
        }
