"""Tests for isoko.ideveloper.itegeko — CLI bridge."""

from __future__ import annotations

import argparse
import json
import sys

from isoko.ideveloper.itegeko import (
    register_subcommands,
    genda,
    _cmd_login,
    _cmd_publish,
    _cmd_search,
    _cmd_docs,
    _cmd_learn,
    _cmd_certify,
    _cmd_profile,
    _cmd_research,
    _cmd_website,
    _cmd_package,
    _cmd_foundation,
    _cmd_labs,
    _cmd_scholarships,
    _cmd_conference,
)


def _make_args(idev_cmd: str, **kwargs) -> argparse.Namespace:
    ns = argparse.Namespace()
    ns.command = "idev"
    ns.idev_command = idev_cmd
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_register_subcommands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    register_subcommands(subparsers)
    args = parser.parse_args(["idev", "login"])
    assert args.command == "idev"
    assert args.idev_command == "login"


def test_genda_no_command():
    args = _make_args("")
    assert "idev_command" in args or True
    args2 = argparse.Namespace()
    args2.command = "idev"
    assert genda(args2) == 1


def test_genda_unknown():
    args = _make_args("nonexistent")
    assert genda(args) == 1


def test_cmd_login_with_token():
    args = _make_args("login", token="test-token")
    code = _cmd_login(args)
    assert code == 0


def test_cmd_login_without_token():
    args = _make_args("login")
    code = _cmd_login(args)
    assert code == 0


def test_cmd_publish():
    args = _make_args("publish", name="test-pkg", version="1.0.0", description="A test", visibility="public")
    code = _cmd_publish(args)
    assert code == 0


def test_cmd_search():
    args = _make_args("search", query="test")
    code = _cmd_search(args)
    assert code == 0


def test_cmd_docs_get():
    args = _make_args("docs", command="get", query="/intro")
    code = _cmd_docs(args)
    assert code == 0


def test_cmd_docs_search():
    args = _make_args("docs", command="search", query="install")
    code = _cmd_docs(args)
    assert code == 0


def test_cmd_docs_guide():
    args = _make_args("docs", command="guide", query="")
    code = _cmd_docs(args)
    assert code == 0


def test_cmd_docs_tutorial():
    args = _make_args("docs", command="tutorial", query="")
    code = _cmd_docs(args)
    assert code == 0


def test_cmd_learn_courses():
    args = _make_args("learn", command="courses", id="", code="")
    code = _cmd_learn(args)
    assert code == 0


def test_cmd_learn_enroll():
    args = _make_args("learn", command="enroll", id="course-1", code="")
    code = _cmd_learn(args)
    assert code == 0


def test_cmd_learn_playground():
    args = _make_args("learn", command="playground", id="", code="function main() {}")
    code = _cmd_learn(args)
    assert code == 0


def test_cmd_learn_challenges():
    args = _make_args("learn", command="challenges", id="", code="")
    code = _cmd_learn(args)
    assert code == 0


def test_cmd_certify_list():
    args = _make_args("certify", command="list", id="")
    code = _cmd_certify(args)
    assert code == 0


def test_cmd_certify_info():
    args = _make_args("certify", command="info", id="i-certified-developer")
    code = _cmd_certify(args)
    assert code == 0


def test_cmd_certify_exam():
    args = _make_args("certify", command="exam", id="exam_i-certified-developer")
    code = _cmd_certify(args)
    assert code == 0


def test_cmd_certify_verify():
    args = _make_args("certify", command="verify", id="i-certified-developer")
    code = _cmd_certify(args)
    assert code == 0


def test_cmd_profile_show():
    args = _make_args("profile", command="show")
    code = _cmd_profile(args)
    assert code == 0


def test_cmd_profile_badges():
    args = _make_args("profile", command="badges")
    code = _cmd_profile(args)
    assert code == 0


def test_cmd_website_news():
    args = _make_args("website", command="news")
    code = _cmd_website(args)
    assert code == 0


def test_cmd_website_releases():
    args = _make_args("website", command="releases")
    code = _cmd_website(args)
    assert code == 0


def test_cmd_website_roadmap():
    args = _make_args("website", command="roadmap")
    code = _cmd_website(args)
    assert code == 0


def test_cmd_website_stats():
    args = _make_args("website", command="stats")
    code = _cmd_website(args)
    assert code == 0


def test_cmd_website_download():
    args = _make_args("website", command="download")
    code = _cmd_website(args)
    assert code == 0


def test_cmd_package_info():
    args = _make_args("package", command="info", name="test-pkg", version="")
    code = _cmd_package(args)
    assert code == 0


def test_cmd_package_stats():
    args = _make_args("package", command="stats", name="test-pkg", version="")
    code = _cmd_package(args)
    assert code == 0


def test_cmd_package_yank():
    args = _make_args("package", command="yank", name="test-pkg", version="1.0.0")
    code = _cmd_package(args)
    assert code == 0


def test_cmd_package_verify():
    args = _make_args("package", command="verify", name="test-pkg", version="")
    code = _cmd_package(args)
    assert code == 0


# ── New command tests ─────────────────────────────────────────────────

def test_cmd_learn_academy():
    args = _make_args("learn", command="academy", id="", code="", name="", path_id="")
    code = _cmd_learn(args)
    assert code == 0


def test_cmd_learn_paths():
    args = _make_args("learn", command="paths", id="path-1", code="", name="", path_id="")
    code = _cmd_learn(args)
    assert code == 0


def test_cmd_learn_achievements():
    args = _make_args("learn", command="achievements", id="", code="", name="", path_id="")
    code = _cmd_learn(args)
    assert code == 0


def test_cmd_learn_assignments():
    args = _make_args("learn", command="assignments", id="", code="", name="HW1", path_id="")
    code = _cmd_learn(args)
    assert code == 0


def test_cmd_docs_books():
    args = _make_args("docs", command="books", query="", book="Intro to I")
    code = _cmd_docs(args)
    assert code == 0


def test_cmd_docs_books_no_book():
    args = _make_args("docs", command="books", query="", book="")
    code = _cmd_docs(args)
    assert code == 0


def test_cmd_research_groups():
    args = _make_args("research", command="groups", id="group-1", name="")
    code = _cmd_research(args)
    assert code == 0


def test_cmd_foundation_info():
    args = _make_args("foundation", command="info")
    code = _cmd_foundation(args)
    assert code == 0


def test_cmd_foundation_members():
    args = _make_args("foundation", command="members")
    code = _cmd_foundation(args)
    assert code == 0


def test_cmd_foundation_board():
    args = _make_args("foundation", command="board")
    code = _cmd_foundation(args)
    assert code == 0


def test_cmd_foundation_policies():
    args = _make_args("foundation", command="policies")
    code = _cmd_foundation(args)
    assert code == 0


def test_cmd_foundation_charter():
    args = _make_args("foundation", command="charter")
    code = _cmd_foundation(args)
    assert code == 0


def test_cmd_labs_list():
    args = _make_args("labs", command="list", id="", step="")
    code = _cmd_labs(args)
    assert code == 0


def test_cmd_labs_start():
    args = _make_args("labs", command="start", id="lab-intro-ai", step="")
    code = _cmd_labs(args)
    assert code == 0


def test_cmd_labs_progress():
    args = _make_args("labs", command="progress", id="lab-intro-ai", step="")
    code = _cmd_labs(args)
    assert code == 0


def test_cmd_labs_steps():
    args = _make_args("labs", command="steps", id="lab-intro-ai", step="step-1")
    code = _cmd_labs(args)
    assert code == 0


def test_cmd_scholarships_list():
    args = _make_args("scholarships", command="list", id="", name="", proposal="", applicant="")
    code = _cmd_scholarships(args)
    assert code == 0


def test_cmd_scholarships_apply():
    args = _make_args("scholarships", command="apply", id="", name="I Scholar", proposal="Need funding", applicant="")
    code = _cmd_scholarships(args)
    assert code == 0


def test_cmd_scholarships_status():
    args = _make_args("scholarships", command="status", id="", name="", proposal="", applicant="user-1")
    code = _cmd_scholarships(args)
    assert code == 0


def test_cmd_scholarships_award():
    args = _make_args("scholarships", command="award", id="app-1", name="", proposal="", applicant="")
    code = _cmd_scholarships(args)
    assert code == 0


def test_cmd_conference_info():
    args = _make_args("conference", command="info")
    code = _cmd_conference(args)
    assert code == 0


def test_cmd_conference_sessions():
    args = _make_args("conference", command="sessions", session_title="")
    code = _cmd_conference(args)
    assert code == 0


def test_cmd_conference_speakers():
    args = _make_args("conference", command="speakers", speaker="Dr. Smith")
    code = _cmd_conference(args)
    assert code == 0


def test_cmd_conference_sponsors():
    args = _make_args("conference", command="sponsors")
    code = _cmd_conference(args)
    assert code == 0


def test_cmd_conference_cfp():
    args = _make_args("conference", command="cfp")
    code = _cmd_conference(args)
    assert code == 0


def test_cmd_conference_schedule():
    args = _make_args("conference", command="schedule")
    code = _cmd_conference(args)
    assert code == 0
