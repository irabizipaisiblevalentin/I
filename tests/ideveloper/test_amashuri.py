"""Tests for isoko.ideveloper.amashuri — Learning Platform."""

from __future__ import annotations

from isoko.ideveloper.amashuri import LearningPlatform
from isoko.ideveloper.ibikoreshingiro import Course, CourseLevel, Lesson, Module


def test_learning_init():
    lp = LearningPlatform()
    assert lp.search_courses("") == []


def test_add_course():
    lp = LearningPlatform()
    course = Course(title="I 101", description="Introduction to I", level=CourseLevel.BEGINNER)
    cid = lp.add_course(course)
    assert cid is not None
    assert lp.get_course(cid) is not None


def test_search_courses():
    lp = LearningPlatform()
    lp.add_course(Course(title="Web Dev", description="Build websites", tags=["web"]))
    lp.add_course(Course(title="AI Basics", description="Machine learning", tags=["ai"]))
    results = lp.search_courses("web")
    assert len(results) == 1
    assert results[0].title == "Web Dev"


def test_enroll():
    lp = LearningPlatform()
    cid = lp.add_course(Course(title="Test Course"))
    assert lp.enroll("user1", cid) is True
    assert lp.enroll("user1", "nonexistent") is False


def test_progress():
    lp = LearningPlatform()
    lesson = Lesson(id="l1", title="Intro")
    module = Module(id="m1", title="Module 1", lessons=[lesson])
    cid = lp.add_course(Course(title="Course", modules=[module]))
    lp.enroll("user1", cid)
    lp.update_progress("user1", cid, "l1", 0.5)
    assert lp.get_progress("user1", cid) == 0.5
    lp.update_progress("user1", cid, "l1", 1.0)
    assert lp.get_progress("user1", cid) == 1.0


def test_playground():
    lp = LearningPlatform()
    session = lp.create_playground_session("function main() {}", "i")
    assert session["language"] == "i"
    assert session["code"] == "function main() {}"


def test_challenges():
    lp = LearningPlatform()
    lp.add_challenge("Hello World", "Print hello world", "easy")
    lp.add_challenge("FizzBuzz", "Solve fizzbuzz", "medium")
    assert len(lp.get_challenges("easy")) == 1
    assert len(lp.get_challenges()) == 2


def test_teacher_resources():
    lp = LearningPlatform()
    r = lp.add_teacher_resource("Lesson Plan 1", "pdf", "Content")
    assert r["type"] == "pdf"


def test_university_curriculum():
    lp = LearningPlatform()
    curr = lp.add_university_curriculum("CS 101", ["I 101", "I 102"], credits=6)
    assert curr["credits"] == 6


def test_get_enrolled_courses():
    lp = LearningPlatform()
    cid = lp.add_course(Course(title="My Course"))
    lp.enroll("user1", cid)
    courses = lp.get_enrolled_courses("user1")
    assert len(courses) == 1
    assert courses[0].title == "My Course"
