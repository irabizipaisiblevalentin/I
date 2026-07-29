"""Tests for isoko.ideveloper.ibikoreshingiro — Core types."""

from __future__ import annotations

from isoko.ideveloper.ibikoreshingiro import (
    IDEVP_VERSION,
    PlatformModule,
    PlatformStatus,
    UserRole,
    AccountTier,
    PackageVisibility,
    CertificationLevel,
    CourseLevel,
    EventType,
    SupportPriority,
    AuditSeverity,
    UserProfile,
    DeveloperProfile,
    PackageRelease,
    PackageVersion,
    PackageStats,
    Course,
    Lesson,
    Module,
    Certification,
    CertificationExam,
    CommunityPost,
    Discussion,
    Event,
    EnterprisePlan,
    SupportTicket,
    AnalyticsReport,
    SecurityAudit,
    ResearchPaper,
    LocalisedContent,
)


def test_idevp_version():
    assert IDEVP_VERSION == "0.1.0"


def test_enums_have_all_values():
    assert PlatformModule.WEBSITE.value == "website"
    assert PlatformStatus.OPERATIONAL.value == "operational"
    assert UserRole.DEVELOPER.value == "developer"
    assert AccountTier.FREE.value == "free"
    assert PackageVisibility.PUBLIC.value == "public"
    assert CertificationLevel.ASSOCIATE.value == "associate"
    assert CourseLevel.BEGINNER.value == "beginner"
    assert EventType.CONFERENCE.value == "conference"
    assert SupportPriority.LOW.value == "low"
    assert AuditSeverity.INFO.value == "info"


def test_user_profile_defaults():
    p = UserProfile()
    assert p.role == UserRole.DEVELOPER
    assert p.tier == AccountTier.FREE
    assert p.badges == []


def test_package_release_defaults():
    r = PackageRelease(name="test-pkg", version="1.0.0", description="A test package")
    assert r.license == "MIT"
    assert r.visibility == PackageVisibility.PUBLIC
    assert r.dependencies == {}


def test_course_structure():
    lesson = Lesson(id="l1", title="Intro", content="# Hello", order=1)
    assert lesson.duration_minutes == 0
    module = Module(id="m1", title="Basics", lessons=[lesson], order=1)
    course = Course(id="c1", title="I 101", modules=[module])
    assert course.level == CourseLevel.BEGINNER
    assert course.modules[0].lessons[0].title == "Intro"


def test_certification_defaults():
    exam = CertificationExam(id="exam1", title="I Certified Developer Exam")
    assert exam.passing_score == 70
    assert exam.duration_minutes == 60
    cert = Certification(id="i-certified-developer", title="I Certified Developer", exam=exam)
    assert cert.issuer == "I Foundation"
    assert cert.validity_years == 2


def test_community_post_defaults():
    post = CommunityPost(id="p1", author_id="u1", author_name="Alice", title="Hello", content="World")
    assert post.upvotes == 0
    assert post.pinned is False


def test_event_defaults():
    event = Event(id="e1", title="I Conf 2026")
    assert event.type == EventType.CONFERENCE
    assert event.is_online is False


def test_enterprise_plan():
    plan = EnterprisePlan(id="team", name="Team", price_monthly=99, max_users=25)
    assert plan.sla_hours == 0
    assert plan.private_registry is False


def test_support_ticket():
    ticket = SupportTicket(id="t1", user_id="u1", subject="Help", description="Issue")
    assert ticket.status == "open"
    assert ticket.priority == SupportPriority.NORMAL


def test_analytics_report():
    report = AnalyticsReport(metric="downloads", value=1000.0)
    assert report.module == PlatformModule.ANALYTICS
    assert report.period == "daily"


def test_security_audit():
    audit = SecurityAudit(target="package:test", severity=AuditSeverity.CRITICAL, description="Vulnerability")
    assert audit.resolved is False


def test_research_paper():
    paper = ResearchPaper(title="I Compiler Optimisation", authors=["Alice", "Bob"])
    assert paper.citations == 0
    assert paper.category == "compilers"


def test_localised_content():
    lc = LocalisedContent(locale="fr", translations={"welcome": "Bienvenue"})
    assert lc.is_rtl is False
    assert lc.is_approved is False


def test_developer_profile():
    dp = DeveloperProfile(user_id="u1")
    assert dp.packages_published == 0
    assert dp.reputation == 0
    assert dp.certifications == []
