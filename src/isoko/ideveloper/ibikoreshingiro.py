"""I Developer Platform — Core types, enums, and dataclasses."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


IDEVP_VERSION = "0.1.0"


class PlatformModule(enum.Enum):
    WEBSITE = "website"
    DOCUMENTATION = "documentation"
    REGISTRY = "registry"
    LEARNING = "learning"
    CERTIFICATION = "certification"
    COMMUNITY = "community"
    OPEN_SOURCE = "open_source"
    ENTERPRISE = "enterprise"
    RESEARCH = "research"
    GLOBALISATION = "globalisation"
    ANALYTICS = "analytics"
    SECURITY = "security"


class PlatformStatus(enum.Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OUTAGE = "outage"
    BETA = "beta"
    PLANNED = "planned"


class UserRole(enum.Enum):
    DEVELOPER = "developer"
    STUDENT = "student"
    EDUCATOR = "educator"
    RESEARCHER = "researcher"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"
    PARTNER = "partner"
    MODERATOR = "moderator"


class AccountTier(enum.Enum):
    FREE = "free"
    DEVELOPER = "developer"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ACADEMIC = "academic"


class PackageVisibility(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    ENTERPRISE = "enterprise"


class CertificationLevel(enum.Enum):
    ASSOCIATE = "associate"
    PROFESSIONAL = "professional"
    EXPERT = "expert"
    ARCHITECT = "architect"
    INSTRUCTOR = "instructor"


class CourseLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EventType(enum.Enum):
    CONFERENCE = "conference"
    MEETUP = "meetup"
    WORKSHOP = "workshop"
    HACKATHON = "hackathon"
    WEBINAR = "webinar"
    BOOTCAMP = "bootcamp"


class SupportPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AuditSeverity(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKER = "blocker"


class AchievementType(enum.Enum):
    COURSE_COMPLETE = "course_complete"
    CHALLENGE_SOLVED = "challenge_solved"
    STREAK = "streak"
    CERTIFICATION = "certification"
    CONTRIBUTION = "contribution"
    MILESTONE = "milestone"


class AssignmentStatus(enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    SUBMITTED = "submitted"
    GRADED = "graded"
    LATE = "late"


class LabDomain(enum.Enum):
    AI = "ai"
    NETWORKING = "networking"
    CYBERSECURITY = "cybersecurity"
    DATABASES = "databases"
    CLOUD = "cloud"
    SYSTEMS = "systems"


class ScholarshipStatus(enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    REVIEWING = "reviewing"
    AWARDED = "awarded"
    CLOSED = "closed"


class ConferenceSessionType(enum.Enum):
    KEYNOTE = "keynote"
    TALK = "talk"
    WORKSHOP = "workshop"
    PANEL = "panel"
    TUTORIAL = "tutorial"
    LIGHTNING = "lightning"


@dataclass
class UserProfile:
    id: str = ""
    username: str = ""
    email: str = ""
    display_name: str = ""
    role: UserRole = UserRole.DEVELOPER
    tier: AccountTier = AccountTier.FREE
    bio: str = ""
    avatar_url: str = ""
    website: str = ""
    github: str = ""
    joined_at: str = ""
    location: str = ""
    languages: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)


@dataclass
class DeveloperProfile:
    user_id: str = ""
    packages_published: int = 0
    projects_created: int = 0
    certifications: List[str] = field(default_factory=list)
    contributions: int = 0
    reputation: int = 0
    followers: int = 0
    following: int = 0
    skills: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)


@dataclass
class PackageRelease:
    name: str = ""
    version: str = ""
    description: str = ""
    author_id: str = ""
    author_name: str = ""
    license: str = "MIT"
    visibility: PackageVisibility = PackageVisibility.PUBLIC
    repository: str = ""
    documentation: str = ""
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    i_version: str = ">=0.1.0"
    readme: str = ""
    signature: str = ""
    verified: bool = False


@dataclass
class PackageVersion:
    package_name: str = ""
    version: str = ""
    published_at: str = ""
    downloads: int = 0
    size_bytes: int = 0
    checksum: str = ""
    yanked: bool = False
    deprecation_message: str = ""


@dataclass
class PackageStats:
    name: str = ""
    total_downloads: int = 0
    recent_downloads: int = 0
    versions_count: int = 0
    stars: int = 0
    forks: int = 0
    issues: int = 0
    open_issues: int = 0
    dependents: int = 0
    security_advisories: int = 0
    score: float = 0.0


@dataclass
class Lesson:
    id: str = ""
    title: str = ""
    content: str = ""
    duration_minutes: int = 0
    order: int = 0
    video_url: str = ""
    code_examples: List[str] = field(default_factory=list)
    quiz_questions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Module:
    id: str = ""
    title: str = ""
    description: str = ""
    lessons: List[Lesson] = field(default_factory=list)
    order: int = 0


@dataclass
class Course:
    id: str = ""
    title: str = ""
    description: str = ""
    level: CourseLevel = CourseLevel.BEGINNER
    modules: List[Module] = field(default_factory=list)
    duration_hours: int = 0
    author_id: str = ""
    author_name: str = ""
    rating: float = 0.0
    enrolled_count: int = 0
    completion_rate: float = 0.0
    prerequisites: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    certificate_id: str = ""


@dataclass
class CertificationExam:
    id: str = ""
    title: str = ""
    description: str = ""
    level: CertificationLevel = CertificationLevel.ASSOCIATE
    duration_minutes: int = 60
    passing_score: int = 70
    questions: List[Dict[str, Any]] = field(default_factory=list)
    price_usd: float = 0.0
    version: str = "1.0"


@dataclass
class Certification:
    id: str = ""
    title: str = ""
    description: str = ""
    level: CertificationLevel = CertificationLevel.ASSOCIATE
    exam: Optional[CertificationExam] = None
    issuer: str = "I Foundation"
    validity_years: int = 2
    badge_url: str = ""
    skills: List[str] = field(default_factory=list)


@dataclass
class CommunityPost:
    id: str = ""
    author_id: str = ""
    author_name: str = ""
    title: str = ""
    content: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    upvotes: int = 0
    downvotes: int = 0
    replies: int = 0
    views: int = 0
    created_at: str = ""
    pinned: bool = False
    solved: bool = False


@dataclass
class Discussion:
    id: str = ""
    title: str = ""
    author_id: str = ""
    author_name: str = ""
    content: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    replies: List[CommunityPost] = field(default_factory=list)
    created_at: str = ""
    last_activity: str = ""
    closed: bool = False


@dataclass
class Event:
    id: str = ""
    title: str = ""
    description: str = ""
    type: EventType = EventType.CONFERENCE
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    is_online: bool = False
    registration_url: str = ""
    max_attendees: int = 0
    attendees_count: int = 0
    organisers: List[str] = field(default_factory=list)
    sponsors: List[str] = field(default_factory=list)


@dataclass
class EnterprisePlan:
    id: str = ""
    name: str = ""
    description: str = ""
    price_monthly: float = 0.0
    max_users: int = 0
    max_projects: int = 0
    support_level: SupportPriority = SupportPriority.NORMAL
    features: List[str] = field(default_factory=list)
    private_registry: bool = False
    audit_logging: bool = False
    sso: bool = False
    sla_hours: int = 0


@dataclass
class SupportTicket:
    id: str = ""
    user_id: str = ""
    subject: str = ""
    description: str = ""
    priority: SupportPriority = SupportPriority.NORMAL
    status: str = "open"
    created_at: str = ""
    updated_at: str = ""
    assigned_to: str = ""
    resolution: str = ""


@dataclass
class AnalyticsReport:
    id: str = ""
    module: PlatformModule = PlatformModule.ANALYTICS
    metric: str = ""
    value: float = 0.0
    period: str = "daily"
    timestamp: str = ""
    dimensions: Dict[str, str] = field(default_factory=dict)


@dataclass
class SecurityAudit:
    id: str = ""
    target: str = ""
    severity: AuditSeverity = AuditSeverity.INFO
    description: str = ""
    action: str = ""
    timestamp: str = ""
    resolved: bool = False
    resolved_at: str = ""


@dataclass
class ResearchPaper:
    id: str = ""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    category: str = "compilers"
    url: str = ""
    doi: str = ""
    published_at: str = ""
    citations: int = 0
    institution: str = ""
    grant_id: str = ""


@dataclass
class LocalisedContent:
    locale: str = "en"
    translations: Dict[str, str] = field(default_factory=dict)
    region: str = "global"
    is_rtl: bool = False
    is_approved: bool = False
    translator_id: str = ""


@dataclass
class LearningPath:
    id: str = ""
    title: str = ""
    description: str = ""
    level: CourseLevel = CourseLevel.BEGINNER
    course_ids: List[str] = field(default_factory=list)
    estimated_hours: int = 0
    certificate_id: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Achievement:
    id: str = ""
    user_id: str = ""
    type: AchievementType = AchievementType.MILESTONE
    title: str = ""
    description: str = ""
    badge_url: str = ""
    unlocked_at: str = ""
    progress: float = 0.0


@dataclass
class Assignment:
    id: str = ""
    course_id: str = ""
    title: str = ""
    description: str = ""
    due_date: str = ""
    max_score: int = 100
    status: AssignmentStatus = AssignmentStatus.DRAFT
    submissions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Textbook:
    id: str = ""
    title: str = ""
    author: str = ""
    description: str = ""
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    version: str = "1.0"
    is_interactive: bool = True
    license: str = "CC-BY-SA"


@dataclass
class Lab:
    id: str = ""
    title: str = ""
    description: str = ""
    domain: LabDomain = LabDomain.SYSTEMS
    difficulty: str = "beginner"
    steps: List[Dict[str, str]] = field(default_factory=list)
    estimated_minutes: int = 30
    validation_script: str = ""
    resources: Dict[str, str] = field(default_factory=dict)


@dataclass
class Scholarship:
    id: str = ""
    title: str = ""
    description: str = ""
    amount_usd: float = 0.0
    deadline: str = ""
    status: ScholarshipStatus = ScholarshipStatus.DRAFT
    criteria: List[str] = field(default_factory=list)
    applications: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Conference:
    id: str = ""
    name: str = ""
    year: int = 2026
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    speakers: List[Dict[str, Any]] = field(default_factory=list)
    sponsors: List[Dict[str, Any]] = field(default_factory=list)
    cfp_open: bool = False


@dataclass
class FoundationMember:
    id: str = ""
    name: str = ""
    role: str = "member"
    email: str = ""
    joined_at: str = ""
    contributions: List[str] = field(default_factory=list)
