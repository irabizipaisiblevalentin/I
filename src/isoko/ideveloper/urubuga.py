"""I Developer Platform — Official Website (Urubuga)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class WebsiteManager:
    def __init__(self):
        self._news: List[Dict[str, Any]] = []
        self._releases: List[Dict[str, Any]] = []
        self._showcases: List[Dict[str, str]] = []
        self._success_stories: List[Dict[str, str]] = []
        self._stats: Dict[str, Any] = {
            "total_downloads": 0,
            "active_developers": 0,
            "packages_published": 0,
            "countries_reached": 0,
            "certifications_issued": 0,
        }
        self._roadmap: List[Dict[str, Any]] = []

    def add_news_item(self, title: str, content: str, author: str = "") -> Dict[str, Any]:
        item = {
            "id": f"news_{len(self._news) + 1}",
            "title": title,
            "content": content,
            "author": author,
            "published_at": "",
        }
        self._news.append(item)
        return item

    def get_news(self) -> List[Dict[str, Any]]:
        return list(self._news)

    def add_release(self, version: str, notes: str, date: str = "") -> Dict[str, Any]:
        release = {
            "version": version,
            "notes": notes,
            "date": date,
            "download_url": f"https://i-lang.org/download/{version}",
        }
        self._releases.append(release)
        return release

    def get_releases(self) -> List[Dict[str, Any]]:
        return list(self._releases)

    def add_showcase(self, title: str, description: str, url: str = "") -> Dict[str, str]:
        item = {"title": title, "description": description, "url": url}
        self._showcases.append(item)
        return item

    def get_showcases(self) -> List[Dict[str, str]]:
        return list(self._showcases)

    def add_success_story(self, name: str, story: str, organisation: str = "") -> Dict[str, str]:
        item = {"name": name, "story": story, "organisation": organisation}
        self._success_stories.append(item)
        return item

    def get_success_stories(self) -> List[Dict[str, str]]:
        return list(self._success_stories)

    def update_stats(self, **kwargs: int) -> None:
        self._stats.update(kwargs)

    def get_stats(self) -> Dict[str, Any]:
        return dict(self._stats)

    def set_roadmap(self, items: List[Dict[str, Any]]) -> None:
        self._roadmap = list(items)

    def get_roadmap(self) -> List[Dict[str, Any]]:
        return list(self._roadmap)

    def get_download_info(self) -> Dict[str, str]:
        return {
            "latest_version": "0.1.0",
            "download_url": "https://i-lang.org/download",
            "checksum": "",
            "platforms": "windows, macOS, linux",
        }

    def get_community_stats(self) -> Dict[str, int]:
        return {
            "github_stars": self._stats.get("github_stars", 0),
            "total_contributors": self._stats.get("total_contributors", 0),
            "open_source_projects": self._stats.get("open_source_projects", 0),
            "meetup_members": self._stats.get("meetup_members", 0),
        }
