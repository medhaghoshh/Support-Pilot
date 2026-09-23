"""
SupportPilot AI

Dynamic Integrations Configuration

Handles persistence of integrations settings to a local JSON file,
falling back to environment variables.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# We save the config file to a stable path in the app directory
CONFIG_FILE_PATH = Path(__file__).parent.parent / "integrations_config.json"


def load_config_file() -> dict:
    """
    Load settings from the JSON config file.
    """
    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # If JSON is corrupt, return empty dict
            return {}
    return {}


def save_config_file(config_data: dict) -> None:
    """
    Save settings to the JSON config file.
    """
    try:
        # Load existing config to merge it
        existing = load_config_file()
        existing.update(config_data)
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4)
    except Exception as e:
        raise RuntimeError(f"Failed to save integration config: {e}")


def get_jira_config() -> dict[str, str | None]:
    """
    Get current Jira configuration, merging file settings with .env settings.
    """
    file_config = load_config_file()
    
    return {
        "JIRA_URL": file_config.get("JIRA_URL") or os.getenv("JIRA_URL"),
        "JIRA_EMAIL": file_config.get("JIRA_EMAIL") or os.getenv("JIRA_EMAIL"),
        "JIRA_API_TOKEN": file_config.get("JIRA_API_TOKEN") or os.getenv("JIRA_API_TOKEN"),
        "JIRA_PROJECT_KEY": file_config.get("JIRA_PROJECT_KEY") or os.getenv("JIRA_PROJECT_KEY"),
    }


def get_email_config() -> dict[str, str | None]:
    """
    Get current Email configuration, merging file settings with .env settings.
    """
    file_config = load_config_file()
    
    return {
        "EMAIL_ADDRESS": file_config.get("EMAIL_ADDRESS") or os.getenv("EMAIL_ADDRESS"),
        "EMAIL_APP_PASSWORD": file_config.get("EMAIL_APP_PASSWORD") or os.getenv("EMAIL_APP_PASSWORD"),
    }
