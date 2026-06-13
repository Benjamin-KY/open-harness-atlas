"""Pytest configuration for open-harness-atlas.

Adds a `--network` flag so the optional link-check tests stay opt-in.
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--network",
        action="store_true",
        default=False,
        help="Run tests that require outbound network (skipped by default).",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--network"):
        return
    skip_network = pytest.mark.skip(reason="needs --network flag")
    for item in items:
        if "network" in item.keywords:
            item.add_marker(skip_network)
