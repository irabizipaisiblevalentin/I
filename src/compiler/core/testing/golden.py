"""
Golden test framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..diagnostics.engine import DiagnosticEngine


@dataclass
class GoldenTest:
    """
    Golden test case.
    
    Compares actual output against expected output stored in files.
    """
    
    name: str
    input_path: Path
    expected_output_path: Path
    expected_errors: Optional[List[str]] = None
    
    @classmethod
    def from_files(cls, input_path: Path, expected_path: Path) -> GoldenTest:
        """Create test from input and expected output files."""
        return cls(
            name=input_path.stem,
            input_path=input_path,
            expected_output_path=expected_path,
        )


class GoldenTestRunner:
    """
    Runs golden tests and compares results.
    """
    
    def __init__(self, update: bool = False) -> None:
        """
        Initialize runner.
        
        Args:
            update: If True, update expected output files
        """
        self._update = update
        self._results: List[dict] = []
    
    def run(self, test: GoldenTest, actual_output: str) -> bool:
        """
        Run a golden test.
        
        Args:
            test: Golden test case
            actual_output: Actual output from compiler
            
        Returns:
            True if test passed
        """
        if self._update:
            self._update_expected(test, actual_output)
            return True
        
        expected = self._load_expected(test)
        
        passed = actual_output == expected
        
        self._results.append({
            "test": test.name,
            "passed": passed,
            "expected": expected,
            "actual": actual_output,
        })
        
        return passed
    
    def _load_expected(self, test: GoldenTest) -> str:
        """Load expected output."""
        if test.expected_output_path.exists():
            return test.expected_output_path.read_text(encoding="utf-8")
        return ""
    
    def _update_expected(self, test: GoldenTest, output: str) -> None:
        """Update expected output file."""
        test.expected_output_path.parent.mkdir(parents=True, exist_ok=True)
        test.expected_output_path.write_text(output, encoding="utf-8")
    
    def get_results(self) -> List[dict]:
        """Get test results."""
        return self._results.copy()
    
    def clear_results(self) -> None:
        """Clear test results."""
        self._results.clear()
