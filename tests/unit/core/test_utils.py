"""
Tests for core utility functions.
"""


from src.compiler.core.utils import (
    camel_to_snake,
    chunks,
    clamp,
    find,
    find_index,
    flatten,
    format_bytes,
    format_duration,
    group_by,
    merge_dicts,
    partition,
    pluralize,
    snake_to_camel,
    unique,
)


class TestClamp:
    """Tests for clamp."""

    def test_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_below_min(self):
        assert clamp(-1, 0, 10) == 0

    def test_above_max(self):
        assert clamp(15, 0, 10) == 10

    def test_equal_min(self):
        assert clamp(0, 0, 10) == 0

    def test_equal_max(self):
        assert clamp(10, 0, 10) == 10


class TestGroupBy:
    """Tests for group_by."""

    def test_group_by_length(self):
        items = ["a", "bb", "cc", "ddd"]
        result = group_by(items, len)
        assert result[1] == ["a"]
        assert result[2] == ["bb", "cc"]
        assert result[3] == ["ddd"]

    def test_empty(self):
        assert group_by([], len) == {}


class TestUnique:
    """Tests for unique."""

    def test_no_duplicates(self):
        assert unique([1, 2, 3]) == [1, 2, 3]

    def test_with_duplicates(self):
        assert unique([1, 2, 2, 3, 1, 3]) == [1, 2, 3]

    def test_empty(self):
        assert unique([]) == []


class TestFlatten:
    """Tests for flatten."""

    def test_basic(self):
        assert flatten([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]

    def test_empty(self):
        assert flatten([[], [], []]) == []

    def test_single(self):
        assert flatten([[1]]) == [1]


class TestChunks:
    """Tests for chunks."""

    def test_exact(self):
        assert list(chunks([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]

    def test_remainder(self):
        assert list(chunks([1, 2, 3], 2)) == [[1, 2], [3]]

    def test_single_chunk(self):
        assert list(chunks([1, 2], 5)) == [[1, 2]]

    def test_empty(self):
        assert list(chunks([], 3)) == []


class TestFind:
    """Tests for find."""

    def test_found(self):
        result = find([1, 2, 3, 4], lambda x: x > 2)
        assert result == 3

    def test_not_found(self):
        result = find([1, 2], lambda x: x > 5)
        assert result is None

    def test_empty(self):
        result = find([], lambda x: True)
        assert result is None


class TestFindIndex:
    """Tests for find_index."""

    def test_found(self):
        assert find_index([10, 20, 30], lambda x: x == 20) == 1

    def test_not_found(self):
        assert find_index([10, 20], lambda x: x == 99) == -1

    def test_first_match(self):
        assert find_index([1, 2, 2, 3], lambda x: x == 2) == 1


class TestPartition:
    """Tests for partition."""

    def test_basic(self):
        evens, odds = partition([1, 2, 3, 4], lambda x: x % 2 == 0)
        assert evens == [2, 4]
        assert odds == [1, 3]

    def test_all_match(self):
        evens, odds = partition([2, 4, 6], lambda x: x % 2 == 0)
        assert evens == [2, 4, 6]
        assert odds == []

    def test_none_match(self):
        evens, odds = partition([1, 3, 5], lambda x: x % 2 == 0)
        assert evens == []
        assert odds == [1, 3, 5]


class TestMergeDicts:
    """Tests for merge_dicts."""

    def test_merge(self):
        result = merge_dicts({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_later_overrides(self):
        result = merge_dicts({"a": 1, "b": 2}, {"b": 3})
        assert result == {"a": 1, "b": 3}

    def test_empty(self):
        assert merge_dicts() == {}


class TestCamelToSnake:
    """Tests for camel_to_snake."""

    def test_simple(self):
        assert camel_to_snake("CamelCase") == "camel_case"

    def test_single_word(self):
        assert camel_to_snake("Hello") == "hello"

    def test_all_upper(self):
        assert camel_to_snake("XMLParser") == "xml_parser"


class TestSnakeToCamel:
    """Tests for snake_to_camel."""

    def test_simple(self):
        assert snake_to_camel("snake_case") == "SnakeCase"

    def test_single_word(self):
        assert snake_to_camel("hello") == "Hello"

    def test_multiple(self):
        assert snake_to_camel("xml_parser") == "XmlParser"


class TestPluralize:
    """Tests for pluralize."""

    def test_singular(self):
        assert pluralize(1, "item") == "item"

    def test_plural_default(self):
        assert pluralize(2, "item") == "items"

    def test_plural_custom(self):
        assert pluralize(3, "child", "children") == "children"

    def test_zero(self):
        assert pluralize(0, "item") == "items"


class TestFormatBytes:
    """Tests for format_bytes."""

    def test_bytes(self):
        assert format_bytes(500) == "500.0B"

    def test_kilobytes(self):
        assert format_bytes(2048) == "2.0KB"

    def test_megabytes(self):
        result = format_bytes(5 * 1024 * 1024)
        assert result == "5.0MB"


class TestFormatDuration:
    """Tests for format_duration."""

    def test_microseconds(self):
        result = format_duration(0.000001)
        assert "us" in result

    def test_milliseconds(self):
        result = format_duration(0.050)
        assert "ms" in result

    def test_seconds(self):
        assert "s" in format_duration(5.0)

    def test_minutes(self):
        result = format_duration(125.0)
        assert "m" in result
