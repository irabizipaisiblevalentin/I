"""Tests for urubuga validation system."""

import pytest
from urubuga.validation import (
    Schema, Field, ValidationResult, ValidationError,
    required, email, url, min_length, max_length, one_of,
)


class TestSchema:
    def test_valid_data(self):
        schema = Schema("user", [
            Field("name", required=True),
            Field("age", field_type="integer", required=False),
        ])
        result = schema.validate({"name": "Alice", "age": 25})
        assert result.is_valid
        assert result.data["name"] == "Alice"

    def test_missing_required(self):
        schema = Schema("user", [Field("name", required=True)])
        result = schema.validate({})
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "required"

    def test_optional_field(self):
        schema = Schema("user", [Field("name", required=False)])
        result = schema.validate({})
        assert result.is_valid

    def test_type_validation(self):
        schema = Schema("s", [Field("count", field_type="integer")])
        result = schema.validate({"count": "not_int"})
        assert not result.is_valid

    def test_min_length(self):
        schema = Schema("s", [
            Field("name", min_length=3)])
        result = schema.validate({"name": "ab"})
        assert not result.is_valid

    def test_max_length(self):
        schema = Schema("s", [
            Field("name", max_length=5)])
        result = schema.validate({"name": "toolongname"})
        assert not result.is_valid

    def test_pattern(self):
        schema = Schema("s", [
            Field("code", pattern=r"^[A-Z]{3}$")])
        assert schema.validate({"code": "ABC"}).is_valid
        assert not schema.validate({"code": "ab"}).is_valid

    def test_choices(self):
        schema = Schema("s", [
            Field("color", choices=["red", "green", "blue"])])
        assert schema.validate({"color": "red"}).is_valid
        assert not schema.validate({"color": "yellow"}).is_valid

    def test_min_value(self):
        schema = Schema("s", [
            Field("age", field_type="integer", min_value=0)])
        assert schema.validate({"age": 5}).is_valid
        assert not schema.validate({"age": -1}).is_valid

    def test_max_value(self):
        schema = Schema("s", [
            Field("score", field_type="float", max_value=100)])
        assert schema.validate({"score": 50}).is_valid
        assert not schema.validate({"score": 150}).is_valid

    def test_default_value(self):
        schema = Schema("s", [
            Field("role", required=False, default="user")])
        result = schema.validate({})
        assert result.data["role"] == "user"

    def test_custom_validator(self):
        def even_only(value):
            if value % 2 != 0:
                return "Must be even"
            return None
        schema = Schema("s", [
            Field("number", field_type="integer", custom=even_only)])
        assert schema.validate({"number": 4}).is_valid
        assert not schema.validate({"number": 3}).is_valid

    def test_multiple_errors(self):
        schema = Schema("s", [
            Field("name", required=True),
            Field("email", required=True),
        ])
        result = schema.validate({})
        assert not result.is_valid
        assert len(result.errors) == 2

    def test_add_field(self):
        schema = Schema("s")
        schema.add_field(Field("name", required=True))
        result = schema.validate({"name": "test"})
        assert result.is_valid

    def test_field_method(self):
        schema = Schema("s")
        schema.field("name", required=True)
        result = schema.validate({"name": "test"})
        assert result.is_valid


class TestValidators:
    def test_required(self):
        assert required("value") is None
        assert required("") is not None
        assert required(0) is None

    def test_email(self):
        assert email("test@example.com") is None
        assert email("invalid") is not None

    def test_url(self):
        assert url("https://example.com") is None
        assert url("not-a-url") is not None

    def test_min_length(self):
        v = min_length(3)
        assert v("hello") is None
        assert v("ab") is not None

    def test_max_length(self):
        v = max_length(5)
        assert v("hello") is None
        assert v("toolong") is not None

    def test_one_of(self):
        v = one_of(["a", "b", "c"])
        assert v("a") is None
        assert v("d") is not None


class TestValidationResult:
    def test_to_dict(self):
        r = ValidationResult(is_valid=False)
        r.add_error("name", "required")
        d = r.to_dict()
        assert not d["is_valid"]
        assert len(d["errors"]) == 1
