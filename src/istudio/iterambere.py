"""I STUDIO — Collaboration (Iterambere)."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from .ibikoreshingiro import CollaborationRole


class CollaborationManager:
    def __init__(self):
        self._users: Dict[str, Dict[str, Any]] = {}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._edits: List[Dict[str, Any]] = []
        self._comments: Dict[str, List[Dict[str, Any]]] = {}
        self._reviews: Dict[str, List[Dict[str, Any]]] = {}
        self._listeners: Dict[str, List[Callable]] = {}

    def create_session(self, session_id: str, host: str, name: str = "") -> Dict[str, Any]:
        session = {
            "id": session_id,
            "name": name or f"Session {session_id[:8]}",
            "host": host,
            "created_at": time.time(),
            "users": [host],
            "active": True,
        }
        self._sessions[session_id] = session
        self._emit("session.created", {"session": session})
        return session

    def join_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        session = self._sessions.get(session_id)
        if not session or not session["active"]:
            return None
        if user_id not in session["users"]:
            session["users"].append(user_id)
        if user_id not in self._users:
            self._users[user_id] = {
                "id": user_id,
                "joined_at": time.time(),
                "role": CollaborationRole.EDITOR,
            }
        self._emit("user.joined", {"session_id": session_id, "user_id": user_id})
        return session

    def leave_session(self, session_id: str, user_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        if user_id in session["users"]:
            session["users"].remove(user_id)
        self._emit("user.left", {"session_id": session_id, "user_id": user_id})
        if not session["users"]:
            session["active"] = False
        return True

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        return list(self._sessions.values())

    def add_user(self, user_id: str, name: str = "", role: CollaborationRole = CollaborationRole.EDITOR) -> Dict[str, Any]:
        user = {
            "id": user_id,
            "name": name or user_id,
            "role": role.value,
            "joined_at": time.time(),
            "online": True,
        }
        self._users[user_id] = user
        self._emit("user.added", {"user": user})
        return user

    def remove_user(self, user_id: str) -> bool:
        user = self._users.pop(user_id, None)
        if user:
            self._emit("user.removed", {"user_id": user_id})
            return True
        return False

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)

    def list_users(self) -> List[Dict[str, Any]]:
        return list(self._users.values())

    def track_edit(self, user_id: str, file_path: str, edit_data: Dict[str, Any]) -> None:
        edit = {
            "user_id": user_id,
            "file_path": file_path,
            "timestamp": time.time(),
            "data": edit_data,
        }
        self._edits.append(edit)
        self._emit("edit.tracked", {"edit": edit})

    def get_edit_history(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        if file_path:
            return [e for e in self._edits if e["file_path"] == file_path]
        return list(self._edits)

    def add_comment(self, file_path: str, user_id: str, content: str, line: int = 0) -> Dict[str, Any]:
        comment = {
            "id": f"comment_{int(time.time() * 1000)}_{user_id}",
            "file_path": file_path,
            "user_id": user_id,
            "content": content,
            "line": line,
            "timestamp": time.time(),
            "resolved": False,
        }
        self._comments.setdefault(file_path, []).append(comment)
        self._emit("comment.added", {"comment": comment})
        return comment

    def resolve_comment(self, comment_id: str, file_path: str) -> bool:
        comments = self._comments.get(file_path, [])
        for comment in comments:
            if comment["id"] == comment_id:
                comment["resolved"] = True
                self._emit("comment.resolved", {"comment_id": comment_id})
                return True
        return False

    def get_comments(self, file_path: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        if file_path:
            return {file_path: self._comments.get(file_path, [])}
        return dict(self._comments)

    def create_review(self, review_id: str, title: str, author: str, files: List[str]) -> Dict[str, Any]:
        review = {
            "id": review_id,
            "title": title,
            "author": author,
            "files": files,
            "status": "open",
            "comments": [],
            "approvals": [],
            "created_at": time.time(),
        }
        self._reviews[review_id] = review
        self._emit("review.created", {"review": review})
        return review

    def approve_review(self, review_id: str, user_id: str) -> bool:
        review = self._reviews.get(review_id)
        if not review:
            return False
        if user_id not in review["approvals"]:
            review["approvals"].append(user_id)
        self._emit("review.approved", {"review_id": review_id, "user_id": user_id})
        return True

    def merge_review(self, review_id: str) -> bool:
        review = self._reviews.get(review_id)
        if not review:
            return False
        review["status"] = "merged"
        self._emit("review.merged", {"review_id": review_id})
        return True

    def get_reviews(self) -> List[Dict[str, Any]]:
        return list(self._reviews.values())

    def on(self, event: str, handler: Callable) -> None:
        self._listeners.setdefault(event, []).append(handler)

    def _emit(self, event: str, data: Dict[str, Any]) -> None:
        for handler in self._listeners.get(event, []):
            try:
                handler(data)
            except Exception:
                pass
