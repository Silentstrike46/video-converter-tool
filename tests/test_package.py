"""Smoke tests to ensure the package works correctly."""

import importlib

import pytest


@pytest.mark.parametrize("module_name", ["vct", "vct.cli", "vct.core", "vct.gui"])
def test_import_module(module_name: str):
    """Test that the package and its subpackages can be imported successfully."""
    module = importlib.import_module(module_name)
    assert module.__name__ == module_name
