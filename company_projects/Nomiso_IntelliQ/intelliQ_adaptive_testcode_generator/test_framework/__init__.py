"""
Test Framework Module

This module provides a base framework for test automation that can be extended 
for different testing frameworks like Selenium, Appium, Playwright, etc.

Classes:
    - AITestCaseCodeGenerator: Base class for test code generation
    - TestContext: Context management for test parameters
    - ScriptWriter: Handles script file operations
    - TestRunner: Orchestrates test execution
"""

from .base_generator import AITestCaseCodeGenerator
from .test_context import TestContext
from .script_writer import ScriptWriter
from .test_runner import TestRunner

__all__ = [
    'AITestCaseCodeGenerator',
    'TestContext', 
    'ScriptWriter',
    'TestRunner'
]