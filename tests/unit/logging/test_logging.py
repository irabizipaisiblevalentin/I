"""
Tests for logging framework.
"""

import io
from datetime import datetime

import pytest

from src.compiler.core.logging import (
    Logger,
    get_logger,
    LogLevel,
    LogHandler,
    ConsoleHandler,
    FileHandler,
    LogFormatter,
    PlainFormatter,
    ColoredFormatter,
    LogRecord,
)
from pathlib import Path
from tempfile import TemporaryDirectory


# ============================================================================
# LogLevel Tests
# ============================================================================


class TestLogLevel:
    """Tests for LogLevel."""
    
    def test_from_string(self):
        """Test parsing level from string."""
        assert LogLevel.from_string("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_string("info") == LogLevel.INFO
        assert LogLevel.from_string("WARN") == LogLevel.WARNING
        assert LogLevel.from_string("error") == LogLevel.ERROR
    
    def test_from_string_invalid(self):
        """Test parsing invalid level."""
        with pytest.raises(ValueError):
            LogLevel.from_string("INVALID")
    
    def test_name_short(self):
        """Test short level name."""
        assert LogLevel.DEBUG.name_short == "DEBU"
        assert LogLevel.INFO.name_short == "INFO"


# ============================================================================
# LogRecord Tests
# ============================================================================


class TestLogRecord:
    """Tests for LogRecord."""
    
    def test_record_creation(self):
        """Test creating a record."""
        record = LogRecord(
            level=LogLevel.INFO,
            message="Test message",
            logger_name="test",
        )
        
        assert record.level == LogLevel.INFO
        assert record.message == "Test message"
        assert record.logger_name == "test"
    
    def test_record_str(self):
        """Test string representation."""
        record = LogRecord(
            level=LogLevel.INFO,
            message="Test message",
            logger_name="test",
        )
        
        result = str(record)
        assert "INFO" in result
        assert "test" in result
        assert "Test message" in result


# ============================================================================
# Formatter Tests
# ============================================================================


class TestPlainFormatter:
    """Tests for PlainFormatter."""
    
    def test_format(self):
        """Test formatting record."""
        formatter = PlainFormatter()
        record = LogRecord(
            level=LogLevel.INFO,
            message="Test message",
            logger_name="test",
        )
        
        result = formatter.format(record)
        
        assert "INFO" in result
        assert "test" in result
        assert "Test message" in result


class TestColoredFormatter:
    """Tests for ColoredFormatter."""
    
    def test_format(self):
        """Test formatting record with colors."""
        formatter = ColoredFormatter()
        record = LogRecord(
            level=LogLevel.INFO,
            message="Test message",
            logger_name="test",
        )
        
        result = formatter.format(record)
        
        assert "\033[32m" in result  # Green for INFO
        assert "\033[0m" in result  # Reset
        assert "Test message" in result


# ============================================================================
# Handler Tests
# ============================================================================


class TestConsoleHandler:
    """Tests for ConsoleHandler."""
    
    def test_handler_creation(self):
        """Test creating handler."""
        stream = io.StringIO()
        handler = ConsoleHandler(stream=stream)
        
        assert handler.is_enabled(LogLevel.INFO)
    
    def test_emit(self):
        """Test emitting record."""
        stream = io.StringIO()
        handler = ConsoleHandler(stream=stream)
        
        record = LogRecord(
            level=LogLevel.INFO,
            message="Test message",
            logger_name="test",
        )
        
        handler.emit(record)
        
        output = stream.getvalue()
        assert "Test message" in output
    
    def test_level_filter(self):
        """Test level filtering."""
        stream = io.StringIO()
        handler = ConsoleHandler(stream=stream)
        handler.set_level(LogLevel.WARNING)
        
        record = LogRecord(
            level=LogLevel.INFO,
            message="Test message",
            logger_name="test",
        )
        
        handler.emit(record)
        
        output = stream.getvalue()
        assert output == ""


class TestFileHandler:
    """Tests for FileHandler."""
    
    def test_handler_creation(self):
        """Test creating handler."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.log"
            handler = FileHandler(path)
            
            assert handler.is_enabled(LogLevel.INFO)
    
    def test_emit(self):
        """Test emitting to file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.log"
            handler = FileHandler(path)
            
            record = LogRecord(
                level=LogLevel.INFO,
                message="Test message",
                logger_name="test",
            )
            
            handler.emit(record)
            handler.flush()
            
            content = path.read_text()
            assert "Test message" in content


# ============================================================================
# Logger Tests
# ============================================================================


class TestLogger:
    """Tests for Logger."""
    
    def test_logger_creation(self):
        """Test creating logger."""
        logger = Logger("test")
        
        assert logger.name == "test"
        assert logger.level == LogLevel.INFO
    
    def test_logger_set_level(self):
        """Test setting logger level."""
        logger = Logger("test")
        logger.set_level(LogLevel.DEBUG)
        
        assert logger.level == LogLevel.DEBUG
    
    def test_logger_child(self):
        """Test creating child logger."""
        logger = Logger("parent")
        child = logger.child("child")
        
        assert child.name == "parent.child"
    
    def test_logger_debug(self):
        """Test debug logging."""
        stream = io.StringIO()
        handler = ConsoleHandler(stream=stream)
        
        logger = Logger("test", handlers=[handler])
        logger.set_level(LogLevel.DEBUG)
        logger.debug("Debug message")
        
        output = stream.getvalue()
        assert "Debug message" in output
    
    def test_logger_info(self):
        """Test info logging."""
        stream = io.StringIO()
        handler = ConsoleHandler(stream=stream)
        
        logger = Logger("test", handlers=[handler])
        logger.info("Info message")
        
        output = stream.getvalue()
        assert "Info message" in output
    
    def test_logger_warning(self):
        """Test warning logging."""
        stream = io.StringIO()
        handler = ConsoleHandler(stream=stream)
        
        logger = Logger("test", handlers=[handler])
        logger.warning("Warning message")
        
        output = stream.getvalue()
        assert "Warning message" in output
    
    def test_logger_error(self):
        """Test error logging."""
        stream = io.StringIO()
        handler = ConsoleHandler(stream=stream)
        
        logger = Logger("test", handlers=[handler])
        logger.error("Error message")
        
        output = stream.getvalue()
        assert "Error message" in output
    
    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger("test")
        
        assert logger.name == "test"
        assert isinstance(logger, Logger)
    
    def test_get_logger_same_name(self):
        """Test get_logger returns same instance."""
        logger1 = get_logger("same")
        logger2 = get_logger("same")
        
        assert logger1 is logger2
