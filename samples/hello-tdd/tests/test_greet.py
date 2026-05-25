# agent-notes: { ctx: "TDD red phase tests for greet command", deps: ["src/greeter/cli.py"], state: active, last: "tara@2026-03-15" }

"""Tests for the greet command.

Written by Tara (red phase) before any implementation existed.
These tests defined the expected behavior for GRT-1.
"""

import pytest
from greeter.cli import greet


def test_greet_default_name():
    """Greeting with no name should address the world."""
    result = greet()
    assert result == "Hello, World!"


def test_greet_custom_name():
    """Greeting with a name should address that person."""
    result = greet(name="Alice")
    assert result == "Hello, Alice!"


def test_greet_empty_name_raises():
    """Greeting with an empty string should raise, not silently default."""
    with pytest.raises(ValueError, match="Name cannot be empty"):
        greet(name="")
