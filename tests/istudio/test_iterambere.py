"""Tests for istudio.iterambere — Collaboration."""

from __future__ import annotations

from src.istudio.iterambere import CollaborationManager
from src.istudio.ibikoreshingiro import CollaborationRole


def test_collaboration_init():
    cm = CollaborationManager()
    assert cm.list_sessions() == []
    assert cm.list_users() == []


def test_create_session():
    cm = CollaborationManager()
    session = cm.create_session("sess1", "alice", "My Session")
    assert session["id"] == "sess1"
    assert session["host"] == "alice"
    assert session["name"] == "My Session"
    assert session["active"] is True


def test_join_session():
    cm = CollaborationManager()
    cm.create_session("sess1", "alice")
    session = cm.join_session("sess1", "bob")
    assert session is not None
    assert "bob" in session["users"]


def test_join_nonexistent_session():
    cm = CollaborationManager()
    assert cm.join_session("nonexistent", "alice") is None


def test_leave_session():
    cm = CollaborationManager()
    cm.create_session("sess1", "alice")
    cm.join_session("sess1", "bob")
    assert cm.leave_session("sess1", "bob") is True
    session = cm.get_session("sess1")
    assert "bob" not in session["users"]


def test_session_inactive_when_empty():
    cm = CollaborationManager()
    cm.create_session("sess1", "alice")
    cm.leave_session("sess1", "alice")
    session = cm.get_session("sess1")
    assert session["active"] is False


def test_get_session():
    cm = CollaborationManager()
    cm.create_session("sess1", "alice")
    assert cm.get_session("sess1") is not None
    assert cm.get_session("nonexistent") is None


def test_add_user():
    cm = CollaborationManager()
    user = cm.add_user("bob", "Bob Smith", CollaborationRole.EDITOR)
    assert user["id"] == "bob"
    assert user["name"] == "Bob Smith"
    assert user["role"] == "editor"
    assert user["online"] is True


def test_remove_user():
    cm = CollaborationManager()
    cm.add_user("bob")
    assert cm.remove_user("bob") is True
    assert cm.remove_user("bob") is False


def test_get_user():
    cm = CollaborationManager()
    cm.add_user("bob")
    assert cm.get_user("bob") is not None
    assert cm.get_user("nonexistent") is None


def test_list_users():
    cm = CollaborationManager()
    cm.add_user("alice")
    cm.add_user("bob")
    assert len(cm.list_users()) == 2


def test_track_edit():
    cm = CollaborationManager()
    cm.track_edit("alice", "main.i", {"type": "insert", "text": "hello"})
    history = cm.get_edit_history("main.i")
    assert len(history) == 1
    assert history[0]["user_id"] == "alice"


def test_get_edit_history_all():
    cm = CollaborationManager()
    cm.track_edit("alice", "a.i", {})
    cm.track_edit("bob", "b.i", {})
    assert len(cm.get_edit_history()) == 2


def test_add_comment():
    cm = CollaborationManager()
    comment = cm.add_comment("main.i", "alice", "Fix this bug", line=42)
    assert comment["file_path"] == "main.i"
    assert comment["user_id"] == "alice"
    assert comment["line"] == 42
    assert comment["resolved"] is False


def test_resolve_comment():
    cm = CollaborationManager()
    comment = cm.add_comment("main.i", "alice", "Fix this")
    assert cm.resolve_comment(comment["id"], "main.i") is True
    comments = cm.get_comments("main.i")
    assert comments["main.i"][0]["resolved"] is True


def test_resolve_nonexistent_comment():
    cm = CollaborationManager()
    assert cm.resolve_comment("nonexistent", "main.i") is False


def test_get_comments():
    cm = CollaborationManager()
    cm.add_comment("a.i", "alice", "comment 1")
    cm.add_comment("b.i", "bob", "comment 2")
    all_comments = cm.get_comments()
    assert "a.i" in all_comments
    assert "b.i" in all_comments


def test_create_review():
    cm = CollaborationManager()
    review = cm.create_review("PR-1", "Add feature X", "alice", ["main.i", "lib.i"])
    assert review["id"] == "PR-1"
    assert review["title"] == "Add feature X"
    assert review["author"] == "alice"
    assert review["status"] == "open"


def test_approve_review():
    cm = CollaborationManager()
    cm.create_review("PR-1", "Feature", "alice", [])
    assert cm.approve_review("PR-1", "bob") is True
    assert cm.approve_review("nonexistent", "bob") is False


def test_merge_review():
    cm = CollaborationManager()
    cm.create_review("PR-1", "Feature", "alice", [])
    assert cm.merge_review("PR-1") is True
    assert cm.get_reviews()[0]["status"] == "merged"
    assert cm.merge_review("nonexistent") is False


def test_get_reviews():
    cm = CollaborationManager()
    cm.create_review("PR-1", "Feature A", "alice", [])
    cm.create_review("PR-2", "Feature B", "bob", [])
    assert len(cm.get_reviews()) == 2


def test_collaboration_events():
    cm = CollaborationManager()
    events = []
    cm.on("session.created", lambda d: events.append(("created", d["session"]["id"])))
    cm.on("user.joined", lambda d: events.append(("joined", d["user_id"])))
    cm.create_session("s1", "alice")
    cm.join_session("s1", "bob")
    assert len(events) >= 2
