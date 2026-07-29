"""date — Date manipulation for the I language.

Provides date creation, formatting, arithmetic, and calendar operations.
"""

from __future__ import annotations

import calendar
from datetime import date as _date, datetime, timedelta
from typing import Optional, Tuple


# ---------------------------------------------------------------------------
# Current date
# ---------------------------------------------------------------------------

def today() -> _date:
    """Today's date."""
    return _date.today()


def now() -> datetime:
    """Current datetime."""
    return datetime.now()


def utc_now() -> datetime:
    """Current UTC datetime."""
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------

def new(year: int, month: int, day: int) -> _date:
    """Create a date. Raises ValueError if invalid."""
    return _date(year, month, day)


def from_ordinal(ordinal: int) -> _date:
    """Create date from proleptic Gregorian ordinal."""
    return _date.fromordinal(ordinal)


def from_timestamp(timestamp: float) -> _date:
    """Create date from Unix timestamp."""
    return _date.fromtimestamp(timestamp)


def parse_date(s: str, fmt: str = "%Y-%m-%d") -> _date:
    """Parse date string with format."""
    return datetime.strptime(s, fmt).date()


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def year(d: _date) -> int:
    return d.year


def month(d: _date) -> int:
    return d.month


def day(d: _date) -> int:
    return d.day


def weekday(d: _date) -> int:
    """Day of week (0=Monday, 6=Sunday)."""
    return d.weekday()


def day_name(d: _date) -> str:
    """Name of day (e.g. 'Monday')."""
    return calendar.day_name[d.weekday()]


def month_name(d: _date) -> str:
    """Name of month (e.g. 'January')."""
    return calendar.month_name[d.month]


def is_leap_year(year_val: int) -> bool:
    """Check if year is a leap year."""
    return calendar.isleap(year_val)


def days_in_month(year_val: int, month_val: int) -> int:
    """Number of days in given month."""
    return calendar.monthrange(year_val, month_val)[1]


def day_of_year(d: _date) -> int:
    """Day of year (1-366)."""
    return d.timetuple().tm_yday


def week_number(d: _date) -> int:
    """ISO week number."""
    return d.isocalendar()[1]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_date(d: _date, fmt: str = "%Y-%m-%d") -> str:
    """Format date to string."""
    return d.strftime(fmt)


def to_iso(d: _date) -> str:
    """ISO 8601 format."""
    return d.isoformat()


def to_timestamp(d: _date) -> float:
    """Convert to Unix timestamp."""
    return datetime.combine(d, datetime.min.time()).timestamp()


# ---------------------------------------------------------------------------
# Arithmetic
# ---------------------------------------------------------------------------

def add_days(d: _date, days: int) -> _date:
    """Add days to date."""
    return d + timedelta(days=days)


def add_months(d: _date, months: int) -> _date:
    """Add months to date."""
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, days_in_month(year, month))
    return _date(year, month, day)


def add_years(d: _date, years: int) -> _date:
    """Add years to date."""
    return add_months(d, years * 12)


def diff_days(a: _date, b: _date) -> int:
    """Difference in days (a - b)."""
    return (a - b).days


def diff_months(a: _date, b: _date) -> int:
    """Approximate difference in months."""
    return (a.year - b.year) * 12 + (a.month - b.month)


def days_between(a: _date, b: _date) -> int:
    """Absolute number of days between dates."""
    return abs((a - b).days)


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def is_before(a: _date, b: _date) -> bool:
    return a < b


def is_after(a: _date, b: _date) -> bool:
    return a > b


def is_same(a: _date, b: _date) -> bool:
    return a == b


def is_between(d: _date, low: _date, high: _date) -> bool:
    return low <= d <= high


def min_date(*dates: _date) -> _date:
    return min(dates)


def max_date(*dates: _date) -> _date:
    return max(dates)


# ---------------------------------------------------------------------------
# Range
# ---------------------------------------------------------------------------

def date_range(start: _date, end: _date, step_days: int = 1):
    """Generate dates from start to end (inclusive)."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=step_days)
