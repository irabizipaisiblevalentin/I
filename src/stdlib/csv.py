"""csv — CSV reading and writing for the I language.

Provides CSV parsing and generation with configurable delimiters.
"""

from __future__ import annotations

import csv as _csv
import io
from typing import Any, Dict, List, Optional, Sequence, TextIO, Union


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def read(path: str, delimiter: str = ",", encoding: str = "utf-8") -> List[List[str]]:
    """Read CSV file as list of rows (each row is list of strings)."""
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = _csv.reader(f, delimiter=delimiter)
        return list(reader)


def reads(s: str, delimiter: str = ",") -> List[List[str]]:
    """Parse CSV string."""
    reader = _csv.reader(io.StringIO(s), delimiter=delimiter)
    return list(reader)


def read_dicts(path: str, delimiter: str = ",", encoding: str = "utf-8") -> List[Dict[str, str]]:
    """Read CSV file as list of dicts (uses first row as header)."""
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = _csv.DictReader(f, delimiter=delimiter)
        return list(reader)


def read_row(path: str, delimiter: str = ",", encoding: str = "utf-8") -> List[str]:
    """Read first row of CSV file."""
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = _csv.reader(f, delimiter=delimiter)
        return next(reader, [])


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def write(path: str, rows: Sequence[Sequence[Any]], delimiter: str = ",",
          encoding: str = "utf-8") -> int:
    """Write rows to CSV file. Returns number of rows written."""
    with open(path, "w", encoding=encoding, newline="") as f:
        writer = _csv.writer(f, delimiter=delimiter)
        count = 0
        for row in rows:
            writer.writerow(row)
            count += 1
        return count


def writes(rows: Sequence[Sequence[Any]], delimiter: str = ",") -> str:
    """Write rows to CSV string."""
    buf = io.StringIO()
    writer = _csv.writer(buf, delimiter=delimiter)
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def write_dicts(path: str, rows: Sequence[Dict[str, Any]], delimiter: str = ",",
                encoding: str = "utf-8") -> None:
    """Write list of dicts to CSV file (uses keys as header)."""
    if not rows:
        return
    with open(path, "w", encoding=encoding, newline="") as f:
        fieldnames = list(rows[0].keys())
        writer = _csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Iteration
# ---------------------------------------------------------------------------

def iter_rows(path: str, delimiter: str = ",", encoding: str = "utf-8"):
    """Iterate over rows in CSV file."""
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = _csv.reader(f, delimiter=delimiter)
        yield from reader


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def column(rows: List[List[str]], index: int) -> List[str]:
    """Extract a column by index."""
    return [row[index] for row in rows if len(row) > index]


def transpose(rows: List[List[str]]) -> List[List[str]]:
    """Transpose rows and columns."""
    if not rows:
        return []
    return list(map(list, zip(*rows)))
