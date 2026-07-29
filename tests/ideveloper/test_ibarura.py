"""Tests for isoko.ideveloper.ibarura — Analytics."""

from __future__ import annotations

from isoko.ideveloper.ibarura import AnalyticsEngine
from isoko.ideveloper.ibikoreshingiro import PlatformModule


def test_analytics_init():
    ae = AnalyticsEngine()
    assert ae.get_download_metrics()["total_downloads"] == 0


def test_track_metric():
    ae = AnalyticsEngine()
    rid = ae.track_metric(PlatformModule.REGISTRY, "publishes", 1.0)
    assert rid is not None
    reports = ae.get_metric(PlatformModule.REGISTRY, "publishes")
    assert len(reports) == 1


def test_package_downloads():
    ae = AnalyticsEngine()
    ae.track_package_download("pkg-a")
    ae.track_package_download("pkg-a")
    ae.track_package_download("pkg-b")
    stats = ae.get_package_statistics("pkg-a")
    assert stats["total_downloads"] == 2


def test_doc_usage():
    ae = AnalyticsEngine()
    ae.track_doc_usage("/intro")
    ae.track_doc_usage("/intro")
    ae.track_doc_usage("/guide")
    popular = ae.get_popular_docs(limit=5)
    assert len(popular) == 2
    assert popular[0]["path"] == "/intro"


def test_performance_dashboards():
    ae = AnalyticsEngine()
    dashboards = ae.get_performance_dashboards()
    assert "registry" in dashboards
    assert "docs" in dashboards


def test_learning_progress():
    ae = AnalyticsEngine()
    ae.track_learning_progress("user1", "course1", 50.0)
    ae.track_learning_progress("user1", "course1", 100.0)
    report = ae.get_learning_progress_report()
    assert report["total_learners"] == 1


def test_release_adoption():
    ae = AnalyticsEngine()
    ae.track_release_adoption("0.2.0", 15.5)
    ae.track_release_adoption("0.1.0", 75.0)
    adoption = ae.get_release_adoption()
    assert adoption["0.2.0"] == 15.5


def test_security_reports():
    ae = AnalyticsEngine()
    reports = ae.get_security_reports()
    assert len(reports) == 2


def test_community_growth():
    ae = AnalyticsEngine()
    growth = ae.get_community_growth_metrics()
    assert "total_users" in growth
    assert "countries_reached" in growth


def test_track_dashboard_metric():
    ae = AnalyticsEngine()
    ae.track_dashboard_metric("growth", "new_users", 100)
    # Should not raise
    assert True
