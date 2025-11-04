"""
Logging utilities for the framework generator.
Provides structured logging and error handling.
"""

import logging
import sys
from enum import Enum
from typing import Optional


class LogLevel(Enum):
    """Log levels for the generator"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class GeneratorLogger:
    """Logger for the framework generator with colored output"""
    
    # ANSI color codes for terminal output
    COLORS = {
        LogLevel.DEBUG: '\033[90m',    # Gray
        LogLevel.INFO: '\033[94m',     # Blue  
        LogLevel.WARNING: '\033[93m',  # Yellow
        LogLevel.ERROR: '\033[91m',    # Red
        LogLevel.SUCCESS: '\033[92m',  # Green
    }
    RESET = '\033[0m'
    
    def __init__(self, name: str = "framework_generator", level: LogLevel = LogLevel.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        self._setup_handlers()
        self._current_step = 0
        self._total_steps = 0
    
    def _setup_handlers(self):
        """Set up console handler with formatting"""
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
    
    def _format_message(self, level: LogLevel, message: str) -> str:
        """Format message with colors and prefixes"""
        color = self.COLORS.get(level, '')
        prefix_map = {
            LogLevel.DEBUG: "[DEBUG]",
            LogLevel.INFO: "[INFO]",
            LogLevel.WARNING: "[WARNING]",
            LogLevel.ERROR: "[ERROR]",
            LogLevel.SUCCESS: "[SUCCESS]"
        }
        prefix = prefix_map.get(level, "[INFO]")
        
        # Add progress indicator if available
        progress = ""
        if self._total_steps > 0:
            progress = f"[{self._current_step}/{self._total_steps}] "
        
        return f"{color}{prefix} {progress}{message}{self.RESET}"
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(self._format_message(LogLevel.DEBUG, message))
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(self._format_message(LogLevel.INFO, message))
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(self._format_message(LogLevel.WARNING, message))
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(self._format_message(LogLevel.ERROR, message))
    
    def success(self, message: str):
        """Log success message"""
        self.logger.info(self._format_message(LogLevel.SUCCESS, message))
    
    def step(self, message: str):
        """Log a step in the generation process"""
        if self._total_steps > 0:
            self._current_step += 1
        self.info(message)
    
    def set_total_steps(self, total: int):
        """Set total number of steps for progress tracking"""
        self._total_steps = total
        self._current_step = 0
    
    def section(self, title: str):
        """Log a section header"""
        separator = "=" * min(50, len(title) + 10)
        self.info(f"\\n{separator}")
        self.info(f"  {title}")
        self.info(separator)


class GeneratorError(Exception):
    """Base exception for generator errors"""
    
    def __init__(self, message: str, details: Optional[str] = None, suggestions: Optional[list] = None):
        self.message = message
        self.details = details
        self.suggestions = suggestions or []
        super().__init__(self.message)
    
    def __str__(self) -> str:
        result = self.message
        if self.details:
            result += f"\\n\\nDetails: {self.details}"
        if self.suggestions:
            result += f"\\n\\nSuggestions:"
            for suggestion in self.suggestions:
                result += f"\\n  - {suggestion}"
        return result


class ConfigurationError(GeneratorError):
    """Exception for configuration-related errors"""
    pass


class TemplateError(GeneratorError):
    """Exception for template-related errors"""
    pass


class FileSystemError(GeneratorError):
    """Exception for file system related errors"""
    pass


# Global logger instance
logger = GeneratorLogger()