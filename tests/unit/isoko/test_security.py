"""Tests for isoko security module."""

import pytest
from isoko.security import (
    sha256, sha512, checksum_file, verify_checksum,
    IntegritySet, SBOM, SBOMEntry, AuditReport, AuditFinding,
    TrustedPublishers,
)


class TestChecksums:
    def test_sha256(self):
        data = b"hello world"
        result = sha256(data)
        assert len(result) == 64
        assert isinstance(result, str)

    def test_sha512(self):
        data = b"hello world"
        result = sha512(data)
        assert len(result) == 128

    def test_verify_checksum(self):
        data = b"test data"
        expected = sha256(data)
        assert verify_checksum(data, expected)
        assert not verify_checksum(data, "wrong checksum")

    def test_verify_checksum_sha512(self):
        data = b"test data"
        expected = sha512(data)
        assert verify_checksum(data, expected, "sha512")

    def test_deterministic(self):
        assert sha256(b"test") == sha256(b"test")
        assert sha256(b"test") != sha256(b"other")


class TestIntegritySet:
    def test_add_verify(self):
        data = b"test data"
        s = IntegritySet()
        s.add("sha256", sha256(data))
        ok, algo = s.verify(data)
        assert ok
        assert algo == "sha256"

    def test_verify_multiple(self):
        data = b"test data"
        s = IntegritySet()
        s.add("sha256", sha256(data))
        s.add("sha512", sha512(data))
        ok, algo = s.verify(data)
        assert ok

    def test_verify_failure(self):
        s = IntegritySet()
        s.add("sha256", "wrong")
        ok, _ = s.verify(b"data")
        assert not ok

    def test_to_dict(self):
        s = IntegritySet()
        s.add("sha256", "abc")
        d = s.to_dict()
        assert d["sha256"] == "abc"

    def test_from_dict(self):
        s = IntegritySet.from_dict({"sha256": "abc", "sha512": "def"})
        assert s.to_dict()["sha256"] == "abc"
        assert s.to_dict()["sha512"] == "def"


class TestSBOM:
    def test_basic(self):
        sbom = SBOM("project", "1.0.0")
        sbom.add(SBOMEntry(name="dep1", version="1.0.0"))
        d = sbom.to_dict()
        assert d["project"]["name"] == "project"
        assert len(d["components"]) == 1

    def test_to_json(self):
        sbom = SBOM("project", "1.0.0")
        sbom.add(SBOMEntry(name="dep1", version="1.0.0", license="MIT"))
        j = sbom.to_json()
        assert "project" in j
        assert "dep1" in j

    def test_sbom_entry(self):
        e = SBOMEntry(
            name="test",
            version="1.0.0",
            license="MIT",
            checksum="abc123",
            source="registry",
            dependencies=["dep1"],
        )
        d = e.to_dict()
        assert d["name"] == "test"
        assert d["license"] == "MIT"
        assert d["dependencies"] == ["dep1"]


class TestAuditReport:
    def test_clean(self):
        report = AuditReport()
        report.total_packages = 10
        assert report.is_clean

    def test_with_findings(self):
        report = AuditReport()
        report.add_finding(AuditFinding(
            severity="high",
            package="vuln-pkg",
            version="1.0.0",
            title="Test vulnerability",
        ))
        assert not report.is_clean
        assert report.vulnerable_count == 1

    def test_low_severity_not_counted(self):
        report = AuditReport()
        report.add_finding(AuditFinding(severity="info"))
        report.add_finding(AuditFinding(severity="low"))
        assert report.vulnerable_count == 0
        assert report.is_clean

    def test_medium_counted(self):
        report = AuditReport()
        report.add_finding(AuditFinding(severity="medium"))
        assert report.vulnerable_count == 1

    def test_critical_counted(self):
        report = AuditReport()
        report.add_finding(AuditFinding(severity="critical"))
        assert report.vulnerable_count == 1

    def test_to_dict(self):
        report = AuditReport()
        report.total_packages = 5
        report.add_finding(AuditFinding(
            severity="high",
            package="x",
            version="1.0",
            title="test",
            description="desc",
            recommendation="fix it",
        ))
        d = report.to_dict()
        assert d["totalPackages"] == 5
        assert d["vulnerablePackages"] == 1
        assert len(d["findings"]) == 1


class TestTrustedPublishers:
    def test_no_restriction(self):
        tp = TrustedPublishers()
        assert tp.is_trusted("any-pkg", "anyone")

    def test_trusted(self):
        tp = TrustedPublishers()
        tp.add_trusted("my-pkg", "trusted-publisher")
        assert tp.is_trusted("my-pkg", "trusted-publisher")
        assert not tp.is_trusted("my-pkg", "untrusted")

    def test_to_dict(self):
        tp = TrustedPublishers()
        tp.add_trusted("pkg", "pub1")
        tp.add_trusted("pkg", "pub2")
        d = tp.to_dict()
        assert "pub1" in d["pkg"]
        assert "pub2" in d["pkg"]

    def test_from_dict(self):
        tp = TrustedPublishers.from_dict({"pkg": ["pub1"]})
        assert tp.is_trusted("pkg", "pub1")
        assert not tp.is_trusted("pkg", "other")
