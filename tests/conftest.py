"""Pytest configuration and shared fixtures for Schedule TUI tests."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, MagicMock

import pytest


@pytest.fixture
def sample_tasks() -> List[Dict[str, Any]]:
    """Sample TaskWarrior task data for testing."""
    return [
        {
            "id": 1,
            "uuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "description": "Test task 1",
            "status": "pending",
            "project": "home",
            "scheduled": "20260206T000000Z",
            "due": "20260208T000000Z",
            "wait": "",
        },
        {
            "id": 2,
            "uuid": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "description": "Test task 2",
            "status": "pending",
            "project": "work",
            "scheduled": "20260207T000000Z",
            "due": "",
            "wait": "20260206T000000Z",
        },
        {
            "id": 3,
            "uuid": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "description": "Test task 3 with a very long description that exceeds fifty characters",
            "status": "pending",
            "project": "",
            "scheduled": "",
            "due": "20260210T000000Z",
            "wait": "",
        },
    ]


@pytest.fixture
def mock_subprocess_run(monkeypatch, sample_tasks):
    """Mock subprocess.run for TaskWarrior commands."""

    def mock_run(cmd, *args, **kwargs):
        result = Mock()
        result.returncode = 0
        result.stderr = ""

        # Handle different command patterns
        if "export" in cmd:
            result.stdout = json.dumps(sample_tasks)
        elif "modify" in cmd:
            result.stdout = "Modified 1 task."
        elif "_config" in cmd:
            # Return sample report configuration
            result.stdout = "\n".join(
                [
                    "report.next.columns=id,description,project",
                    "report.all.columns=id,description",
                    "report.overdue.columns=id,description,due",
                ]
            )
        else:
            result.stdout = ""

        return result

    monkeypatch.setattr(subprocess, "run", mock_run)
    return mock_run


@pytest.fixture
def mock_config(monkeypatch, tmp_path):
    """Mock configuration for testing."""
    config_data = {
        "default_report": "next",
        "default_date_fields": ["scheduled"],
        "confirm_before_schedule": False,
        "hotkeys": {
            "1": "tomorrow",
            "2": "+2d",
            "3": "+3d",
            "4": "sow",
            "5": "som",
        },
    }

    # Create a temporary config file
    config_file = tmp_path / "config.yaml"

    def mock_get_config_path():
        return config_file

    # Patch the get_config_path function
    from schedule import config

    monkeypatch.setattr(config, "get_config_path", mock_get_config_path)

    return config_data


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file for testing."""
    config_file = tmp_path / "config.yaml"
    return config_file
