"""Tests for isoko.ideveloper.urubuga — Official Website."""

from __future__ import annotations

from isoko.ideveloper.urubuga import WebsiteManager


def test_website_init():
    wm = WebsiteManager()
    assert wm.get_news() == []
    assert wm.get_releases() == []
    assert wm.get_stats()["total_downloads"] == 0


def test_add_news():
    wm = WebsiteManager()
    item = wm.add_news_item("I 0.2 Released", "New features", "Core Team")
    assert item["title"] == "I 0.2 Released"
    assert len(wm.get_news()) == 1


def test_add_release():
    wm = WebsiteManager()
    release = wm.add_release("0.2.0", "Major update", "2026-01-15")
    assert release["version"] == "0.2.0"
    assert len(wm.get_releases()) == 1


def test_add_showcase():
    wm = WebsiteManager()
    item = wm.add_showcase("Awesome Project", "A project built with I", "https://example.com")
    assert item["title"] == "Awesome Project"
    assert len(wm.get_showcases()) == 1


def test_success_stories():
    wm = WebsiteManager()
    story = wm.add_success_story("Acme Corp", "We built our platform with I", "Acme")
    assert story["name"] == "Acme Corp"
    assert len(wm.get_success_stories()) == 1


def test_update_stats():
    wm = WebsiteManager()
    wm.update_stats(github_stars=1000, total_contributors=50)
    assert wm.get_stats()["github_stars"] == 1000
    assert wm.get_stats()["total_contributors"] == 50


def test_roadmap():
    wm = WebsiteManager()
    items = [{"quarter": "Q1 2026", "milestones": ["Feature A", "Feature B"]}]
    wm.set_roadmap(items)
    assert len(wm.get_roadmap()) == 1


def test_download_info():
    wm = WebsiteManager()
    info = wm.get_download_info()
    assert info["latest_version"] == "0.1.0"
    assert "windows" in info["platforms"]


def test_community_stats():
    wm = WebsiteManager()
    stats = wm.get_community_stats()
    assert "github_stars" in stats
    assert "open_source_projects" in stats
