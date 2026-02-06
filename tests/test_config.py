"""Tests for config.py - Configuration loading and date field management."""

import os
from pathlib import Path

import pytest
import yaml

from schedule.config import (
    DEFAULT_CONFIG,
    DateFieldManager,
    get_config_path,
    load_config,
)


class TestGetConfigPath:
    """Test configuration path resolution."""

    def test_env_variable_takes_precedence(self, monkeypatch, tmp_path):
        """Environment variable SCHEDULE_CONFIG_FILE should override defaults."""
        custom_path = tmp_path / "my_config.yaml"
        monkeypatch.setenv("SCHEDULE_CONFIG_FILE", str(custom_path))

        result = get_config_path()

        assert result == custom_path

    def test_xdg_config_home_when_set(self, monkeypatch, tmp_path):
        """Should use XDG_CONFIG_HOME when environment variable is set."""
        monkeypatch.delenv("SCHEDULE_CONFIG_FILE", raising=False)
        xdg_home = tmp_path / "xdg_config"
        monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_home))

        result = get_config_path()

        assert result == xdg_home / "schedule" / "config.yaml"

    def test_default_config_location(self, monkeypatch):
        """Should default to ~/.config/schedule/config.yaml."""
        monkeypatch.delenv("SCHEDULE_CONFIG_FILE", raising=False)
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

        result = get_config_path()

        expected = Path.home() / ".config" / "schedule" / "config.yaml"
        assert result == expected

    def test_tilde_expansion_in_env_path(self, monkeypatch):
        """Should expand ~ in SCHEDULE_CONFIG_FILE path."""
        monkeypatch.setenv("SCHEDULE_CONFIG_FILE", "~/custom/config.yaml")

        result = get_config_path()

        assert "~" not in str(result)
        assert str(result).startswith(str(Path.home()))


class TestLoadConfig:
    """Test configuration file loading."""

    def test_returns_defaults_when_file_missing(self, monkeypatch, tmp_path):
        """Should return DEFAULT_CONFIG when config file doesn't exist."""
        missing_file = tmp_path / "nonexistent.yaml"
        monkeypatch.setattr("schedule.config.get_config_path", lambda: missing_file)

        result = load_config()

        assert result == DEFAULT_CONFIG

    def test_loads_valid_yaml_file(self, monkeypatch, tmp_path):
        """Should load and parse valid YAML configuration."""
        config_file = tmp_path / "config.yaml"
        custom_config = {
            "default_report": "overdue",
            "hotkeys": {"1": "+1w", "2": "friday"},
        }
        config_file.write_text(yaml.dump(custom_config))
        monkeypatch.setattr("schedule.config.get_config_path", lambda: config_file)

        result = load_config()

        assert result["default_report"] == "overdue"
        assert result["hotkeys"]["1"] == "+1w"
        # Should merge with defaults
        assert "default_date_fields" in result

    def test_returns_defaults_on_invalid_yaml(self, monkeypatch, tmp_path):
        """Should return defaults if YAML is malformed."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: syntax: {{")
        monkeypatch.setattr("schedule.config.get_config_path", lambda: config_file)

        result = load_config()

        assert result == DEFAULT_CONFIG

    def test_returns_defaults_on_empty_file(self, monkeypatch, tmp_path):
        """Should return defaults if file is empty."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")
        monkeypatch.setattr("schedule.config.get_config_path", lambda: config_file)

        result = load_config()

        assert result == DEFAULT_CONFIG

    def test_returns_defaults_on_read_error(self, monkeypatch, tmp_path):
        """Should return defaults if file cannot be read."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("valid: yaml")
        config_file.chmod(0o000)  # Remove read permissions
        monkeypatch.setattr("schedule.config.get_config_path", lambda: config_file)

        try:
            result = load_config()
            assert result == DEFAULT_CONFIG
        finally:
            config_file.chmod(0o644)  # Restore permissions for cleanup

    def test_config_merges_with_defaults(self, monkeypatch, tmp_path):
        """Custom config should override defaults but keep unspecified values."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"default_report": "custom"}))
        monkeypatch.setattr("schedule.config.get_config_path", lambda: config_file)

        result = load_config()

        assert result["default_report"] == "custom"  # Overridden
        assert (
            result["default_date_fields"] == DEFAULT_CONFIG["default_date_fields"]
        )  # Default
        assert result["hotkeys"] == DEFAULT_CONFIG["hotkeys"]  # Default

    def test_full_custom_config(self, monkeypatch, tmp_path):
        """Should handle completely custom configuration."""
        config_file = tmp_path / "config.yaml"
        custom_config = {
            "default_report": "all",
            "default_date_fields": ["due", "wait"],
            "confirm_before_schedule": True,
            "hotkeys": {
                "1": "+1d",
                "2": "monday",
                "3": "eow",
                "6": "custom",
            },
        }
        config_file.write_text(yaml.dump(custom_config))
        monkeypatch.setattr("schedule.config.get_config_path", lambda: config_file)

        result = load_config()

        assert result["default_report"] == "all"
        assert result["default_date_fields"] == ["due", "wait"]
        assert result["confirm_before_schedule"] is True
        assert result["hotkeys"]["1"] == "+1d"
        assert result["hotkeys"]["6"] == "custom"


class TestDateFieldManager:
    """Test date field management functionality."""

    def test_initialization_empty(self):
        """Should initialize with no active fields when None provided."""
        manager = DateFieldManager()

        assert manager.get_active() == []

    def test_initialization_with_fields(self):
        """Should initialize with specified active fields."""
        manager = DateFieldManager(["scheduled", "due"])

        active = manager.get_active()
        assert sorted(active) == ["due", "scheduled"]

    def test_get_active_returns_sorted_list(self):
        """Should return active fields in sorted order."""
        manager = DateFieldManager(["wait", "scheduled", "due"])

        active = manager.get_active()

        assert active == ["due", "scheduled", "wait"]

    def test_toggle_adds_field(self):
        """Toggling inactive field should add it."""
        manager = DateFieldManager(["scheduled"])

        manager.toggle("due")

        assert "due" in manager.get_active()
        assert "scheduled" in manager.get_active()

    def test_toggle_removes_field(self):
        """Toggling active field should remove it."""
        manager = DateFieldManager(["scheduled", "due"])

        manager.toggle("due")

        active = manager.get_active()
        assert "due" not in active
        assert "scheduled" in active

    def test_toggle_multiple_times(self):
        """Toggling field multiple times should alternate state."""
        manager = DateFieldManager()

        # First toggle - add
        manager.toggle("wait")
        assert "wait" in manager.get_active()

        # Second toggle - remove
        manager.toggle("wait")
        assert "wait" not in manager.get_active()

        # Third toggle - add again
        manager.toggle("wait")
        assert "wait" in manager.get_active()

    def test_toggle_all_three_fields(self):
        """Should handle all three standard date fields."""
        manager = DateFieldManager()

        manager.toggle("scheduled")
        manager.toggle("due")
        manager.toggle("wait")

        active = manager.get_active()
        assert active == ["due", "scheduled", "wait"]

    def test_toggle_removes_all_fields(self):
        """Should handle removing all fields."""
        manager = DateFieldManager(["scheduled", "due", "wait"])

        manager.toggle("scheduled")
        manager.toggle("due")
        manager.toggle("wait")

        assert manager.get_active() == []

    def test_initialization_removes_duplicates(self):
        """Should handle duplicate fields in initialization."""
        manager = DateFieldManager(["scheduled", "scheduled", "due"])

        active = manager.get_active()
        assert active.count("scheduled") == 1
        assert len(active) == 2
