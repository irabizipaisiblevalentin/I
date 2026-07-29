"""Tests for isoko.ideveloper.isoko — Open Source / Project Hosting."""

from __future__ import annotations

from isoko.ideveloper.isoko import OpenSourcePlatform


def test_opensource_init():
    osp = OpenSourcePlatform()
    assert osp.search_projects("") == []


def test_create_project():
    osp = OpenSourcePlatform()
    proj = osp.create_project("my-lib", "user1", "A great library")
    assert proj["name"] == "my-lib"
    assert proj["visibility"] == "public"


def test_search_projects():
    osp = OpenSourcePlatform()
    osp.create_project("web-framework", "u1", "Web framework")
    osp.create_project("game-engine", "u2", "Game engine")
    results = osp.search_projects("web")
    assert len(results) == 1


def test_create_issue():
    osp = OpenSourcePlatform()
    proj = osp.create_project("my-lib", "u1")
    issue = osp.create_issue(proj["id"], "Bug found", "Description", "u1")
    assert issue is not None
    assert issue["status"] == "open"


def test_get_issues():
    osp = OpenSourcePlatform()
    proj = osp.create_project("my-lib", "u1")
    osp.create_issue(proj["id"], "Bug 1", "Desc", "u1")
    osp.create_issue(proj["id"], "Bug 2", "Desc", "u2")
    assert len(osp.get_issues(proj["id"])) == 2


def test_create_review():
    osp = OpenSourcePlatform()
    proj = osp.create_project("my-lib", "u1")
    review = osp.create_review(proj["id"], "Add feature", "u2", [{"file": "main.i", "changes": "..."}])
    assert review is not None
    assert review["status"] == "open"


def test_approve_review():
    osp = OpenSourcePlatform()
    proj = osp.create_project("my-lib", "u1")
    review = osp.create_review(proj["id"], "Patch", "u2", [])
    assert osp.approve_review(proj["id"], review["id"], "reviewer1") is True
    assert osp.approve_review(proj["id"], review["id"], "reviewer2") is True
    assert review["status"] == "approved"


def test_project_templates():
    osp = OpenSourcePlatform()
    tmpl = osp.add_project_template("Library", "Template for libraries", {"src/lib.i": "// code"})
    assert tmpl["name"] == "Library"
    assert len(osp.get_project_templates()) == 1


def test_contributor_dashboard():
    osp = OpenSourcePlatform()
    proj = osp.create_project("my-lib", "u1")
    dashboard = osp.get_contributor_dashboard(proj["id"])
    assert "total_contributors" in dashboard


def test_funding():
    osp = OpenSourcePlatform()
    proj = osp.create_project("my-lib", "u1")
    funding = osp.add_funding(proj["id"], "sponsor1", 100.0, "Great work!")
    assert funding is not None
    assert osp.add_funding("nonexistent", "s1", 50.0) is None


def test_community_governance():
    osp = OpenSourcePlatform()
    proj = osp.create_project("my-lib", "u1")
    gov = osp.get_community_governance(proj["id"])
    assert "code_of_conduct" in gov
