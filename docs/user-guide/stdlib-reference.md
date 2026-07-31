# I Standard Library Reference

Version **1.0.0** ships 44 standard-library modules plus `urubuga.i` (web framework
source). The modules are written in Python, hosted in the `stdlib` package, and are
imported from host code as `import stdlib.<module>`.

> **Note for I programs:** In 1.0.0 the `shyiramo` import system resolves a small set of
> built-in module names. The full Python standard library below is available to
> toolchain and host integrations. See the [Language Guide](language-guide.md#modules).

## Module Index by Category

| Category | Modules |
| --- | --- |
| Text & Unicode | `text`, `unicode`, `localization`, `serialization` |
| Math & Numbers | `math`, `numbers`, `random` |
| Data Structures | `collections`, `package` |
| Data Formats | `json`, `xml`, `yaml`, `csv`, `configuration` |
| Files & Paths | `io`, `filesystem`, `paths` |
| Time & Date | `time`, `date` |
| Networking & Web | `http`, `httpserver`, `network`, `websocket` |
| Security & Crypto | `crypto`, `security` |
| System & Process | `system`, `process`, `environment`, `terminal`, `debug` |
| Compression & Archive | `compression`, `archive` |
| Media & UI | `audio`, `image`, `video`, `graphics`, `window` |
| Database | `database` |
| Tooling | `compiler`, `vm`, `testing`, `benchmark`, `reflection` |

---

## Text & Unicode

### `text` — string manipulation

Core string helpers: `to_upper`, `to_lower`, `to_title`, `trim`, `ltrim`, `rtrim`,
`split`, `rsplit`, `join`, `lines`, `repeat`, `reverse`, `replace`, `pad_left`,
`pad_right`, `pad_center`, `pad_numeric`, `truncate`, `wrap`, `template`,
`pluralize`, `normalize`, `strip_accents`, `to_case_fold`.

Searching and inspection: `contains`, `count`, `find`, `rfind`, `index_of`,
`starts_with`, `ends_with`, `is_empty`, `is_blank`, `is_alpha`, `is_alphanumeric`,
`is_numeric`, `is_identifier`.

Regular expressions: `regex_search`, `regex_find_all`, `regex_replace`.

```python
import stdlib.text as t
t.to_upper("muraho")          # "MURAHO"
t.join(["-", "a", "b", "c"])  # "a-b-c"
```

### `unicode` — Unicode utilities

Code points: `code_point`, `code_points`, `from_code_point`, `from_code_points`,
`chars`, `graphemes`, `utf8_bytes`, `utf8_encoded`, `encode`, `decode`, `normalize`,
`is_normalized`, `strip_combining`, `combining`, `reverse`, `lookup`, `name`,
`category`, `numeric_value`, `digit_value`, `east_asian_width`.

Character classes: `is_alpha`, `is_alnum`, `is_digit`, `is_numeric`, `is_space`,
`is_lower`, `is_upper`, `is_title`, `is_control`, `is_printable`, `is_punctuation`,
`is_symbol`.

### `localization` — locales and translation

Constants: `RW`, `EN`, `FR`, `ES`, `DE`, `JA`.

Classes: `Locale` (language/region handling), `Translator` (key → localized string).
Functions: `format_number`, `format_currency`.

### `serialization` — binary and text encodings

Base64: `to_base64`, `from_base64`, `to_base64url`, `from_base64url`.
Hex: `to_hex`, `from_hex`. JSON: `to_json`, `from_json`.
Pickle: `to_pickle`, `from_pickle`. Packed binary: `pack`, `unpack`.

---

## Math & Numbers

### `math` — mathematics

Constants: `PI`, `E`, `TAU`, `PHI`, `INFINITY`, `NAN`, `MAX_INT`, `MIN_INT`.

Basic: `add`, `sub`, `mul`, `div`, `mod`, `idiv`, `abs`, `floor`, `ceil`, `round_to`,
`sign`, `clamp`, `lerp`, `min_val`, `max_val`, `sum`, `product`, `mean`, `median`,
`variance`, `stdev`.

Powers & exponents: `pow`, `sqrt`, `cbrt`, `exp`, `exp2`, `ln`, `log`, `log2`,
`log10`.

Trigonometry: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `sinh`, `cosh`,
`tanh`, `degrees`, `radians`.

Number theory: `gcd`, `lcm`, `factorial`, `fibonacci`, `is_prime`, `primes_up_to`.

### `numbers` — numeric helpers

`is_int`, `is_float`, `is_bool`, `is_number`, `is_rational`, `to_int`, `to_float`,
`to_rational`, `parse_int`, `parse_float`, `try_parse_int`, `try_parse_float`,
`abs_val`, `clamp`, `sign`, `snap`, `precision`, `min_of`, `max_of`, `in_range`,
`map_range`.

### `random` — randomness

`random`, `rand_int`, `choice`, `choices`, `sample`, `shuffle`, `shuffled`,
`coin_flip`, `gauss`, `uniform`, `seed`.

Class: `Random` (seeded generator instance).

---

## Data Structures

### `collections` — lists, maps, sets

Lists: `list_new`, `list_of`, `list_append`, `list_prepend`, `list_insert`,
`list_pop`, `list_remove`, `list_contains`, `list_index`, `list_count`, `list_slice`,
`list_reverse`, `list_reverse_mutate`, `list_sort`, `list_sort_mutate`, `list_unique`,
`list_flatten`, `list_flat_map`, `list_zip`, `list_rotate`, `list_chunk`,
`list_sample`, `list_enumerate`, `list_copy`.

Functional helpers: `filter_list`, `all_match`, `any_match`, `find_first`,
`find_last`, `reduce_list`, `partition`, `sliding_window`, `frequency`, `group_by`.

Maps: `map_new`, `map_put`, `map_get`, `map_has`, `map_remove`, `map_keys`,
`map_values`, `map_items`, `map_merge`, `map_from_pairs`, `map_list`,
`map_map_values`, `map_filter`.

Sets: `set_new`, `set_union`, `set_intersection`, `set_difference`,
`set_symmetric_difference`, `set_is_subset`, `set_is_superset`.

### `package` — package metadata

`parse_manifest`, `save_manifest`, `resolve_deps`, `version_satisfies`.
Class: `PackageInfo`.

---

## Data Formats

### `json` — JSON

`load`, `loads`, `try_loads`, `dump`, `dumps`, `to_file`, `from_file`,
`try_from_file`, `is_valid`, `validate`, `minify`, `compact`, `prettify`, `patch`.

### `xml` — XML

`from_string`, `from_file`, `to_string`, `to_file`, `parse`, `make_element`,
`make_tree`, `children`, `parent`, `attr`, `attrs`, `set_attr`, `add_child`,
`remove_child`, `find`, `findall`, `findtext`, `xpath`, `get_text`, `text`, `tag`,
`pretty`.

### `yaml` — YAML

`load`, `load_all`, `load_file`, `load_all_file`, `try_load`, `try_load_file`,
`dump`, `dumps`, `dump_file`.

### `csv` — comma-separated values

`read`, `reads`, `read_row`, `read_dicts`, `iter_rows`, `column`, `write`, `writes`,
`write_dicts`, `transpose`.

### `configuration` — config files

Class: `Config`. Functions: `load_file`, `save_file`, `merge`.

---

## Files & Paths

### `io` — input/output

`read_file`, `read_lines`, `read_bytes`, `write_file`, `write_lines`, `write_bytes`,
`append_file`, `copy_file`, `copy_stream`, `exists`, `is_file`, `is_dir`, `list_dir`,
`mkdir`, `remove`, `rename`, `size`, `temp_file`, `temp_dir`.

Classes: `StringStream`, `MemoryStream`.

### `filesystem` — rich file operations

`exists`, `is_file`, `is_dir`, `is_link`, `list_dir`, `list_files`, `list_dirs`,
`walk_files`, `glob`, `make_dir`, `make_temp_dir`, `make_temp_file`, `delete`,
`delete_tree`, `copy`, `copy_tree`, `move`, `symlink`, `readlink`, `file_size`,
`file_mtime`, `file_stat`, `dir_size`, `disk_usage`, `chmod`, `executable`,
`readable`, `writable`.

### `paths` — path utilities

`join`, `split`, `parts`, `absolute`, `relative`, `normalize`, `real`, `basename`,
`dirname`, `filename`, `stem`, `ext`, `split_ext`, `parent`, `home`, `cwd`, `temp`,
`exists`, `is_absolute`, `is_relative`, `is_file`, `is_dir`, `is_link`, `list_dir`,
`make_dirs`, `remove_file`, `remove_dir`, `walk`, `same`, `to_posix`, `to_windows`.

---

## Time & Date

### `time` — time utilities

`now`, `now_monotonic`, `now_perf_counter`, `now_ns`, `sleep`, `parse`,
`format_time`, `format_duration`.
Class: `Timer`.

### `date` — calendar dates

`new`, `today`, `now`, `utc_now`, `parse_date`, `format_date`, `to_iso`,
`to_timestamp`, `from_timestamp`, `from_ordinal`, `year`, `month`, `day`,
`weekday`, `day_name`, `month_name`, `week_number`, `day_of_year`, `is_leap_year`,
`days_in_month`, `date_range`, `days_between`, `diff_days`, `diff_months`,
`add_days`, `add_months`, `add_years`, `min_date`, `max_date`, `is_before`,
`is_after`, `is_same`, `is_between`.

---

## Networking & Web

### `http` — HTTP client

`get`, `post`, `put`, `delete`, `head`, `request`.
Class: `HTTPResponse`.

```python
import stdlib.http as h
resp = h.get("https://example.com")
print(resp.status_code)
```

### `httpserver` — HTTP server

Classes: `UrubugaHTTPServer`, `UrubugaHTTPHandler`, `NativeRequest`,
`NativeResponse`, `UrubugaWebSocketServer`.
Helpers: `urubuga_json_dumps`, `urubuga_json_loads`, `urubuga_sha256`,
`urubuga_hmac`, `urubuga_random_bytes`, `urubuga_random_token`,
`urubuga_timestamp`, `urubuga_iso_timestamp`, `urubuga_sleep`,
`urubuga_compress`, `urubuga_decompress`, `urubuga_encrypt`, `urubuga_decrypt`,
`urubuga_url_encode`, `urubuga_url_decode`.

### `network` — networking

`hostname`, `resolve`, `reverse_dns`, `is_port_open`, `connect`, `build_url`,
`parse_url`, `encode_query`, `decode_query`, `url_encode`, `url_decode`.
Class: `URL`.

### `websocket` — WebSocket framing

Class: `WebSocketFrame`. Function: `generate_accept_key`.

### `urubuga.i` — web framework source

A Kinyarwanda-authored web framework source module distributed as package data.
It is the seed of the planned `urubuga` framework integration.

---

## Security & Crypto

### `crypto` — hashing and HMAC

Hashing: `hash_md5`, `hash_sha1`, `hash_sha256`, `hash_sha512`, `hash_file`.
HMAC: `hmac_sha256`, `hmac_sha512`.
Random: `random_bytes`, `random_hex`, `random_url_safe`. Comparison: `compare_digest`.

> MD5/SHA-1 are provided for legacy interoperability and are marked
> `usedforsecurity=False` where the host Python permits.

### `security` — application security

`escape_html`, `unescape_html`, `strip_html`, `strip_control_chars`,
`sanitize_filename`, `is_valid_email`, `is_strong_password`, `password_strength`,
`generate_password`, `generate_token`, `generate_api_key`, `generate_salt`.

---

## System & Process

### `system` — runtime information

`hostname`, `arch`, `platform_name`, `os_name`, `os_version`, `pid`, `ppid`,
`cpu_count`, `python_version`, `env`, `env_vars`, `set_env`, `get_stdin`,
`get_stdout`, `get_stderr`, `get_argv`, `exit`.

### `process` — subprocesses

`run`, `run_capture`, `run_checked`, `popen`, `exec_command`, `list_processes`,
`which`.
Class: `ProcessResult`.

> **Security:** the process API launches host commands. Only pass trusted, validated
> arguments to it.

### `environment` — environment variables

`get`, `set_var`, `has`, `unset`, `all_vars`, `items`, `keys`, `values`, `ensure`,
`path_list`, `home_dir`, `temp_dir`, `working_dir`, `is_windows`, `is_linux`,
`is_macos`.

### `terminal` — terminal UI

`write`, `writeln`, `colored`, `print_color`, `red`, `green`, `blue`, `yellow`,
`bold`, `prompt`, `confirm`, `password`, `print_table`.
Classes: `Color`, `ProgressBar`.

### `debug` — debugging aids

`assert_debug`, `breakpoint_here`, `stack_trace`, `print_stack`, `debug_var`,
`debug_vars`, `caller_info`, `memory_dump`, `trace_calls`.

---

## Compression & Archive

### `compression` — compression

zlib: `compress`, `decompress`, `decompress_to_size`, `adler32`, `crc32`.
gzip: `gzip_compress`, `gzip_decompress`, `compress_file`, `decompress_file`.

### `archive` — zip and tar archives

Zip: `zip_create`, `zip_add`, `zip_list`, `zip_extract`.
Tar: `tar_create`, `tar_extract`, `tar_list`.

> **Security:** extraction rejects path traversal (`../`) and symbolic links.

---

## Media & UI

### `audio`, `image`, `video` — media metadata

`audio`: `detect_format`, `audio_info`, `wav_info`, class `AudioInfo`.
`image`: `detect_format`, `image_info`, `png_dimensions`, `jpeg_dimensions`, class
`ImageInfo`.
`video`: `detect_format`, `video_info`, class `VideoInfo`.

### `graphics` — colors and shapes

Classes: `Color`, `Point`, `Rect`. Named colors: `BLACK`, `WHITE`, `RED`, `GREEN`,
`BLUE`, `CYAN`, `MAGENTA`, `YELLOW`, `TRANSPARENT`.

### `window` — display and windowing

`get_displays`, `get_primary_display`, `create_window`.
Classes: `DisplayInfo`, `Window`.

---

## Database

### `database` — embedded SQL

Class: `Database` — embedded SQLite-backed database with connection, query, and
transaction support.

```python
import stdlib.database as db
d = db.Database("app.db")
d.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
```

---

## Tooling

### `compiler` — compiler API

`compile_source`, `disassemble`, `version`.

### `vm` — virtual machine API

`create_vm`, `run_source`, `run_bytecode`, `format_report`, `version`.

### `testing` — assertions and suites

Assertions: `assert_true`, `assert_false`, `assert_equal`, `assert_not_equal`,
`assert_in`, `assert_is_none`, `assert_is_not_none`, `assert_raises`.
Classes: `TestSuite`, `TestRunner`, `TestResult`.

### `benchmark` — performance measurement

`bench`, `bench_time`, `bench_compare`, `print_results`.
Classes: `BenchmarkResult`, `Timer`.

### `reflection` — introspection

`type_of`, `type_name`, `is_callable`, `is_function`, `is_class`, `is_module`,
`is_type`, `get_attr`, `set_attr`, `has_attr`, `call_method`, `methods`,
`properties`, `inspect_function`, `superclass`, `subclasses`.

---

## Version Compatibility

The module index and function names above are verified against the 1.0.0 wheel. New
modules and functions may be added in minor releases; removal or rename follows
semantic versioning (breaking changes bump the major version).
