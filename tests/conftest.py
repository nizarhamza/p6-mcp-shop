"""Catalog tests: tools/ and tests/ on sys.path, the demo database of the golden harness built once.

Run with an MCP for Primavera P6 checkout (with its tests/fixtures) on PYTHONPATH and its dependencies installed:

    PYTHONPATH=<p6-mcp checkout> python -m pytest
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import golden  # noqa: E402


@pytest.fixture(scope="session")
def demo():
    return golden.demo()


@pytest.fixture(scope="session")
def rendered(demo):
    """{skill name: (skill, rendering, step results, raw slot values, example args)} of every src skill."""
    return {name: run[:5] for name, run in _runs(demo).items()}


@pytest.fixture(scope="session")
def oracle_problems(demo):
    """{skill name: differences with its oracles}, compared right after that skill's golden run: an oracle may
    read what the run left (the workbook written, the health snapshot saved), which the next run removes."""
    return {name: run[5] for name, run in _runs(demo).items()}


_RUNS: dict = {}


def _runs(demo) -> dict:
    if not _RUNS:
        from oracles import compare
        for name in golden.names():
            skill = golden.load(name)
            text, results, raw = golden.golden(skill)
            args = golden.example_args(skill)
            _RUNS[name] = (skill, text, results, raw, args, compare(name, skill, results, raw, args, demo))
    return _RUNS
