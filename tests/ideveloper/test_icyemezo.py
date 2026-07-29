"""Tests for isoko.ideveloper.icyemezo — Certification Programme."""

from __future__ import annotations

from isoko.ideveloper.icyemezo import CertificationProgramme


def test_certification_init():
    cp = CertificationProgramme()
    certs = cp.list_certifications()
    assert len(certs) == 8


def test_get_certification():
    cp = CertificationProgramme()
    cert = cp.get_certification("i-certified-developer")
    assert cert is not None
    assert cert.title == "I Certified Developer"


def test_get_exam():
    cp = CertificationProgramme()
    cert = cp.get_certification("i-certified-developer")
    assert cert is not None and cert.exam is not None
    exam = cp.get_exam(cert.exam.id)
    assert exam is not None
    assert exam.passing_score == 70


def test_take_exam_pass():
    cp = CertificationProgramme()
    cert = cp.get_certification("i-certified-developer")
    assert cert is not None and cert.exam is not None
    answers = {q["id"]: q["answer"] for q in cert.exam.questions}
    result = cp.take_exam("user1", cert.exam.id, answers)
    assert result["passed"] is True
    assert result["score"] >= 70


def test_take_exam_fail():
    cp = CertificationProgramme()
    cert = cp.get_certification("i-certified-architect")
    assert cert is not None and cert.exam is not None
    answers = {q["id"]: "wrong" for q in cert.exam.questions}
    result = cp.take_exam("user1", cert.exam.id, answers)
    assert result["passed"] is False


def test_issue_certificate():
    cp = CertificationProgramme()
    issued = cp.issue_certificate("user1", "i-certified-developer")
    assert issued is not None
    assert issued["title"] == "I Certified Developer"


def test_get_user_certifications():
    cp = CertificationProgramme()
    cp.issue_certificate("user1", "i-certified-web-developer")
    certs = cp.get_user_certifications("user1")
    assert len(certs) >= 1


def test_verify_certificate():
    cp = CertificationProgramme()
    cp.issue_certificate("user2", "i-certified-developer")
    assert cp.verify_certificate("user2", "i-certified-developer") is True
    assert cp.verify_certificate("user2", "i-certified-architect") is False


def test_exam_not_found():
    cp = CertificationProgramme()
    result = cp.take_exam("user1", "nonexistent", {})
    assert result["passed"] is False
    assert "error" in result


def test_all_certifications_have_exams():
    cp = CertificationProgramme()
    for cert in cp.list_certifications():
        assert cert.exam is not None, f"{cert.id} missing exam"
        assert len(cert.exam.questions) > 0, f"{cert.id} has no questions"
