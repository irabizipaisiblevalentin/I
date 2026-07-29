"""I Developer Platform — CLI bridge for isoko integration."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    ConferenceSessionType,
    IDEVP_VERSION,
    LabDomain,
    PackageRelease,
    PackageVisibility,
    PlatformModule,
    ScholarshipStatus,
)
from .ububiko import PackageRegistry
from .urubuga import WebsiteManager
from .inyandiko import DocumentationPlatform
from .amashuri import LearningPlatform
from .icyemezo import CertificationProgramme
from .umuryango import CommunityPlatform
from .isoko import OpenSourcePlatform
from .ibigo import EnterprisePlatform
from .ubushakashatsi import ResearchPlatform
from .isi_yose import GlobalisationManager
from .ibarura import AnalyticsEngine
from .umutekano import SecurityManager
from .ishyinguro import Foundation
from .laborotwari import Labs
from .inkunga import Scholarships
from .inama import GlobalConference


def register_subcommands(subparsers: Any) -> None:
    ip = subparsers.add_parser("idev", help="I Developer Platform commands")
    ip_se = ip.add_subparsers(dest="idev_command")

    p_login = ip_se.add_parser("login", help="Authenticate with the Developer Platform")
    p_login.add_argument("--token", help="API token")

    p_publish = ip_se.add_parser("publish", help="Publish a package")
    p_publish.add_argument("name", help="Package name")
    p_publish.add_argument("--version", default="0.1.0", help="Package version")
    p_publish.add_argument("--description", default="", help="Package description")
    p_publish.add_argument("--visibility", choices=["public", "private", "enterprise"], default="public", help="Package visibility")

    p_search = ip_se.add_parser("search", help="Search packages")
    p_search.add_argument("query", help="Search query")

    p_docs = ip_se.add_parser("docs", help="Access documentation")
    p_docs.add_argument("command", choices=["get", "search", "guide", "tutorial", "books"])
    p_docs.add_argument("query", nargs="?", default="", help="Documentation path or search query")
    p_docs.add_argument("--book", default="", help="Book title for books command")

    p_learn = ip_se.add_parser("learn", help="Learning platform")
    p_learn.add_argument("command", choices=["courses", "enroll", "progress", "playground", "challenges", "academy", "paths", "achievements", "assignments"])
    p_learn.add_argument("id", nargs="?", default="", help="Course ID")
    p_learn.add_argument("--code", default="", help="Code for playground")
    p_learn.add_argument("--name", default="", help="Name of learning path or assignment")
    p_learn.add_argument("--path-id", default="", help="Learning path ID")

    p_certify = ip_se.add_parser("certify", help="Certification programme")
    p_certify.add_argument("command", choices=["list", "info", "exam", "verify"])
    p_certify.add_argument("id", nargs="?", default="", help="Certification or exam ID")

    p_profile = ip_se.add_parser("profile", help="Developer profile")
    p_profile.add_argument("command", choices=["show", "badges"])

    p_community = ip_se.add_parser("community", help="Community platform")
    p_community.add_argument("command", choices=["events", "forums", "mentorship", "rfc"])

    p_enterprise = ip_se.add_parser("enterprise", help="Enterprise services")
    p_enterprise.add_argument("command", choices=["plans", "subscribe", "ticket", "advisories"])

    p_research = ip_se.add_parser("research", help="Research platform")
    p_research.add_argument("command", choices=["papers", "benchmarks", "partnerships", "groups"])
    p_research.add_argument("--name", default="", help="Research group name")
    p_research.add_argument("--id", default="", help="Group or entity ID")

    p_security = ip_se.add_parser("security", help="Security commands")
    p_security.add_argument("command", choices=["audit", "mfa", "keys"])

    p_analytics = ip_se.add_parser("analytics", help="Analytics dashboard")
    p_analytics.add_argument("command", choices=["metrics", "downloads", "growth", "docs-usage"])

    p_global = ip_se.add_parser("global", help="Globalisation settings")
    p_global.add_argument("command", choices=["locales", "mirrors", "translate"])

    p_website = ip_se.add_parser("website", help="Official website info")
    p_website.add_argument("command", choices=["news", "releases", "showcase", "roadmap", "stats", "download"])

    p_package = ip_se.add_parser("package", help="Package management")
    p_package.add_argument("command", choices=["info", "stats", "versions", "yank", "verify"])
    p_package.add_argument("name", help="Package name")
    p_package.add_argument("--version", default="", help="Package version")

    p_foundation = ip_se.add_parser("foundation", help="I Foundation governance")
    p_foundation.add_argument("command", choices=["info", "members", "board", "policies", "charter"])
    p_foundation.add_argument("--name", default="", help="Member name")
    p_foundation.add_argument("--role", default="", help="Member role")

    p_labs = ip_se.add_parser("labs", help="I Labs guided learning")
    p_labs.add_argument("command", choices=["list", "start", "progress", "steps"])
    p_labs.add_argument("id", nargs="?", default="", help="Lab ID")
    p_labs.add_argument("--step", default="", help="Step ID to validate")

    p_scholarships = ip_se.add_parser("scholarships", help="I Scholarships")
    p_scholarships.add_argument("command", choices=["list", "apply", "status", "award"])
    p_scholarships.add_argument("id", nargs="?", default="", help="Scholarship ID")
    p_scholarships.add_argument("--name", default="", help="Scholarship name")
    p_scholarships.add_argument("--proposal", default="", help="Application proposal")
    p_scholarships.add_argument("--applicant", default="", help="Applicant ID for status")

    p_conference = ip_se.add_parser("conference", help="I Global Conference")
    p_conference.add_argument("command", choices=["info", "sessions", "speakers", "sponsors", "cfp", "schedule"])
    p_conference.add_argument("--name", default="", help="Conference name")
    p_conference.add_argument("--session-title", default="", help="Session title")
    p_conference.add_argument("--speaker", default="", help="Speaker name")
    p_conference.add_argument("--sponsor", default="", help="Sponsor name")
    p_conference.add_argument("--tier", default="", help="Sponsor tier")
    p_conference.add_argument("--amount", type=float, default=0.0, help="Sponsor amount")


def genda(args: argparse.Namespace) -> int:
    idev_cmd = getattr(args, "idev_command", None)
    if not idev_cmd:
        print("idev: missing command\nRun 'isoko idev --help' for usage.")
        return 1
    handlers = {
        "login": _cmd_login,
        "publish": _cmd_publish,
        "search": _cmd_search,
        "docs": _cmd_docs,
        "learn": _cmd_learn,
        "certify": _cmd_certify,
        "profile": _cmd_profile,
        "community": _cmd_community,
        "enterprise": _cmd_enterprise,
        "research": _cmd_research,
        "security": _cmd_security,
        "analytics": _cmd_analytics,
        "global": _cmd_global,
        "website": _cmd_website,
        "package": _cmd_package,
        "foundation": _cmd_foundation,
        "labs": _cmd_labs,
        "scholarships": _cmd_scholarships,
        "conference": _cmd_conference,
    }
    handler = handlers.get(idev_cmd)
    if not handler:
        print(f"idev: unknown command '{idev_cmd}'")
        return 1
    return handler(args)


def _cmd_login(args: argparse.Namespace) -> int:
    token = getattr(args, "token", None)
    if token:
        print(json.dumps({"status": "ok", "message": "Authenticated successfully"}))
    else:
        print("Opening browser for authentication...")
        print(json.dumps({"status": "pending", "message": "Follow the instructions to authenticate"}))
    return 0


def _cmd_publish(args: argparse.Namespace) -> int:
    registry = PackageRegistry()
    visibility = PackageVisibility(args.visibility) if hasattr(args, "visibility") else PackageVisibility.PUBLIC
    release = PackageRelease(
        name=args.name,
        version=getattr(args, "version", "0.1.0"),
        description=getattr(args, "description", ""),
        visibility=visibility,
    )
    pkg_id = registry.publish(release)
    print(json.dumps({"status": "ok", "package": pkg_id}))
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    registry = PackageRegistry()
    results = registry.search(args.query)
    print(json.dumps(results, indent=2) if results else json.dumps({"message": "No results found"}))
    return 0


def _cmd_docs(args: argparse.Namespace) -> int:
    docs = DocumentationPlatform()
    cmd = args.command
    if cmd == "get":
        result = docs.get_document(args.query) if args.query else None
        print(json.dumps({"path": args.query, "found": result is not None}))
    elif cmd == "search":
        results = docs.search(args.query) if args.query else []
        print(json.dumps(results, indent=2))
    elif cmd == "guide":
        guides = docs.get_guides()
        print(json.dumps([g["title"] for g in guides], indent=2))
    elif cmd == "tutorial":
        tutorials = docs.get_tutorials()
        print(json.dumps([t["title"] for t in tutorials], indent=2))
    elif cmd == "books":
        book_name = getattr(args, "book", "") or args.query
        if book_name:
            book = docs.get_book(book_name)
            if book:
                print(json.dumps({"title": book["title"], "chapters": len(book.get("chapters", [])), "exercises": len(book.get("exercises", []))}, indent=2))
            else:
                print(json.dumps({"error": "Book not found"}))
        else:
            print(json.dumps({"message": "Use --book to specify a book title"}))
    return 0


def _cmd_learn(args: argparse.Namespace) -> int:
    lp = LearningPlatform()
    cmd = args.command
    if cmd == "courses":
        courses = lp.search_courses("")
        print(json.dumps([{"id": c.id, "title": c.title, "level": c.level.value} for c in courses], indent=2))
    elif cmd == "enroll":
        if args.id:
            lp.enroll("current-user", args.id)
            print(json.dumps({"status": "ok", "course_id": args.id}))
    elif cmd == "progress":
        progress = lp.get_progress("current-user", args.id) if args.id else 0.0
        print(json.dumps({"course_id": args.id, "progress": progress}))
    elif cmd == "playground":
        code = getattr(args, "code", "")
        session = lp.create_playground_session(code or "function main() {}")
        print(json.dumps(session, indent=2))
    elif cmd == "challenges":
        challenges = lp.get_challenges()
        print(json.dumps(challenges, indent=2))
    elif cmd == "academy":
        paths = lp.search_learning_paths("")
        print(json.dumps([{"id": p["id"], "title": p["title"], "courses": len(p["courses"])} for p in paths], indent=2))
    elif cmd == "paths":
        path_id = getattr(args, "path_id", "") or args.id
        if path_id:
            progress = lp.get_path_progress("current-user", path_id)
            print(json.dumps(progress, indent=2))
        else:
            paths = lp.search_learning_paths("")
            print(json.dumps([{"id": p["id"], "title": p["title"]} for p in paths], indent=2))
    elif cmd == "achievements":
        achievements = lp.get_user_achievements("current-user")
        print(json.dumps(achievements, indent=2))
    elif cmd == "assignments":
        name = getattr(args, "name", "") or args.id
        if name:
            assignments = lp.list_assignments("current-user")
            print(json.dumps([a for a in assignments if name in a.get("title", "")], indent=2))
        else:
            assignments = lp.list_assignments("current-user")
            print(json.dumps(assignments, indent=2))
    return 0


def _cmd_certify(args: argparse.Namespace) -> int:
    cp = CertificationProgramme()
    cmd = args.command
    if cmd == "list":
        certs = cp.list_certifications()
        print(json.dumps([{"id": c.id, "title": c.title, "level": c.level.value} for c in certs], indent=2))
    elif cmd == "info":
        cert = cp.get_certification(args.id) if args.id else None
        if cert:
            print(json.dumps({"id": cert.id, "title": cert.title, "description": cert.description, "skills": cert.skills}, indent=2))
        else:
            print(json.dumps({"error": "Certification not found"}))
    elif cmd == "exam":
        exam = cp.get_exam(args.id) if args.id else None
        if exam:
            print(json.dumps({"id": exam.id, "title": exam.title, "duration": exam.duration_minutes, "questions_count": len(exam.questions)}, indent=2))
    elif cmd == "verify":
        valid = cp.verify_certificate("current-user", args.id) if args.id else False
        print(json.dumps({"certification_id": args.id, "valid": valid}))
    return 0


def _cmd_profile(args: argparse.Namespace) -> int:
    cmd = args.command
    if cmd == "show":
        print(json.dumps({
            "username": "developer",
            "display_name": "I Developer",
            "role": "developer",
            "tier": "free",
            "badges": [],
            "stats": {"packages": 0, "projects": 0, "contributions": 0},
        }, indent=2))
    elif cmd == "badges":
        print(json.dumps([], indent=2))
    return 0


def _cmd_community(args: argparse.Namespace) -> int:
    cp = CommunityPlatform()
    cmd = args.command
    if cmd == "events":
        events = cp.list_events()
        print(json.dumps([{"id": e.id, "title": e.title, "type": e.type.value} for e in events], indent=2))
    elif cmd == "forums":
        print(json.dumps({"message": "Forums available at https://i-lang.org/community"}))
    elif cmd == "mentorship":
        match = cp.request_mentorship("mentor", "current-user")
        print(json.dumps(match, indent=2))
    elif cmd == "rfc":
        rfc = cp.submit_rfc("New Feature", "Description", "current-user")
        print(json.dumps(rfc, indent=2))
    return 0


def _cmd_enterprise(args: argparse.Namespace) -> int:
    ep = EnterprisePlatform()
    cmd = args.command
    if cmd == "plans":
        plans = ep.get_plans()
        print(json.dumps([{"id": p.id, "name": p.name, "price": p.price_monthly, "features": p.features} for p in plans], indent=2))
    elif cmd == "subscribe":
        ep.subscribe("my-org", "team")
        print(json.dumps({"status": "ok", "plan": "team"}))
    elif cmd == "ticket":
        from .ibikoreshingiro import SupportTicket
        ticket = SupportTicket(user_id="current-user", subject="Support request", description="")
        tid = ep.create_ticket(ticket)
        print(json.dumps({"status": "ok", "ticket_id": tid}))
    elif cmd == "advisories":
        advisories = ep.get_security_advisories()
        print(json.dumps(advisories, indent=2))
    return 0


def _cmd_research(args: argparse.Namespace) -> int:
    rp = ResearchPlatform()
    cmd = args.command
    if cmd == "papers":
        papers = rp.search_papers("")
        print(json.dumps([{"id": p.id, "title": p.title, "category": p.category} for p in papers], indent=2))
    elif cmd == "benchmarks":
        benchmarks = rp.get_benchmarks()
        print(json.dumps(benchmarks, indent=2))
    elif cmd == "partnerships":
        partnerships = rp.get_partnerships()
        print(json.dumps(partnerships, indent=2))
    elif cmd == "groups":
        group_id = getattr(args, "id", "") or getattr(args, "name", "")
        if group_id:
            network = rp.get_collaboration_network(group_id)
            print(json.dumps(network, indent=2))
        else:
            print(json.dumps({"message": "Use --id or --name to specify a research group"}))
    return 0


def _cmd_security(args: argparse.Namespace) -> int:
    sm = SecurityManager()
    cmd = args.command
    if cmd == "audit":
        logs = sm.get_audit_log()
        print(json.dumps([{"id": a.id, "target": a.target, "severity": a.severity.value, "description": a.description} for a in logs], indent=2))
    elif cmd == "mfa":
        sm.enable_mfa("current-user")
        print(json.dumps({"status": "ok", "message": "MFA enabled"}))
    elif cmd == "keys":
        key_info = sm.create_api_key("current-user", "CLI Key", ["read", "write"])
        print(json.dumps({"status": "ok", "key": key_info["key"], "name": key_info["name"]}))
    return 0


def _cmd_analytics(args: argparse.Namespace) -> int:
    ae = AnalyticsEngine()
    cmd = args.command
    if cmd == "metrics":
        dashboards = ae.get_performance_dashboards()
        print(json.dumps(dashboards, indent=2))
    elif cmd == "downloads":
        metrics = ae.get_download_metrics()
        print(json.dumps(metrics, indent=2))
    elif cmd == "growth":
        growth = ae.get_community_growth_metrics()
        print(json.dumps(growth, indent=2))
    elif cmd == "docs-usage":
        popular = ae.get_popular_docs()
        print(json.dumps(popular, indent=2))
    return 0


def _cmd_global(args: argparse.Namespace) -> int:
    gm = GlobalisationManager()
    cmd = args.command
    if cmd == "locales":
        locales = gm.get_supported_locales()
        print(json.dumps(locales, indent=2))
    elif cmd == "mirrors":
        mirrors = gm.get_mirrors()
        print(json.dumps(mirrors, indent=2))
    elif cmd == "translate":
        gm.add_translation("fr", "welcome", "Bienvenue")
        print(json.dumps({"status": "ok", "locale": "fr"}))
    return 0


def _cmd_website(args: argparse.Namespace) -> int:
    wm = WebsiteManager()
    cmd = args.command
    if cmd == "news":
        news = wm.get_news()
        print(json.dumps(news, indent=2))
    elif cmd == "releases":
        releases = wm.get_releases()
        print(json.dumps(releases, indent=2))
    elif cmd == "showcase":
        showcases = wm.get_showcases()
        print(json.dumps(showcases, indent=2))
    elif cmd == "roadmap":
        roadmap = wm.get_roadmap()
        print(json.dumps(roadmap, indent=2))
    elif cmd == "stats":
        stats = wm.get_stats()
        print(json.dumps(stats, indent=2))
    elif cmd == "download":
        info = wm.get_download_info()
        print(json.dumps(info, indent=2))
    return 0


def _cmd_package(args: argparse.Namespace) -> int:
    registry = PackageRegistry()
    cmd = args.command
    name = args.name
    if cmd == "info":
        pkg = registry.get_package(name)
        if pkg:
            print(json.dumps({"name": pkg.name, "version": pkg.version, "description": pkg.description, "author": pkg.author_name, "verified": pkg.verified}, indent=2))
        else:
            print(json.dumps({"error": "Package not found"}))
    elif cmd == "stats":
        stats = registry.get_stats(name)
        if stats:
            print(json.dumps({"name": stats.name, "downloads": stats.total_downloads, "versions": stats.versions_count, "score": stats.score}, indent=2))
    elif cmd == "versions":
        pkg = registry.get_package(name)
        if pkg:
            version = getattr(args, "version", "")
            v = registry.get_version(name, version) if version else None
            print(json.dumps({"versions": [{"version": pkg.version, "downloads": 0}]}))
    elif cmd == "yank":
        version = getattr(args, "version", "")
        if version:
            registry.yank_version(name, version)
            print(json.dumps({"status": "ok", "yanked": f"{name}@{version}"}))
    elif cmd == "verify":
        verified = registry.is_verified_publisher(name)
        print(json.dumps({"name": name, "verified": verified}))
    return 0


def _cmd_foundation(args: argparse.Namespace) -> int:
    fnd = Foundation()
    cmd = args.command
    if cmd == "info":
        print(json.dumps({"name": "I Foundation", "mission": fnd.FOUNDATION_CHARTER["mission"], "values": fnd.FOUNDATION_CHARTER["values"]}, indent=2))
    elif cmd == "members":
        members = fnd.list_members()
        print(json.dumps(members, indent=2))
    elif cmd == "board":
        board = fnd.get_board()
        print(json.dumps([{"name": m.get("name", ""), "role": m.get("role", "")} for m in board], indent=2))
    elif cmd == "policies":
        policies = fnd.get_policies()
        print(json.dumps(policies, indent=2))
    elif cmd == "charter":
        print(json.dumps(fnd.FOUNDATION_CHARTER, indent=2))
    return 0


def _cmd_labs(args: argparse.Namespace) -> int:
    labs = Labs()
    cmd = args.command
    if cmd == "list":
        templates = labs.list_lab_templates()
        print(json.dumps([{"id": t["id"], "title": t["title"], "domain": t.get("domain", "")} for t in templates], indent=2))
    elif cmd == "start":
        lab_id = getattr(args, "id", "")
        if lab_id:
            instance = labs.start_lab(lab_id)
            print(json.dumps({"status": "running", "lab_id": lab_id, "instance_id": instance.get("instance_id", "")}, indent=2))
        else:
            print(json.dumps({"error": "Missing lab ID"}))
    elif cmd == "progress":
        lab_id = getattr(args, "id", "")
        if lab_id:
            progress = labs.get_lab_progress(lab_id)
            print(json.dumps(progress, indent=2))
    elif cmd == "steps":
        step = getattr(args, "step", "")
        lab_id = getattr(args, "id", "")
        if step and lab_id:
            valid = labs.validate_step(lab_id, step)
            print(json.dumps({"lab_id": lab_id, "step": step, "valid": valid}))
        else:
            print(json.dumps({"message": "Use --step and id to validate a step"}))
    return 0


def _cmd_scholarships(args: argparse.Namespace) -> int:
    sch = Scholarships()
    cmd = args.command
    if cmd == "list":
        all_sch = sch.list_scholarships()
        print(json.dumps(all_sch, indent=2))
    elif cmd == "apply":
        name = getattr(args, "name", "") or getattr(args, "id", "")
        proposal = getattr(args, "proposal", "")
        if name and proposal:
            app = sch.apply(name, "current-user", proposal)
            print(json.dumps({"status": "submitted", "application_id": app.get("id", "")}, indent=2))
        else:
            print(json.dumps({"error": "Need --name and --proposal"}))
    elif cmd == "status":
        applicant = getattr(args, "applicant", "") or "current-user"
        dashboard = sch.get_applicant_dashboard(applicant)
        print(json.dumps(dashboard, indent=2))
    elif cmd == "award":
        app_id = getattr(args, "id", "")
        if app_id:
            result = sch.award_scholarship(app_id)
            print(json.dumps({"status": "awarded", "result": result}, indent=2))
    return 0


def _cmd_conference(args: argparse.Namespace) -> int:
    conf = GlobalConference()
    cmd = args.command
    if cmd == "info":
        print(json.dumps({"name": "I Global Conference", "status": "active", "cfp_open": True}, indent=2))
    elif cmd == "sessions":
        title = getattr(args, "session_title", "")
        if title:
            sessions = conf.search_sessions(title)
            print(json.dumps(sessions, indent=2))
        else:
            schedule = conf.get_conference_schedule()
            print(json.dumps(schedule, indent=2))
    elif cmd == "speakers":
        speaker = getattr(args, "speaker", "")
        if speaker:
            sessions = conf.list_speaker_sessions(speaker)
            print(json.dumps(sessions, indent=2))
        else:
            print(json.dumps({"message": "Use --speaker to list sessions by speaker"}))
    elif cmd == "sponsors":
        sponsors = conf.list_sponsors()
        print(json.dumps(sponsors, indent=2))
    elif cmd == "cfp":
        if conf.is_cfp_open():
            print(json.dumps({"cfp": "open", "message": "Submit proposals with --session-title"}))
        else:
            print(json.dumps({"cfp": "closed"}))
    elif cmd == "schedule":
        schedule = conf.get_conference_schedule()
        print(json.dumps(schedule, indent=2))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="idev", description="I Developer Platform CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {IDEVP_VERSION}")
    subparsers = parser.add_subparsers(dest="command")
    register_subcommands(subparsers)
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    return genda(args)


if __name__ == "__main__":
    sys.exit(main())
