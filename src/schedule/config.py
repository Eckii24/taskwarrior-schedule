"""Configuration module for Schedule TUI.

Loads configuration from YAML file with XDG base directory support.
Supports environment variable override via SCHEDULE_CONFIG_FILE.
Falls back to defaults if file is missing or invalid.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


DEFAULT_CONFIG = {
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


def get_config_path() -> Path:
    """Get the configuration file path.

    Priority:
    1. SCHEDULE_CONFIG_FILE environment variable
    2. XDG config directory: ~/.config/schedule/config.yaml

    Returns:
        Path object pointing to config file (may not exist)
    """
    # Check environment variable first
    env_path = os.environ.get("SCHEDULE_CONFIG_FILE")
    if env_path:
        return Path(env_path).expanduser()

    # Use XDG base directory standard
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        config_dir = Path(xdg_config_home) / "schedule"
    else:
        config_dir = Path.home() / ".config" / "schedule"

    return config_dir / "config.yaml"


def load_config() -> Dict[str, Any]:
    """Load configuration from file or return defaults.

    Attempts to load configuration from the config file path.
    If the file doesn't exist, returns default config.
    If the file exists but contains invalid YAML, returns default config.
    If the file exists and is valid, merges it with defaults (file overrides).

    Returns:
        Dictionary containing merged configuration
    """
    config_path = get_config_path()

    # If file doesn't exist, return defaults
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    # Try to load and parse YAML
    try:
        with open(config_path, "r") as f:
            file_config = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        # If there's any error reading or parsing, return defaults
        return DEFAULT_CONFIG.copy()

    # If YAML is valid but empty, return defaults
    if file_config is None:
        return DEFAULT_CONFIG.copy()

    # Merge file config over defaults
    result = DEFAULT_CONFIG.copy()
    if isinstance(file_config, dict):
        result.update(file_config)

    return result
