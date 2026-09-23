"""
SupportPilot AI

Integrations Router

Provides endpoints to read and update integrations configurations,
and to test live connections to Jira and Gmail SMTP services.
"""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
import requests
from requests.auth import HTTPBasicAuth
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config.dynamic_config import (
    get_jira_config,
    get_email_config,
    save_config_file,
    load_config_file,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)

# Mask string for passwords and api tokens
MASK_PLACEHOLDER = "••••••••••••••••"


def _is_masked(val: str | None) -> bool:
    if not val:
        return False
    if val == MASK_PLACEHOLDER:
        return True
    # Treat sequence of bullets, asterisks, dots, or question marks as masked
    if all(c in "•*?." for c in val):
        return True
    return False


# ---------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------

class IntegrationsConfigResponse(BaseModel):
    jira_url: str | None
    jira_email: str | None
    jira_api_token: str | None
    jira_project_key: str | None
    email_address: str | None
    email_app_password: str | None


class IntegrationsConfigRequest(BaseModel):
    jira_url: str | None = None
    jira_email: str | None = None
    jira_api_token: str | None = None
    jira_project_key: str | None = None
    email_address: str | None = None
    email_app_password: str | None = None


class JiraTestRequest(BaseModel):
    jira_url: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str


class EmailTestRequest(BaseModel):
    email_address: str
    email_app_password: str
    test_recipient: str = Field(..., description="Email to send test message to")


# ---------------------------------------------------
# Configuration Endpoints
# ---------------------------------------------------

@router.get("/config", response_model=IntegrationsConfigResponse)
def get_config():
    """
    Get current configuration, masking passwords/tokens.
    """
    jira = get_jira_config()
    email = get_email_config()

    # Mask JIRA API token if present
    masked_jira_token = MASK_PLACEHOLDER if jira.get("JIRA_API_TOKEN") else None
    
    # Mask EMAIL app password if present
    masked_email_pwd = MASK_PLACEHOLDER if email.get("EMAIL_APP_PASSWORD") else None

    return {
        "jira_url": jira.get("JIRA_URL"),
        "jira_email": jira.get("JIRA_EMAIL"),
        "jira_api_token": masked_jira_token,
        "jira_project_key": jira.get("JIRA_PROJECT_KEY"),
        "email_address": email.get("EMAIL_ADDRESS"),
        "email_app_password": masked_email_pwd,
    }


@router.post("/config")
def update_config(payload: IntegrationsConfigRequest):
    """
    Update integration configuration.
    Values matching MASK_PLACEHOLDER will not overwrite existing saved tokens.
    """
    existing_file = load_config_file()
    jira = get_jira_config()
    email = get_email_config()

    updated = {}

    # Jira updates
    if payload.jira_url is not None:
        updated["JIRA_URL"] = payload.jira_url
    if payload.jira_email is not None:
        updated["JIRA_EMAIL"] = payload.jira_email
    if payload.jira_project_key is not None:
        updated["JIRA_PROJECT_KEY"] = payload.jira_project_key
    
    if payload.jira_api_token is not None:
        if not _is_masked(payload.jira_api_token):
            updated["JIRA_API_TOKEN"] = payload.jira_api_token
        elif jira.get("JIRA_API_TOKEN"):
            # Preserve existing token
            updated["JIRA_API_TOKEN"] = existing_file.get("JIRA_API_TOKEN") or jira.get("JIRA_API_TOKEN")

    # Email updates
    if payload.email_address is not None:
        updated["EMAIL_ADDRESS"] = payload.email_address
    
    if payload.email_app_password is not None:
        if not _is_masked(payload.email_app_password):
            updated["EMAIL_APP_PASSWORD"] = payload.email_app_password
        elif email.get("EMAIL_APP_PASSWORD"):
            # Preserve existing password
            updated["EMAIL_APP_PASSWORD"] = existing_file.get("EMAIL_APP_PASSWORD") or email.get("EMAIL_APP_PASSWORD")

    save_config_file(updated)
    return {"status": "success", "message": "Integrations configuration updated successfully"}


# ---------------------------------------------------
# Test Connection Endpoints
# ---------------------------------------------------

@router.post("/jira/test")
def test_jira_connection(payload: JiraTestRequest):
    """
    Perform a real connection test to the Jira instance using basic auth.
    """
    # If the user passed the placeholder, use the saved token instead
    api_token = payload.jira_api_token
    if _is_masked(api_token):
        saved_jira = get_jira_config()
        api_token = saved_jira.get("JIRA_API_TOKEN")
        if not api_token:
            raise HTTPException(status_code=400, detail="Jira API Token is missing")

    url = f"{payload.jira_url.rstrip('/')}/rest/api/3/project/{payload.jira_project_key}"
    logger.info("Testing Jira connection to %s", url)

    try:
        response = requests.get(
            url=url,
            headers={"Accept": "application/json"},
            auth=HTTPBasicAuth(payload.jira_email, api_token),
            timeout=10,
        )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Jira server timed out (10s)")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Failed to connect to Jira instance. Check URL.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    if response.status_code == 200:
        try:
            proj_data = response.json()
            proj_name = proj_data.get("name", payload.jira_project_key)
            return {
                "status": "success",
                "message": f"Successfully connected to Jira Project: {proj_name}"
            }
        except Exception:
            return {
                "status": "success",
                "message": "Connected successfully (Response content type was not JSON)"
            }
    elif response.status_code == 401:
        raise HTTPException(status_code=401, detail="Authentication failed. Check Jira Email and API Token.")
    elif response.status_code == 403:
        raise HTTPException(status_code=403, detail="Forbidden. Check API token permissions/access rights.")
    elif response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"Project Key '{payload.jira_project_key}' not found or URL is invalid."
        )
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Jira API returned HTTP {response.status_code}: {response.text[:200]}"
        )


@router.post("/email/test")
def test_email_connection(payload: EmailTestRequest):
    """
    Perform a real connection test to Gmail SMTP and send a verification test email.
    """
    # If the user passed the placeholder, use the saved password instead
    app_password = payload.email_app_password
    if _is_masked(app_password):
        saved_email = get_email_config()
        app_password = saved_email.get("EMAIL_APP_PASSWORD")
        if not app_password:
            raise HTTPException(status_code=400, detail="Email App Password is missing")

    logger.info("Testing Gmail SMTP connection for %s", payload.email_address)

    # Build the email
    email = EmailMessage()
    email["From"] = payload.email_address
    email["To"] = payload.test_recipient
    email["Subject"] = "SupportPilot - Email Integration Test"
    email.set_content(
        "Hello!\n\n"
        "This is an automated test email sent from SupportPilot to verify your "
        "SMTP email settings.\n\n"
        "If you received this email, your SMTP configuration is correct and active!\n\n"
        "Regards,\n"
        "SupportPilot Orchestrator Daemon"
    )

    try:
        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as smtp:
            smtp.login(payload.email_address, app_password)
            smtp.send_message(email)
        
        return {
            "status": "success",
            "message": f"SMTP test successful. Verification email sent to {payload.test_recipient}"
        }
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=401, detail="Authentication failed. Check Email Address and App Password.")
    except (smtplib.SMTPConnectError, TimeoutError) as socket_timeout_errors:
        raise HTTPException(status_code=504, detail="SMTP server connection timed out. Check internet access.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMTP Error: {str(e)}")
