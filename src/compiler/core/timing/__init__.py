"""
Timing Utilities

Performance measurement and timing.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, Generator, List, Optional


@dataclass
class TimingEntry:
    """A single timing measurement."""
    
    name: str
    elapsed: float
    count: int = 1
    
    @property
    def average(self) -> float:
        """Average time per call."""
        return self.elapsed / self.count if self.count > 0 else 0.0


class Timer:
    """
    Simple timer for measuring elapsed time.
    """
    
    def __init__(self) -> None:
        self._start: Optional[float] = None
        self._elapsed: float = 0.0
    
    def start(self) -> None:
        """Start the timer."""
        self._start = time.perf_counter()
    
    def stop(self) -> float:
        """
        Stop the timer.
        
        Returns:
            Elapsed time in seconds
        """
        if self._start is not None:
            self._elapsed += time.perf_counter() - self._start
            self._start = None
        return self._elapsed
    
    @property
    def elapsed(self) -> float:
        """Elapsed time in seconds."""
        if self._start is not None:
            return self._elapsed + (time.perf_counter() - self._start)
        return self._elapsed
    
    def reset(self) -> None:
        """Reset the timer."""
        self._start = None
        self._elapsed = 0.0


class TimingCollector:
    """
    Collects timing measurements.
    """
    
    def __init__(self) -> None:
        self._entries: Dict[str, TimingEntry] = {}
    
    def record(self, name: str, elapsed: float) -> None:
        """
        Record a timing measurement.
        
        Args:
            name: Measurement name
            elapsed: Elapsed time in seconds
        """
        if name in self._entries:
            entry = self._entries[name]
            entry.elapsed += elapsed
            entry.count += 1
        else:
            self._entries[name] = TimingEntry(name=name, elapsed=elapsed)
    
    @contextmanager
    def measure(self, name: str) -> Generator[None, None, None]:
        """
        Context manager for measuring code blocks.
        
        Args:
            name: Measurement name
        """
        timer = Timer()
        timer.start()
        try:
            yield
        finally:
            timer.stop()
            self.record(name, timer.elapsed)
    
    def get_entries(self) -> List[TimingEntry]:
        """Get all timing entries."""
        return list(self._entries.values())
    
    def get_entry(self, name: str) -> Optional[TimingEntry]:
        """Get specific timing entry."""
        return self._entries.get(name)
    
    def clear(self) -> None:
        """Clear all entries."""
        self._entries.clear()
    
    def format_report(self) -> str:
        """Format timing report."""
        lines = ["Timing Report:", "=" * 40]
        
        entries = sorted(
            self._entries.values(),
            key=lambda e: e.elapsed,
            reverse=True,
        )
        
        for entry in entries:
            lines.append(
                f"  {entry.name:30s} "
                f"{entry.elapsed*1000:8.2f}ms "
                f"(x{entry.count})"
            )
        
        return "\n".join(lines)
