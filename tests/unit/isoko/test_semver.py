"""Tests for isoko semver module."""

import pytest
from isoko.semver import Version, Range, parse_version, parse_range, max_satisfying, min_satisfying, sort_versions


class TestVersion:
    def test_parse_basic(self):
        v = Version.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease is None
        assert v.build is None

    def test_parse_prerelease(self):
        v = Version.parse("1.0.0-alpha.1")
        assert v.major == 1
        assert v.prerelease == "alpha.1"

    def test_parse_build(self):
        v = Version.parse("1.0.0+build.42")
        assert v.build == "build.42"

    def test_parse_full(self):
        v = Version.parse("1.2.3-beta.1+build.42")
        assert v.prerelease == "beta.1"
        assert v.build == "build.42"

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            Version.parse("not-a-version")
        with pytest.raises(ValueError):
            Version.parse("1.2")
        with pytest.raises(ValueError):
            Version.parse("1.2.3.4")

    def test_try_parse(self):
        assert Version.try_parse("1.2.3") is not None
        assert Version.try_parse("invalid") is None

    def test_str(self):
        assert str(Version.parse("1.2.3")) == "1.2.3"
        assert str(Version.parse("1.0.0-alpha")) == "1.0.0-alpha"
        assert str(Version.parse("1.0.0+build")) == "1.0.0+build"
        assert str(Version.parse("1.0.0-alpha+build")) == "1.0.0-alpha+build"

    def test_eq(self):
        assert Version(1, 2, 3) == Version(1, 2, 3)
        assert Version(1, 2, 3) != Version(1, 2, 4)
        assert Version(1, 2, 3) != "1.2.3"

    def test_lt(self):
        assert Version(1, 0, 0) < Version(2, 0, 0)
        assert Version(1, 0, 0) < Version(1, 1, 0)
        assert Version(1, 0, 0) < Version(1, 0, 1)
        assert not Version(1, 0, 0) < Version(1, 0, 0)

    def test_le(self):
        assert Version(1, 0, 0) <= Version(1, 0, 0)
        assert Version(1, 0, 0) <= Version(1, 0, 1)
        assert not Version(1, 0, 1) <= Version(1, 0, 0)

    def test_gt(self):
        assert Version(2, 0, 0) > Version(1, 0, 0)
        assert not Version(1, 0, 0) > Version(1, 0, 0)

    def test_ge(self):
        assert Version(1, 0, 0) >= Version(1, 0, 0)
        assert Version(1, 0, 1) >= Version(1, 0, 0)
        assert not Version(1, 0, 0) >= Version(1, 0, 1)

    def test_hash(self):
        s = {Version(1, 0, 0), Version(1, 0, 0), Version(2, 0, 0)}
        assert len(s) == 2

    def test_prerelease_ordering(self):
        alpha = Version.parse("1.0.0-alpha")
        beta = Version.parse("1.0.0-beta")
        stable = Version.parse("1.0.0")
        assert alpha < beta < stable

    def test_tuple(self):
        assert Version(1, 2, 3).tuple == (1, 2, 3)

    def test_is_prerelease(self):
        assert Version.parse("1.0.0-alpha").is_prerelease
        assert not Version.parse("1.0.0").is_prerelease


class TestRange:
    def test_exact(self):
        r = Range("1.2.3")
        assert r.satisfies(Version.parse("1.2.3"))
        assert not r.satisfies(Version.parse("1.2.4"))

    def test_caret(self):
        r = Range("^1.2.3")
        assert r.satisfies(Version.parse("1.2.3"))
        assert r.satisfies(Version.parse("1.9.9"))
        assert not r.satisfies(Version.parse("2.0.0"))
        assert not r.satisfies(Version.parse("1.2.2"))

    def test_caret_zero(self):
        r = Range("^0.1.0")
        assert r.satisfies(Version.parse("0.1.0"))
        assert r.satisfies(Version.parse("0.1.5"))
        assert not r.satisfies(Version.parse("0.2.0"))

    def test_caret_zero_patch(self):
        r = Range("^0.0.3")
        assert r.satisfies(Version.parse("0.0.3"))
        assert not r.satisfies(Version.parse("0.0.4"))

    def test_tilde(self):
        r = Range("~1.2.3")
        assert r.satisfies(Version.parse("1.2.3"))
        assert r.satisfies(Version.parse("1.2.9"))
        assert not r.satisfies(Version.parse("1.3.0"))
        assert not r.satisfies(Version.parse("1.2.2"))

    def test_wildcard(self):
        r = Range("*")
        assert r.satisfies(Version.parse("0.0.1"))
        assert r.satisfies(Version.parse("999.999.999"))

    def test_gte(self):
        r = Range(">=1.0.0")
        assert r.satisfies(Version.parse("1.0.0"))
        assert r.satisfies(Version.parse("2.0.0"))
        assert not r.satisfies(Version.parse("0.9.9"))

    def test_lte(self):
        r = Range("<=2.0.0")
        assert r.satisfies(Version.parse("2.0.0"))
        assert r.satisfies(Version.parse("1.0.0"))
        assert not r.satisfies(Version.parse("2.0.1"))

    def test_gt(self):
        r = Range(">1.0.0")
        assert r.satisfies(Version.parse("1.0.1"))
        assert not r.satisfies(Version.parse("1.0.0"))

    def test_lt(self):
        r = Range("<2.0.0")
        assert r.satisfies(Version.parse("1.9.9"))
        assert not r.satisfies(Version.parse("2.0.0"))

    def test_eq(self):
        r = Range("=1.0.0")
        assert r.satisfies(Version.parse("1.0.0"))
        assert not r.satisfies(Version.parse("1.0.1"))

    def test_neq(self):
        r = Range("!=1.0.0")
        assert not r.satisfies(Version.parse("1.0.0"))
        assert r.satisfies(Version.parse("1.0.1"))

    def test_space_separated(self):
        r = Range(">=1.0.0 <2.0.0")
        assert r.satisfies(Version.parse("1.5.0"))
        assert not r.satisfies(Version.parse("2.0.0"))
        assert not r.satisfies(Version.parse("0.9.0"))

    def test_comma_separated(self):
        r = Range(">=1.0.0,<2.0.0")
        assert r.satisfies(Version.parse("1.5.0"))
        assert not r.satisfies(Version.parse("2.0.0"))

    def test_empty_range(self):
        r = Range("")
        assert r.satisfies(Version.parse("1.0.0"))

    def test_x_range(self):
        r = Range("1.x")
        assert r.satisfies(Version.parse("1.0.0"))
        assert r.satisfies(Version.parse("1.9.9"))
        assert not r.satisfies(Version.parse("2.0.0"))

    def test_x_range_patch(self):
        r = Range("1.2.*")
        assert r.satisfies(Version.parse("1.2.0"))
        assert r.satisfies(Version.parse("1.2.9"))
        assert not r.satisfies(Version.parse("1.3.0"))


class TestHelpers:
    def test_max_satisfying(self):
        versions = [
            Version.parse("1.0.0"),
            Version.parse("1.1.0"),
            Version.parse("1.2.0"),
            Version.parse("2.0.0"),
        ]
        assert max_satisfying(versions, "^1.0.0") == Version.parse("1.2.0")
        assert max_satisfying(versions, ">=2.0.0") == Version.parse("2.0.0")
        assert max_satisfying(versions, "<1.0.0") is None

    def test_min_satisfying(self):
        versions = [
            Version.parse("1.0.0"),
            Version.parse("1.1.0"),
            Version.parse("1.2.0"),
        ]
        assert min_satisfying(versions, ">=1.0.0") == Version.parse("1.0.0")
        assert min_satisfying(versions, ">1.0.0") == Version.parse("1.1.0")

    def test_sort_versions(self):
        versions = [
            Version.parse("2.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.5.0"),
        ]
        sorted_asc = sort_versions(versions)
        assert sorted_asc == [Version.parse("1.0.0"), Version.parse("1.5.0"), Version.parse("2.0.0")]

        sorted_desc = sort_versions(versions, descending=True)
        assert sorted_desc == [Version.parse("2.0.0"), Version.parse("1.5.0"), Version.parse("1.0.0")]

    def test_parse_version(self):
        v = parse_version("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_range(self):
        r = parse_range("^1.0.0")
        assert r.satisfies(Version.parse("1.5.0"))
