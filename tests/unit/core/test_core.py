"""
Tests for features, context, and testing.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from src.compiler.core.context import CompilerContext
from src.compiler.core.features import FeatureFlagManager
from src.compiler.core.testing import CompilerTestHelper, GoldenTest, GoldenTestRunner

# ============================================================================
# FeatureFlagManager Tests
# ============================================================================


class TestFeatureFlagManager:
    """Tests for FeatureFlagManager."""

    def test_default_flags(self):
        """Test default feature flags."""
        manager = FeatureFlagManager()

        assert not manager.is_enabled("experimental_generics")
        assert manager.is_enabled("experimental_pattern_matching")

    def test_enable(self):
        """Test enabling feature."""
        manager = FeatureFlagManager()
        manager.enable("experimental_generics")

        assert manager.is_enabled("experimental_generics")

    def test_disable(self):
        """Test disabling feature."""
        manager = FeatureFlagManager()
        manager.disable("experimental_pattern_matching")

        assert not manager.is_enabled("experimental_pattern_matching")

    def test_reset(self):
        """Test resetting overrides."""
        manager = FeatureFlagManager()
        manager.enable("experimental_generics")
        manager.reset()

        assert not manager.is_enabled("experimental_generics")

    def test_get_enabled(self):
        """Test getting enabled features."""
        manager = FeatureFlagManager()
        manager.enable("experimental_generics")

        enabled = manager.get_enabled()

        assert "experimental_generics" in enabled
        assert "experimental_pattern_matching" in enabled


# ============================================================================
# CompilerContext Tests
# ============================================================================


class TestCompilerContext:
    """Tests for CompilerContext."""

    def test_creation(self):
        """Test creating context."""
        ctx = CompilerContext()

        assert ctx.diagnostics is not None
        assert ctx.features is not None

    def test_add_source(self):
        """Test adding source file."""
        from src.compiler.core.source import SourceFile

        ctx = CompilerContext()
        source = SourceFile.from_string("hello")

        ctx.add_source(source)

        assert ctx.get_source("<string>") is not None

    def test_set_get_state(self):
        """Test setting and getting state."""
        ctx = CompilerContext()

        ctx.set_state("key", "value")

        assert ctx.get_state("key") == "value"
        assert ctx.get_state("missing", "default") == "default"

    def test_reset(self):
        """Test resetting context."""
        ctx = CompilerContext()
        ctx.set_state("key", "value")

        ctx.reset()

        assert ctx.get_state("key") is None


# ============================================================================
# GoldenTest Tests
# ============================================================================


class TestGoldenTest:
    """Tests for GoldenTest."""

    def test_runner_update(self):
        """Test runner with update mode."""
        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "test.il"
            expected_path = Path(tmpdir) / "test.expected"

            input_path.write_text("hello")

            test = GoldenTest(
                name="test",
                input_path=input_path,
                expected_output_path=expected_path,
            )

            runner = GoldenTestRunner(update=True)
            runner.run(test, "expected output")

            assert expected_path.read_text() == "expected output"

    def test_runner_pass(self):
        """Test runner with passing test."""
        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "test.il"
            expected_path = Path(tmpdir) / "test.expected"

            input_path.write_text("hello")
            expected_path.write_text("output")

            test = GoldenTest(
                name="test",
                input_path=input_path,
                expected_output_path=expected_path,
            )

            runner = GoldenTestRunner()
            passed = runner.run(test, "output")

            assert passed

    def test_runner_fail(self):
        """Test runner with failing test."""
        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "test.il"
            expected_path = Path(tmpdir) / "test.expected"

            input_path.write_text("hello")
            expected_path.write_text("expected")

            test = GoldenTest(
                name="test",
                input_path=input_path,
                expected_output_path=expected_path,
            )

            runner = GoldenTestRunner()
            passed = runner.run(test, "actual")

            assert not passed


# ============================================================================
# CompilerTestHelper Tests
# ============================================================================


class TestCompilerTestHelper:
    """Tests for CompilerTestHelper."""

    def test_add_source(self):
        """Test adding source."""
        helper = CompilerTestHelper()
        source = helper.add_source("hello")

        assert source.content == "hello"

    def test_assert_no_errors(self):
        """Test asserting no errors."""
        helper = CompilerTestHelper()
        helper.assert_no_errors()

    def test_assert_errors(self):
        """Test asserting errors."""
        helper = CompilerTestHelper()
        helper.diagnostics.error("test error")
        helper.assert_errors(1)

    def test_get_error_messages(self):
        """Test getting error messages."""
        helper = CompilerTestHelper()
        helper.diagnostics.error("error 1")
        helper.diagnostics.error("error 2")

        messages = helper.get_error_messages()

        assert len(messages) == 2
        assert "error 1" in messages
        assert "error 2" in messages
