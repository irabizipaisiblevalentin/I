"""Comprehensive tests for the I Standard Library (ISTDLIB) — Sprint 9."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


# ═══════════════════════════════════════════════════════════════
# Foundation modules
# ═══════════════════════════════════════════════════════════════

class TestText(unittest.TestCase):
    def test_case_conversion(self):
        from stdlib.text import to_upper, to_lower, to_title, to_case_fold
        self.assertEqual(to_upper("hello"), "HELLO")
        self.assertEqual(to_lower("HELLO"), "hello")
        self.assertEqual(to_title("hello world"), "Hello World")
        self.assertEqual(to_case_fold("STRASSE"), "strasse")

    def test_search(self):
        from stdlib.text import contains, starts_with, ends_with, find, count
        self.assertTrue(contains("hello world", "world"))
        self.assertFalse(contains("hello", "xyz"))
        self.assertTrue(starts_with("hello", "hel"))
        self.assertTrue(ends_with("hello", "llo"))
        self.assertEqual(find("hello", "ll"), 2)
        self.assertEqual(count("banana", "an"), 2)

    def test_split_join(self):
        from stdlib.text import split, join, lines
        self.assertEqual(split("a,b,c", ","), ["a", "b", "c"])
        self.assertEqual(split("hello world"), ["hello", "world"])
        self.assertEqual(join(["a", "b", "c"], ", "), "a, b, c")
        self.assertEqual(lines("a\nb\nc"), ["a", "b", "c"])

    def test_trim_pad(self):
        from stdlib.text import trim, ltrim, rtrim, pad_left, pad_right, pad_center
        self.assertEqual(trim("  hi  "), "hi")
        self.assertEqual(ltrim("  hi  "), "hi  ")
        self.assertEqual(rtrim("  hi  "), "  hi")
        self.assertEqual(pad_left("42", 5), "   42")
        self.assertEqual(pad_right("hi", 5), "hi   ")
        self.assertEqual(pad_center("hi", 6), "  hi  ")

    def test_replace(self):
        from stdlib.text import replace, reverse, repeat, truncate
        self.assertEqual(replace("hello", "l", "r"), "herro")
        self.assertEqual(reverse("abc"), "cba")
        self.assertEqual(repeat("ab", 3), "ababab")
        self.assertEqual(truncate("hello world", 8), "hello...")

    def test_validation(self):
        from stdlib.text import is_empty, is_numeric, is_alpha, is_alphanumeric
        self.assertTrue(is_empty(""))
        self.assertTrue(is_empty("   "))
        self.assertFalse(is_empty("hi"))
        self.assertTrue(is_numeric("42"))
        self.assertTrue(is_numeric("3.14"))
        self.assertFalse(is_numeric("abc"))
        self.assertTrue(is_alpha("hello"))
        self.assertTrue(is_alphanumeric("abc123"))

    def test_transform(self):
        from stdlib.text import normalize, strip_accents, template
        self.assertEqual(normalize("cafe\u0301"), "café")
        self.assertEqual(strip_accents("café"), "cafe")
        self.assertEqual(template("Hello {name}", name="World"), "Hello World")


class TestMath(unittest.TestCase):
    def test_constants(self):
        from stdlib.math import PI, E, TAU
        self.assertAlmostEqual(PI, 3.141592653589793, places=10)
        self.assertAlmostEqual(E, 2.718281828459045, places=10)
        self.assertAlmostEqual(TAU, 2 * PI, places=10)

    def test_basic_arithmetic(self):
        from stdlib.math import add, sub, mul, div, mod, pow, sqrt
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(sub(5, 3), 2)
        self.assertEqual(mul(3, 4), 12)
        self.assertEqual(div(10, 2), 5.0)
        self.assertEqual(mod(10, 3), 1)
        self.assertEqual(pow(2, 10), 1024)
        self.assertEqual(sqrt(9), 3.0)

    def test_division_by_zero(self):
        from stdlib.math import div, mod
        with self.assertRaises(ValueError):
            div(1, 0)
        with self.assertRaises(ValueError):
            mod(1, 0)

    def test_rounding(self):
        from stdlib.math import floor, ceil, round_to, clamp, lerp
        self.assertEqual(floor(3.7), 3)
        self.assertEqual(ceil(3.2), 4)
        self.assertEqual(round_to(3.14159, 2), 3.14)
        self.assertEqual(clamp(10, 0, 5), 5)
        self.assertEqual(clamp(-1, 0, 5), 0)
        self.assertAlmostEqual(lerp(0, 10, 0.3), 3.0, places=5)

    def test_logarithms(self):
        from stdlib.math import ln, log2, log10, exp
        self.assertAlmostEqual(log10(100), 2.0, places=5)
        self.assertAlmostEqual(log2(8), 3.0, places=5)
        self.assertAlmostEqual(exp(0), 1.0, places=5)

    def test_trig(self):
        from stdlib.math import sin, cos, PI
        self.assertAlmostEqual(sin(0), 0.0, places=5)
        self.assertAlmostEqual(cos(0), 1.0, places=5)
        self.assertAlmostEqual(sin(PI / 2), 1.0, places=5)

    def test_statistics(self):
        from stdlib.math import mean, median, stdev
        self.assertEqual(mean([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(median([1, 2, 3, 4, 5]), 3)
        self.assertEqual(median([1, 2, 3, 4]), 2.5)
        self.assertAlmostEqual(stdev([1, 2, 3, 4, 5]), 1.414213, places=3)

    def test_number_theory(self):
        from stdlib.math import gcd, lcm, factorial, is_prime, fibonacci
        self.assertEqual(gcd(12, 8), 4)
        self.assertEqual(lcm(4, 6), 12)
        self.assertEqual(factorial(5), 120)
        self.assertTrue(is_prime(7))
        self.assertFalse(is_prime(4))
        self.assertEqual(fibonacci(10), 55)


class TestNumbers(unittest.TestCase):
    def test_type_checks(self):
        from stdlib.numbers import is_int, is_float, is_number, is_bool
        self.assertTrue(is_int(42))
        self.assertTrue(is_float(3.14))
        self.assertTrue(is_number(42))
        self.assertTrue(is_bool(True))
        self.assertFalse(is_int(True))

    def test_parsing(self):
        from stdlib.numbers import parse_int, parse_float, try_parse_int
        self.assertEqual(parse_int("42"), 42)
        self.assertEqual(parse_int("ff", 16), 255)
        self.assertAlmostEqual(parse_float("3.14"), 3.14, places=5)
        self.assertIsNone(try_parse_int("abc"))

    def test_conversion(self):
        from stdlib.numbers import to_int, to_float
        self.assertEqual(to_int("42"), 42)
        self.assertEqual(to_int("abc", 0), 0)
        self.assertAlmostEqual(to_float("3.14"), 3.14, places=5)

    def test_utility(self):
        from stdlib.numbers import sign, clamp, map_range
        self.assertEqual(sign(5), 1)
        self.assertEqual(sign(-5), -1)
        self.assertEqual(sign(0), 0)
        self.assertEqual(clamp(10, 0, 5), 5)
        self.assertAlmostEqual(map_range(5, 0, 10, 0, 100), 50.0)


class TestCollections(unittest.TestCase):
    def test_list_ops(self):
        from stdlib.collections import list_new, list_copy, list_contains, list_reverse
        lst = list_new(1, 2, 3)
        self.assertEqual(lst, [1, 2, 3])
        self.assertTrue(list_contains(lst, 2))
        self.assertEqual(list_reverse(lst), [3, 2, 1])

    def test_list_transform(self):
        from stdlib.collections import list_flatten, list_unique, list_chunk
        self.assertEqual(list_flatten([[1, 2], [3, 4]]), [1, 2, 3, 4])
        self.assertEqual(list_unique([1, 2, 1, 3]), [1, 2, 3])
        self.assertEqual(list_chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])

    def test_functional(self):
        from stdlib.collections import map_list, filter_list, reduce_list, any_match, all_match
        self.assertEqual(map_list(lambda x: x * 2, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(filter_list(lambda x: x > 2, [1, 2, 3, 4]), [3, 4])
        self.assertEqual(reduce_list(lambda a, b: a + b, [1, 2, 3]), 6)
        self.assertTrue(any_match(lambda x: x > 2, [1, 2, 3]))
        self.assertFalse(all_match(lambda x: x > 2, [1, 2, 3]))

    def test_map_ops(self):
        from stdlib.collections import map_new, map_get, map_has, map_merge
        d = map_new(a=1, b=2)
        self.assertEqual(map_get(d, "a"), 1)
        self.assertTrue(map_has(d, "a"))
        merged = map_merge(d, {"c": 3})
        self.assertEqual(merged, {"a": 1, "b": 2, "c": 3})

    def test_set_ops(self):
        from stdlib.collections import set_new, set_union, set_intersection, set_difference
        a = set_new(1, 2, 3)
        b = set_new(2, 3, 4)
        self.assertEqual(set_union(a, b), {1, 2, 3, 4})
        self.assertEqual(set_intersection(a, b), {2, 3})
        self.assertEqual(set_difference(a, b), {1})

    def test_aggregation(self):
        from stdlib.collections import group_by, frequency, sliding_window
        self.assertEqual(group_by([1, 2, 3], lambda x: x % 2), {1: [1, 3], 0: [2]})
        self.assertEqual(frequency(["a", "b", "a"]), {"a": 2, "b": 1})
        self.assertEqual(sliding_window([1, 2, 3, 4], 2), [(1, 2), (2, 3), (3, 4)])


class TestRandom(unittest.TestCase):
    def test_basic(self):
        from stdlib.random import Random
        rng = Random(42)
        self.assertEqual(rng.rand_int(1, 1), 1)
        self.assertTrue(0 <= rng.random() < 1)
        self.assertIn(rng.choice([1, 2, 3]), [1, 2, 3])

    def test_reproducibility(self):
        from stdlib.random import Random
        rng1 = Random(123)
        rng2 = Random(123)
        self.assertEqual([rng1.random() for _ in range(5)], [rng2.random() for _ in range(5)])

    def test_shuffle(self):
        from stdlib.random import Random
        rng = Random(42)
        lst = [1, 2, 3, 4, 5]
        shuffled = rng.shuffled(lst)
        self.assertEqual(sorted(shuffled), lst)

    def test_coin_flip(self):
        from stdlib.random import Random
        rng = Random(42)
        results = [rng.coin_flip(0.0) for _ in range(10)]
        self.assertFalse(any(results))


class TestUnicode(unittest.TestCase):
    def test_classification(self):
        from stdlib.unicode import is_upper, is_lower, is_digit, is_alpha
        self.assertTrue(is_upper("A"))
        self.assertTrue(is_lower("a"))
        self.assertTrue(is_digit("5"))
        self.assertTrue(is_alpha("z"))

    def test_properties(self):
        from stdlib.unicode import category, name, code_point, from_code_point
        self.assertEqual(code_point("A"), 65)
        self.assertEqual(from_code_point(65), "A")
        self.assertEqual(name("A"), "LATIN CAPITAL LETTER A")

    def test_normalization(self):
        from stdlib.unicode import normalize, is_normalized, strip_combining
        self.assertTrue(is_normalized("cafe", "NFC"))
        nfd = normalize("cafe\u0301", "NFD")
        self.assertFalse(is_normalized(nfd, "NFC"))
        self.assertEqual(strip_combining("hello"), "hello")

    def test_encoding(self):
        from stdlib.unicode import encode, decode, code_points, from_code_points
        self.assertEqual(encode("hello"), b"hello")
        self.assertEqual(decode(b"hello"), "hello")
        self.assertEqual(code_points("AB"), [65, 66])
        self.assertEqual(from_code_points([65, 66]), "AB")


# ═══════════════════════════════════════════════════════════════
# Core modules
# ═══════════════════════════════════════════════════════════════

class TestTime(unittest.TestCase):
    def test_now(self):
        from stdlib.time import now, now_monotonic
        self.assertGreater(now(), 0)
        self.assertGreater(now_monotonic(), 0)

    def test_format(self):
        from stdlib.time import format_time, format_duration
        self.assertIn("2023", format_time(1700000000, "%Y"))
        self.assertEqual(format_duration(0.5), "500.0 ms")
        self.assertEqual(format_duration(90), "1m 30s")

    def test_timer(self):
        from stdlib.time import Timer
        with Timer() as t:
            pass
        self.assertGreaterEqual(t.elapsed, 0)


class TestDate(unittest.TestCase):
    def test_today(self):
        from stdlib.date import today, now
        self.assertIsNotNone(today())
        self.assertIsNotNone(now())

    def test_creation(self):
        from stdlib.date import new, format_date, to_iso
        d = new(2024, 1, 15)
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)
        self.assertEqual(format_date(d), "2024-01-15")
        self.assertEqual(to_iso(d), "2024-01-15")

    def test_arithmetic(self):
        from stdlib.date import new, add_days, diff_days
        d = new(2024, 1, 1)
        d2 = add_days(d, 10)
        self.assertEqual(diff_days(d2, d), 10)

    def test_leap_year(self):
        from stdlib.date import is_leap_year
        self.assertTrue(is_leap_year(2024))
        self.assertFalse(is_leap_year(2023))


class TestIO(unittest.TestCase):
    def test_file_ops(self):
        from stdlib.io import read_file, write_file, append_file, exists
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            path = f.name
        try:
            write_file(path, "hello")
            self.assertEqual(read_file(path), "hello")
            append_file(path, " world")
            self.assertEqual(read_file(path), "hello world")
            self.assertTrue(exists(path))
        finally:
            os.unlink(path)

    def test_read_write_lines(self):
        from stdlib.io import read_lines, write_lines
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            path = f.name
        try:
            write_lines(path, ["a", "b", "c"])
            self.assertEqual(read_lines(path), ["a", "b", "c"])
        finally:
            os.unlink(path)

    def test_memory_stream(self):
        from stdlib.io import MemoryStream
        s = MemoryStream()
        s.write(b"hello")
        s.seek(0)
        self.assertEqual(s.read(), b"hello")

    def test_string_stream(self):
        from stdlib.io import StringStream
        s = StringStream()
        s.write("hello")
        s.seek(0)
        self.assertEqual(s.read(), "hello")


class TestPaths(unittest.TestCase):
    def test_join(self):
        from stdlib.paths import join, stem, ext, basename, dirname
        self.assertIn("test.txt", join("dir", "test.txt"))
        self.assertEqual(stem("/path/to/file.txt"), "file")
        self.assertEqual(ext("/path/to/file.txt"), ".txt")
        self.assertEqual(basename("/path/to/file.txt"), "file.txt")
        self.assertEqual(dirname("/path/to/file.txt"), "/path/to")

    def test_normalize(self):
        from stdlib.paths import normalize
        self.assertIn("test", normalize("path/./to/../test"))

    def test_split(self):
        from stdlib.paths import split, split_ext
        d, f = split("/path/to/file.txt")
        self.assertEqual(f, "file.txt")
        root, ext = split_ext("/path/to/file.txt")
        self.assertEqual(ext, ".txt")


class TestFilesystem(unittest.TestCase):
    def test_copy_delete(self):
        from stdlib.filesystem import copy, exists, delete
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"test")
            src = f.name
        dst = src + ".bak"
        try:
            copy(src, dst)
            self.assertTrue(exists(dst))
            delete(dst)
            self.assertFalse(exists(dst))
        finally:
            if os.path.exists(src):
                os.unlink(src)

    def test_dir_ops(self):
        from stdlib.filesystem import make_dir, list_dirs, exists
        d = tempfile.mkdtemp()
        subdir = os.path.join(d, "test_dir")
        try:
            make_dir(subdir)
            self.assertTrue(exists(subdir))
            self.assertIn("test_dir", list_dirs(d))
        finally:
            os.rmdir(subdir)
            os.rmdir(d)

    def test_disk_usage(self):
        from stdlib.filesystem import disk_usage
        total, used, free = disk_usage(".")
        self.assertGreater(total, 0)


class TestJSON(unittest.TestCase):
    def test_dumps_loads(self):
        from stdlib.json import dumps, loads, is_valid
        data = {"name": "test", "value": 42, "nested": [1, 2, 3]}
        s = dumps(data)
        self.assertTrue(is_valid(s))
        self.assertEqual(loads(s), data)

    def test_compact_pretty(self):
        from stdlib.json import compact, prettify
        s = compact({"a": 1})
        self.assertNotIn(" ", s)
        p = prettify('{"a":1}')
        self.assertIn("\n", p)

    def test_try_loads(self):
        from stdlib.json import try_loads
        self.assertEqual(try_loads("invalid"), None)
        self.assertEqual(try_loads("invalid", {}), {})
        self.assertEqual(try_loads('{"ok": true}'), {"ok": True})


class TestCSV(unittest.TestCase):
    def test_read_write(self):
        from stdlib.csv import reads, writes
        rows = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
        s = writes(rows)
        parsed = reads(s)
        self.assertEqual(parsed, rows)

    def test_dicts(self):
        from stdlib.csv import reads
        s = "Name,Age\nAlice,30\nBob,25\n"
        rows = reads(s)
        self.assertEqual(len(rows), 3)


class TestXML(unittest.TestCase):
    def test_parse_to_string(self):
        from stdlib.xml import from_string, to_string, tag, text
        root = from_string("<root><item>hello</item></root>")
        self.assertEqual(tag(root), "root")
        item = root[0]
        self.assertEqual(tag(item), "item")
        self.assertEqual(text(item), "hello")

    def test_build(self):
        from stdlib.xml import make_element, add_child, to_string
        root = make_element("root")
        add_child(root, "child", text="value")
        s = to_string(root)
        self.assertIn("child", s)
        self.assertIn("value", s)


class TestSerialization(unittest.TestCase):
    def test_pickle(self):
        from stdlib.serialization import to_pickle, from_pickle
        data = {"key": [1, 2, 3]}
        self.assertEqual(from_pickle(to_pickle(data)), data)

    def test_base64(self):
        from stdlib.serialization import to_base64, from_base64
        data = b"hello world"
        self.assertEqual(from_base64(to_base64(data)), data)

    def test_hex(self):
        from stdlib.serialization import to_hex, from_hex
        data = b"\xde\xad\xbe\xef"
        self.assertEqual(from_hex(to_hex(data)), data)


class TestCompression(unittest.TestCase):
    def test_zlib(self):
        from stdlib.compression import compress, decompress
        data = b"hello world " * 100
        compressed = compress(data)
        self.assertLess(len(compressed), len(data))
        self.assertEqual(decompress(compressed), data)

    def test_gzip(self):
        from stdlib.compression import gzip_compress, gzip_decompress
        data = b"test data " * 50
        compressed = gzip_compress(data)
        self.assertEqual(gzip_decompress(compressed), data)

    def test_crc32(self):
        from stdlib.compression import crc32
        self.assertEqual(crc32(b"hello"), crc32(b"hello"))
        self.assertNotEqual(crc32(b"hello"), crc32(b"world"))


class TestDatabase(unittest.TestCase):
    def test_basic(self):
        from stdlib.database import Database
        db = Database(":memory:")
        db.execute("CREATE TABLE test (name TEXT, age INTEGER)")
        db.insert("test", {"name": "Alice", "age": 30})
        rows = db.fetch_all("SELECT * FROM test")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Alice")
        self.assertTrue(db.table_exists("test"))
        self.assertIn("test", db.tables())
        db.close()


class TestCrypto(unittest.TestCase):
    def test_hashing(self):
        from stdlib.crypto import hash_sha256, hash_md5
        self.assertEqual(hash_sha256(b"hello"), hash_sha256(b"hello"))
        self.assertNotEqual(hash_sha256(b"hello"), hash_md5(b"hello"))

    def test_hmac(self):
        from stdlib.crypto import hmac_sha256
        self.assertEqual(hmac_sha256(b"key", b"msg"), hmac_sha256(b"key", b"msg"))
        self.assertNotEqual(hmac_sha256(b"key1", b"msg"), hmac_sha256(b"key2", b"msg"))

    def test_random(self):
        from stdlib.crypto import random_bytes, random_hex
        self.assertEqual(len(random_bytes(16)), 16)
        self.assertEqual(len(random_hex(16)), 32)


class TestSecurity(unittest.TestCase):
    def test_password(self):
        from stdlib.security import generate_password, password_strength, is_strong_password
        pwd = generate_password(20)
        self.assertEqual(len(pwd), 20)
        score, label = password_strength("StrongP@ss1")
        self.assertGreater(score, 2)
        self.assertTrue(is_strong_password("MyP@ssw0rd"))

    def test_sanitize(self):
        from stdlib.security import escape_html, sanitize_filename
        self.assertIn("&amp;", escape_html("a&b"))
        self.assertNotIn("/", sanitize_filename("a/b"))


class TestArchive(unittest.TestCase):
    def test_zip(self):
        from stdlib.archive import zip_create, zip_extract, zip_list
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "test.txt")
            with open(src, "w") as f:
                f.write("hello")
            archive = os.path.join(d, "test.zip")
            zip_create(archive, [src])
            self.assertIn("test.txt", zip_list(archive))
            extract_dir = os.path.join(d, "out")
            os.makedirs(extract_dir)
            zip_extract(archive, extract_dir)


# ═══════════════════════════════════════════════════════════════
# System modules
# ═══════════════════════════════════════════════════════════════

class TestSystem(unittest.TestCase):
    def test_os_info(self):
        from stdlib.system import os_name, arch, python_version, pid
        self.assertIn(os_name(), ("Windows", "Linux", "Darwin"))
        self.assertGreater(len(arch()), 0)
        self.assertGreater(len(python_version()), 0)
        self.assertGreater(pid(), 0)


class TestEnvironment(unittest.TestCase):
    def test_env(self):
        from stdlib.environment import get, set_var, has, unset
        set_var("I_TEST_VAR", "hello")
        self.assertEqual(get("I_TEST_VAR"), "hello")
        self.assertTrue(has("I_TEST_VAR"))
        unset("I_TEST_VAR")
        self.assertFalse(has("I_TEST_VAR"))


class TestConfiguration(unittest.TestCase):
    def test_config(self):
        from stdlib.configuration import Config
        c = Config()
        c.set("database.host", "localhost")
        c.set("database.port", 5432)
        self.assertEqual(c.get("database.host"), "localhost")
        self.assertEqual(c.get("database.port"), 5432)
        self.assertTrue(c.has("database.host"))
        self.assertFalse(c.has("database.missing"))
        self.assertEqual(c.get("missing.key", "default"), "default")

    def test_merge(self):
        from stdlib.configuration import Config
        c = Config({"a": 1})
        c.merge({"b": 2, "a": 3})
        self.assertEqual(c.get("a"), 3)
        self.assertEqual(c.get("b"), 2)


class TestLogging(unittest.TestCase):
    def test_logger(self):
        from stdlib.logging import Logger
        l = Logger("test", level=0)
        l.info("test message")


class TestTerminal(unittest.TestCase):
    def test_color(self):
        from stdlib.terminal import colored, red, green, bold
        s = colored("hello", fg="\033[31m")
        self.assertIn("hello", s)
        self.assertIn("\033[", s)
        self.assertIn("hello", red("hello"))
        self.assertIn("hello", green("hello"))
        self.assertIn("hello", bold("hello"))

    def test_table(self):
        from stdlib.terminal import print_table
        import io
        buf = io.StringIO()
        print_table(["Name", "Age"], [["Alice", "30"], ["Bob", "25"]], file=buf)
        output = buf.getvalue()
        self.assertIn("Alice", output)
        self.assertIn("Bob", output)


# ═══════════════════════════════════════════════════════════════
# Network module
# ═══════════════════════════════════════════════════════════════

class TestNetwork(unittest.TestCase):
    def test_hostname(self):
        from stdlib.network import hostname
        self.assertGreater(len(hostname()), 0)

    def test_url(self):
        from stdlib.network import URL, parse_url
        url = parse_url("https://example.com:8080/path?q=1#top")
        self.assertEqual(url.scheme, "https")
        self.assertEqual(url.host, "example.com")
        self.assertEqual(url.port, 8080)


# ═══════════════════════════════════════════════════════════════
# Media modules
# ═══════════════════════════════════════════════════════════════

class TestImage(unittest.TestCase):
    def test_detect_format(self):
        from stdlib.image import detect_format
        png_header = b"\x89PNG\r\n\x1a\n"
        self.assertEqual(detect_format(png_header + b"\x00" * 20), "png")
        self.assertIsNone(detect_format(b"random data"))

    def test_image_info(self):
        from stdlib.image import image_info, ImageInfo
        self.assertIsInstance(ImageInfo(100, 200, "png"), ImageInfo)


class TestAudio(unittest.TestCase):
    def test_detect_format(self):
        from stdlib.audio import detect_format
        self.assertEqual(detect_format(b"fLaC" + b"\x00" * 10), "flac")
        self.assertIsNone(detect_format(b"random"))


class TestVideo(unittest.TestCase):
    def test_detect_format(self):
        from stdlib.video import detect_format
        self.assertIsNone(detect_format(b"random"))


class TestGraphics(unittest.TestCase):
    def test_point(self):
        from stdlib.graphics import Point
        p1 = Point(1, 2)
        p2 = Point(4, 6)
        self.assertEqual((p1 + p2).x, 5)
        self.assertAlmostEqual(p1.distance_to(p2), 5.0)

    def test_rect(self):
        from stdlib.graphics import Rect, Point
        r = Rect(0, 0, 10, 10)
        self.assertEqual(r.area, 100)
        self.assertTrue(r.contains(Point(5, 5)))
        self.assertFalse(r.contains(Point(15, 5)))

    def test_color(self):
        from stdlib.graphics import Color
        c = Color(255, 128, 0)
        self.assertEqual(c.to_hex(), "#ff8000")
        c2 = Color.from_hex("#ff8000")
        self.assertEqual(c, c2)


class TestWindow(unittest.TestCase):
    def test_window(self):
        from stdlib.window import Window, create_window
        w = create_window("Test", 800, 600)
        self.assertEqual(w.title, "Test")
        self.assertEqual(w.size, (800, 600))
        w.resize(1024, 768)
        self.assertEqual(w.size, (1024, 768))
        w.close()
        self.assertTrue(w.is_closed)


# ═══════════════════════════════════════════════════════════════
# Advanced modules
# ═══════════════════════════════════════════════════════════════

class TestReflection(unittest.TestCase):
    def test_type(self):
        from stdlib.reflection import type_name, type_of, is_type, is_callable
        self.assertEqual(type_name(42), "int")
        self.assertEqual(type_of("hi"), str)
        self.assertTrue(is_type(42, int))
        self.assertTrue(is_callable(len))

    def test_inspect(self):
        from stdlib.reflection import inspect_function, methods, properties
        info = inspect_function(len)
        self.assertEqual(info["name"], "len")
        self.assertIn("obj", info["parameters"])
        self.assertTrue(len(methods("hello")) > 0)


class TestTesting(unittest.TestCase):
    def test_assertions(self):
        from stdlib.testing import assert_equal, assert_true, assert_false, assert_raises, assert_in
        assert_equal(1, 1)
        assert_true(True)
        assert_false(False)
        assert_raises(ValueError, int, "abc")
        assert_in(1, [1, 2, 3])

    def test_suite(self):
        from stdlib.testing import TestSuite
        suite = TestSuite("test")
        suite.add("pass", lambda: None)
        suite.add("fail", lambda: (_ for _ in ()).throw(AssertionError("fail")))
        results = suite.run()
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].passed)
        self.assertFalse(results[1].passed)


class TestBenchmark(unittest.TestCase):
    def test_bench(self):
        from stdlib.benchmark import bench, bench_time
        result = bench(lambda: sum(range(100)), iterations=100, name="sum_test")
        self.assertEqual(result.name, "sum_test")
        self.assertEqual(result.iterations, 100)
        self.assertGreater(result.avg_ms, 0)

    def test_timer(self):
        from stdlib.benchmark import Timer
        with Timer("test") as t:
            pass
        self.assertGreaterEqual(t.elapsed_ms, 0)


class TestDebug(unittest.TestCase):
    def test_debug_var(self):
        from stdlib.debug import debug_var, memory_dump, stack_trace
        import io
        buf = io.StringIO()
        import sys
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            debug_var("x", 42)
        finally:
            sys.stdout = old_stdout
        self.assertIn("42", buf.getvalue())

    def test_memory_dump(self):
        from stdlib.debug import memory_dump
        info = memory_dump([1, 2, 3])
        self.assertEqual(info["type"], "list")
        self.assertGreater(info["size_bytes"], 0)

    def test_stack_trace(self):
        from stdlib.debug import stack_trace
        st = stack_trace()
        self.assertIsInstance(st, list)


class TestLocalization(unittest.TestCase):
    def test_locale(self):
        from stdlib.localization import Locale, EN, RW
        self.assertEqual(EN.language, "en")
        self.assertEqual(RW.currency, "RWF")

    def test_translator(self):
        from stdlib.localization import Translator, EN
        t = Translator(EN)
        t.add("hello", {"en": "Hello", "rw": "Muraho"})
        self.assertEqual(t.t("hello"), "Hello")
        t.set_language("rw")
        self.assertEqual(t.t("hello"), "Muraho")

    def test_format_number(self):
        from stdlib.localization import format_number, EN, FR
        self.assertEqual(format_number(1234.56, EN), "1,234.56")
        self.assertEqual(format_number(1234.56, FR), "1 234,56")


# ═══════════════════════════════════════════════════════════════
# Meta modules
# ═══════════════════════════════════════════════════════════════

class TestPackage(unittest.TestCase):
    def test_package_info(self):
        from stdlib.package import PackageInfo
        info = PackageInfo("test-pkg", "1.0.0", "A test package", ["dep1"])
        d = info.to_dict()
        info2 = PackageInfo.from_dict(d)
        self.assertEqual(info.name, info2.name)
        self.assertEqual(info.version, info2.version)

    def test_version_check(self):
        from stdlib.package import version_satisfies
        self.assertTrue(version_satisfies("1.2.0", ">=1.0.0"))
        self.assertFalse(version_satisfies("0.9.0", ">=1.0.0"))
        self.assertTrue(version_satisfies("1.0.0", "==1.0.0"))


class TestVM(unittest.TestCase):
    def test_version(self):
        from stdlib.vm import version
        self.assertEqual(version(), "1.0.0")


if __name__ == "__main__":
    unittest.main()
