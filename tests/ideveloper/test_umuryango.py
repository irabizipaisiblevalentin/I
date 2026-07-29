"""Tests for isoko.ideveloper.umuryango — Community Platform."""

from __future__ import annotations

from isoko.ideveloper.umuryango import CommunityPlatform
from isoko.ideveloper.ibikoreshingiro import CommunityPost, Discussion, Event, EventType


def test_community_init():
    cp = CommunityPlatform()
    assert cp.search_discussions("") == []


def test_create_discussion():
    cp = CommunityPlatform()
    d = Discussion(title="How to start?", content="I'm new", author_id="u1", author_name="Alice")
    did = cp.create_discussion(d)
    assert cp.get_discussion(did) is not None


def test_search_discussions():
    cp = CommunityPlatform()
    cp.create_discussion(Discussion(title="I Compiler", content="How does the compiler work?", author_id="u1", author_name="Bob"))
    cp.create_discussion(Discussion(title="Web Framework", content="Best web framework?", author_id="u2", author_name="Alice"))
    results = cp.search_discussions("compiler")
    assert len(results) == 1


def test_add_reply():
    cp = CommunityPlatform()
    did = cp.create_discussion(Discussion(title="Question", author_id="u1", author_name="User"))
    reply = CommunityPost(author_id="u2", author_name="Helper", title="Re:", content="Answer")
    assert cp.add_reply(did, reply) is True
    assert cp.add_reply("nonexistent", reply) is False


def test_create_event():
    cp = CommunityPlatform()
    event = Event(title="I Conf 2026", type=EventType.CONFERENCE, location="Kigali")
    eid = cp.create_event(event)
    assert cp.get_event(eid) is not None


def test_list_events():
    cp = CommunityPlatform()
    cp.create_event(Event(title="Conference", type=EventType.CONFERENCE))
    cp.create_event(Event(title="Workshop", type=EventType.WORKSHOP))
    assert len(cp.list_events(EventType.CONFERENCE)) == 1
    assert len(cp.list_events()) == 2


def test_register_for_event():
    cp = CommunityPlatform()
    eid = cp.create_event(Event(title="Meetup", max_attendees=50))
    assert cp.register_for_event(eid, "user1") is True
    assert cp.register_for_event("nonexistent", "user1") is False


def test_create_forum():
    cp = CommunityPlatform()
    forum = cp.create_forum("General", "General discussion")
    assert forum["name"] == "General"


def test_create_user_group():
    cp = CommunityPlatform()
    group = cp.create_user_group("I Enthusiasts", "u1", "Group for I fans")
    assert group["owner"] == "u1"
    assert "u1" in group["members"]


def test_mentorship():
    cp = CommunityPlatform()
    match = cp.request_mentorship("mentor1", "mentee1")
    assert match["status"] == "pending"


def test_submit_rfc():
    cp = CommunityPlatform()
    rfc = cp.submit_rfc("New Feature", "Description here", "u1")
    assert rfc["status"] == "draft"


def test_developer_profile():
    cp = CommunityPlatform()
    profile = cp.get_developer_profile("u1", "alice")
    assert profile["username"] == "alice"
    assert "reputation" in profile


def test_recognition_programme():
    cp = CommunityPlatform()
    prog = cp.get_recognition_programme()
    assert "badges" in prog
    assert "top_contributors" in prog
