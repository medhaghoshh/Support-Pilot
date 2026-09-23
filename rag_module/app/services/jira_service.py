"""
SupportPilot AI

Jira Service

Provides helper functions for:

- Creating Jira tickets
- Fetching Jira ticket status
- Updating Jira workflow status
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10

# ---------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------

from app.config.dynamic_config import get_jira_config

def _is_configured() -> bool:
    """
    Returns True only when all Jira configuration
    variables are available.
    """
    config = get_jira_config()
    missing_keys = [k for k, v in config.items() if not v]
    if missing_keys:
        logger.error(
            "Jira service is not configured correctly. Missing keys: %s",
            ", ".join(missing_keys),
        )
        return False
    return True


# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------

def _auth() -> HTTPBasicAuth:
    """
    Build Jira authentication object.
    """
    config = get_jira_config()
    return HTTPBasicAuth(
        config["JIRA_EMAIL"],
        config["JIRA_API_TOKEN"],
    )


def _json_headers() -> dict[str, str]:
    """
    Headers used for JSON requests.
    """

    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _request_headers() -> dict[str, str]:
    """
    Headers used for GET requests.
    """

    return {
        "Accept": "application/json",
    }


# ---------------------------------------------------
# Create Jira Ticket
# ---------------------------------------------------

def create_jira_ticket(
    summary: str,
    description: str,
) -> dict[str, Any] | None:
    """
    Create a Jira issue.

    Parameters
    ----------
    summary : str
        Jira issue summary.

    description : str
        Jira issue description.

    Returns
    -------
    dict[str, Any] | None
        Jira API response on success,
        otherwise None.
    """

    logger.info(
        "Creating Jira ticket..."
    )

    if not _is_configured():
        return None

    config = get_jira_config()
    url = f"{config['JIRA_URL']}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {
                "key": config['JIRA_PROJECT_KEY'],
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description,
                            }
                        ],
                    }
                ],
            },
            "issuetype": {
                "name": "Task",
            },
        }
    }

    try:

        response = requests.post(
            url=url,
            json=payload,
            headers=_json_headers(),
            auth=_auth(),
            timeout=REQUEST_TIMEOUT,
        )

    except requests.exceptions.Timeout:

        logger.error(
            "Timed out while creating Jira ticket."
        )

        return None

    except requests.exceptions.ConnectionError:

        logger.error(
            "Unable to connect to Jira."
        )

        return None

    except requests.exceptions.RequestException:

        logger.exception(
            "Unexpected Jira request error."
        )

        return None

    if response.status_code == 201:

        data = response.json()

        data["jira_status"] = "To Do"

        data["ticket_url"] = (
            f"{config['JIRA_URL']}/browse/{data['key']}"
        )

        logger.info(
            "Jira ticket created successfully (%s).",
            data["key"],
        )

        return data

    logger.error(
        "Failed to create Jira ticket "
        "(HTTP %s). Response: %s",
        response.status_code,
        response.text,
    )

    return None

# ---------------------------------------------------
# Get Jira Ticket Status
# ---------------------------------------------------

def get_jira_ticket_status(
    ticket_key: str,
) -> str | None:
    """
    Retrieve the current workflow status
    of a Jira issue.

    Parameters
    ----------
    ticket_key : str
        Jira issue key.

    Returns
    -------
    str | None
        Current workflow status,
        or None if unavailable.
    """

    logger.info(
        "Fetching Jira status for %s",
        ticket_key,
    )

    if not _is_configured():
        return None

    config = get_jira_config()
    url = (
        f"{config['JIRA_URL']}/rest/api/3/issue/"
        f"{ticket_key}"
    )

    try:

        response = requests.get(
            url=url,
            headers=_request_headers(),
            auth=_auth(),
            timeout=REQUEST_TIMEOUT,
        )

    except requests.exceptions.Timeout:

        logger.error(
            "Timed out while fetching Jira status."
        )

        return None

    except requests.exceptions.ConnectionError:

        logger.error(
            "Unable to connect to Jira."
        )

        return None

    except requests.exceptions.RequestException:

        logger.exception(
            "Unexpected Jira request error."
        )

        return None

    if response.status_code == 200:

        data = response.json()

        status = (
            data
            .get("fields", {})
            .get("status", {})
            .get("name")
        )

        logger.info(
            "Jira status for %s is %s",
            ticket_key,
            status,
        )

        return status

    logger.error(
        "Failed to fetch Jira status "
        "(HTTP %s). Response: %s",
        response.status_code,
        response.text,
    )

    return None

# ---------------------------------------------------
# Update Jira Ticket Status
# ---------------------------------------------------

def update_jira_status(
    ticket_key: str,
    target_status: str,
) -> bool:
    """
    Move a Jira issue to another workflow status.

    Parameters
    ----------
    ticket_key : str
        Jira issue key.

    target_status : str
        Desired workflow status.

    Returns
    -------
    bool
        True if updated successfully,
        otherwise False.
    """

    logger.info(
        "Updating Jira ticket %s -> %s",
        ticket_key,
        target_status,
    )

    if not _is_configured():
        return False

    config = get_jira_config()
    url = (
        f"{config['JIRA_URL']}/rest/api/3/issue/"
        f"{ticket_key}/transitions"
    )

    # ---------------------------------------------------
    # Retrieve Available Transitions
    # ---------------------------------------------------

    try:

        response = requests.get(
            url=url,
            headers=_request_headers(),
            auth=_auth(),
            timeout=REQUEST_TIMEOUT,
        )

    except requests.exceptions.Timeout:

        logger.error(
            "Timed out while retrieving transitions."
        )

        return False

    except requests.exceptions.ConnectionError:

        logger.error(
            "Unable to connect to Jira."
        )

        return False

    except requests.exceptions.RequestException:

        logger.exception(
            "Unexpected Jira request error."
        )

        return False

    if response.status_code != 200:

        logger.error(
            "Unable to retrieve transitions "
            "(HTTP %s). Response: %s",
            response.status_code,
            response.text,
        )

        return False

    transitions = response.json().get(
        "transitions",
        [],
    )

    transition_id = None

    # ---------------------------------------------------
    # Find Matching Transition
    # ---------------------------------------------------

    for transition in transitions:

        transition_name = (
            transition
            .get("to", {})
            .get("name", "")
        )

        if (
            transition_name.lower()
            == target_status.lower()
        ):

            transition_id = transition.get("id")
            break

    if transition_id is None:

        logger.warning(
            "Target status '%s' is not available.",
            target_status,
        )

        available = [
            t.get("to", {}).get("name", "Unknown")
            for t in transitions
        ]

        logger.info(
            "Available statuses: %s",
            ", ".join(available),
        )

        return False

    payload = {
        "transition": {
            "id": transition_id,
        }
    }

    # ---------------------------------------------------
    # Update Ticket Status
    # ---------------------------------------------------

    try:

        update_response = requests.post(
            url=url,
            json=payload,
            headers=_json_headers(),
            auth=_auth(),
            timeout=REQUEST_TIMEOUT,
        )

    except requests.exceptions.Timeout:

        logger.error(
            "Timed out while updating Jira status."
        )

        return False

    except requests.exceptions.ConnectionError:

        logger.error(
            "Unable to connect to Jira."
        )

        return False

    except requests.exceptions.RequestException:

        logger.exception(
            "Unexpected Jira request error."
        )

        return False

    if update_response.status_code == 204:

        logger.info(
            "Jira ticket %s updated to %s.",
            ticket_key,
            target_status,
        )

        return True

    logger.error(
        "Failed to update Jira ticket "
        "(HTTP %s). Response: %s",
        update_response.status_code,
        update_response.text,
    )

    return False


# ---------------------------------------------------
# Public Exports
# ---------------------------------------------------

__all__ = [
    "create_jira_ticket",
    "get_jira_ticket_status",
    "update_jira_status",
]