from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


# ──────────────────────────────────────────────────────────────────────
# PassStats
# ──────────────────────────────────────────────────────────────────────

@dataclass
class PassStats:
    name: str
    duration_ms: float = 0.0
    changed: bool = False
    instructions_before: int = 0
    instructions_after: int = 0
    blocks_before: int = 0
    blocks_after: int = 0
    functions_before: int = 0
    functions_after: int = 0
    bytes_before: int = 0
    bytes_after: int = 0
    details: str = ""

    @property
    def instructions_eliminated(self) -> int:
        return self.instructions_before - self.instructions_after

    @property
    def blocks_eliminated(self) -> int:
        return self.blocks_before - self.blocks_after

    @property
    def functions_eliminated(self) -> int:
        return self.functions_before - self.functions_after

    @property
    def bytes_saved(self) -> int:
        return self.bytes_before - self.bytes_after


# ──────────────────────────────────────────────────────────────────────
# StatisticsEngine
# ──────────────────────────────────────────────────────────────────────

class StatisticsEngine:
    __slots__ = (
        "_pass_stats",
        "_pass_timers",
        "_total_instructions_before",
        "_total_instructions_after",
        "_total_blocks_before",
        "_total_blocks_after",
        "_total_functions_before",
        "_total_functions_after",
        "_total_bytes_before",
        "_total_bytes_after",
        "_start_time",
        "_pass_counts",
    )

    def __init__(self) -> None:
        self._pass_stats: dict[str, PassStats] = {}
        self._pass_timers: dict[str, float] = {}
        self._total_instructions_before = 0
        self._total_instructions_after = 0
        self._total_blocks_before = 0
        self._total_blocks_after = 0
        self._total_functions_before = 0
        self._total_functions_after = 0
        self._total_bytes_before = 0
        self._total_bytes_after = 0
        self._start_time = time.monotonic()
        self._pass_counts: dict[str, int] = {}

    # ── pass lifecycle ──

    def start_pass(self, name: str) -> None:
        self._pass_timers[name] = time.monotonic()
        if name not in self._pass_counts:
            self._pass_counts[name] = 0
        self._pass_counts[name] += 1

    def end_pass(self, name: str, changed: bool = False, details: str = "") -> None:
        start = self._pass_timers.pop(name, self._start_time)
        duration = (time.monotonic() - start) * 1000.0

        if name in self._pass_stats:
            existing = self._pass_stats[name]
            existing.duration_ms += duration
            existing.changed = existing.changed or changed
            if details:
                existing.details = details
        else:
            self._pass_stats[name] = PassStats(
                name=name,
                duration_ms=duration,
                changed=changed,
                details=details,
            )

    # ── counters ──

    def record_instruction_count(self, before: int, after: int) -> None:
        self._total_instructions_before += before
        self._total_instructions_after += after

    def record_block_count(self, before: int, after: int) -> None:
        self._total_blocks_before += before
        self._total_blocks_after += after

    def record_function_count(self, before: int, after: int) -> None:
        self._total_functions_before += before
        self._total_functions_after += after

    def record_byte_count(self, before: int, after: int) -> None:
        self._total_bytes_before += before
        self._total_bytes_after += after

    # ── queries ──

    def get_pass_stats(self, name: str) -> PassStats | None:
        return self._pass_stats.get(name)

    def all_pass_stats(self) -> list[PassStats]:
        return list(self._pass_stats.values())

    # ── properties ──

    @property
    def total_duration_ms(self) -> float:
        return (time.monotonic() - self._start_time) * 1000.0

    @property
    def total_passes_run(self) -> int:
        return sum(self._pass_counts.values())

    @property
    def total_passes_changed(self) -> int:
        return sum(1 for s in self._pass_stats.values() if s.changed)

    @property
    def instructions_eliminated(self) -> int:
        return self._total_instructions_before - self._total_instructions_after

    @property
    def blocks_eliminated(self) -> int:
        return self._total_blocks_before - self._total_blocks_after

    @property
    def functions_eliminated(self) -> int:
        return self._total_functions_before - self._total_functions_after

    @property
    def bytes_saved(self) -> int:
        return self._total_bytes_before - self._total_bytes_after

    # ── report generation ──

    def generate_report(self, module_name: str = "module") -> OptimizationReport:
        return OptimizationReport(
            module_name=module_name,
            pass_stats=self.all_pass_stats(),
            total_duration_ms=self.total_duration_ms,
            instructions_before=self._total_instructions_before,
            instructions_after=self._total_instructions_after,
            blocks_before=self._total_blocks_before,
            blocks_after=self._total_blocks_after,
            functions_before=self._total_functions_before,
            functions_after=self._total_functions_after,
            bytes_before=self._total_bytes_before,
            bytes_after=self._total_bytes_after,
        )


# ──────────────────────────────────────────────────────────────────────
# OptimizationReport
# ──────────────────────────────────────────────────────────────────────

class OptimizationReport:
    __slots__ = (
        "_module_name",
        "_pass_stats",
        "_total_duration_ms",
        "_instructions_before",
        "_instructions_after",
        "_blocks_before",
        "_blocks_after",
        "_functions_before",
        "_functions_after",
        "_bytes_before",
        "_bytes_after",
    )

    def __init__(
        self,
        module_name: str,
        pass_stats: list[PassStats],
        total_duration_ms: float,
        instructions_before: int,
        instructions_after: int,
        blocks_before: int,
        blocks_after: int,
        functions_before: int,
        functions_after: int,
        bytes_before: int,
        bytes_after: int,
    ) -> None:
        self._module_name = module_name
        self._pass_stats = list(pass_stats)
        self._total_duration_ms = total_duration_ms
        self._instructions_before = instructions_before
        self._instructions_after = instructions_after
        self._blocks_before = blocks_before
        self._blocks_after = blocks_after
        self._functions_before = functions_before
        self._functions_after = functions_after
        self._bytes_before = bytes_before
        self._bytes_after = bytes_after

    # ── properties ──

    @property
    def module_name(self) -> str:
        return self._module_name

    @property
    def total_duration_ms(self) -> float:
        return self._total_duration_ms

    @property
    def instructions_eliminated(self) -> int:
        return self._instructions_before - self._instructions_after

    @property
    def blocks_eliminated(self) -> int:
        return self._blocks_before - self._blocks_after

    @property
    def functions_eliminated(self) -> int:
        return self._functions_before - self._functions_after

    @property
    def bytes_saved(self) -> int:
        return self._bytes_before - self._bytes_after

    @property
    def pass_count(self) -> int:
        return len(self._pass_stats)

    @property
    def changed_passes(self) -> list[PassStats]:
        return [s for s in self._pass_stats if s.changed]

    @property
    def unchanged_passes(self) -> list[PassStats]:
        return [s for s in self._pass_stats if not s.changed]

    @property
    def slowest_pass(self) -> PassStats | None:
        if not self._pass_stats:
            return None
        return max(self._pass_stats, key=lambda s: s.duration_ms)

    @property
    def most_effective_pass(self) -> PassStats | None:
        changed = self.changed_passes
        if not changed:
            return None
        return max(changed, key=lambda s: s.instructions_eliminated)

    # ── formatting ──

    def format_summary(self) -> str:
        lines = [
            f"Optimization Report: {self._module_name}",
            f"  Duration:          {self._total_duration_ms:.2f} ms",
            f"  Passes run:        {self.pass_count}",
            f"  Passes changed:    {len(self.changed_passes)}",
            f"  Instructions:      {self._instructions_before} -> {self._instructions_after} ({self.instructions_eliminated} eliminated)",
            f"  Blocks:            {self._blocks_before} -> {self._blocks_after} ({self.blocks_eliminated} eliminated)",
            f"  Functions:         {self._functions_before} -> {self._functions_after} ({self.functions_eliminated} eliminated)",
            f"  Bytes:             {self._bytes_before} -> {self._bytes_after} ({self.bytes_saved} saved)",
        ]
        return "\n".join(lines)

    def format_table(self) -> str:
        if not self._pass_stats:
            return "(no passes recorded)"

        header = f"{'Pass':<30} {'Time (ms)':>10} {'Changed':>8} {'Instr':>10} {'Blocks':>8} {'Bytes':>10}"
        separator = "-" * len(header)
        rows = [header, separator]

        for s in self._pass_stats:
            changed_str = "yes" if s.changed else "no"
            row = (
                f"{s.name:<30} "
                f"{s.duration_ms:>10.2f} "
                f"{changed_str:>8} "
                f"{s.instructions_eliminated:>10} "
                f"{s.blocks_eliminated:>8} "
                f"{s.bytes_saved:>10}"
            )
            rows.append(row)

        rows.append(separator)
        total_row = (
            f"{'TOTAL':<30} "
            f"{self._total_duration_ms:>10.2f} "
            f"{len(self.changed_passes):>8} "
            f"{self.instructions_eliminated:>10} "
            f"{self.blocks_eliminated:>8} "
            f"{self.bytes_saved:>10}"
        )
        rows.append(total_row)

        return "\n".join(rows)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_name": self._module_name,
            "total_duration_ms": self._total_duration_ms,
            "pass_count": self.pass_count,
            "changed_pass_count": len(self.changed_passes),
            "instructions": {
                "before": self._instructions_before,
                "after": self._instructions_after,
                "eliminated": self.instructions_eliminated,
            },
            "blocks": {
                "before": self._blocks_before,
                "after": self._blocks_after,
                "eliminated": self.blocks_eliminated,
            },
            "functions": {
                "before": self._functions_before,
                "after": self._functions_after,
                "eliminated": self.functions_eliminated,
            },
            "bytes": {
                "before": self._bytes_before,
                "after": self._bytes_after,
                "saved": self.bytes_saved,
            },
            "passes": [
                {
                    "name": s.name,
                    "duration_ms": s.duration_ms,
                    "changed": s.changed,
                    "instructions_eliminated": s.instructions_eliminated,
                    "blocks_eliminated": s.blocks_eliminated,
                    "functions_eliminated": s.functions_eliminated,
                    "bytes_saved": s.bytes_saved,
                    "details": s.details,
                }
                for s in self._pass_stats
            ],
        }
