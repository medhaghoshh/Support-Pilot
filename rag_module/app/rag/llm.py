"""
Milestone 3 - Member 5 (RAG / LLM Engineer)

LLM Configuration

This module initializes the Groq Large Language Model
used by the Resolution Agent.

Supports automatic fallback to a secondary model
when the primary model hits its daily token quota (429).

Environment Variables
---------------------
GROQ_API_KEY
    API key for Groq.

GROQ_MODEL
    Primary Groq model name.
    Default:
        openai/gpt-oss-120b

GROQ_FALLBACK_MODEL
    Fallback model used when primary hits rate limits.
    Default:
        llama3-8b-8192

GROQ_TEMPERATURE
    Sampling temperature.
    Default:
        0.0

Exports
-------
llm
    Initialized ChatGroq client with fallback support.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from groq import RateLimitError
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

# ---------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------

load_dotenv()

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)

GROQ_FALLBACK_MODEL = os.getenv(
    "GROQ_FALLBACK_MODEL",
    "llama-3.1-8b-instant",
)

GROQ_TEMPERATURE = float(
    os.getenv(
        "GROQ_TEMPERATURE",
        "0.0",
    )
)

# ---------------------------------------------------
# Validation
# ---------------------------------------------------

if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY environment variable is missing.")
    raise ValueError("GROQ_API_KEY is not set in the environment.")

if not 0.0 <= GROQ_TEMPERATURE <= 2.0:
    logger.error("Invalid GROQ_TEMPERATURE: %.2f", GROQ_TEMPERATURE)
    raise ValueError("GROQ_TEMPERATURE must be between 0.0 and 2.0.")


# ---------------------------------------------------
# LLM Wrapper with Automatic Fallback
# ---------------------------------------------------

class FallbackLLM:
    """
    Wraps two ChatGroq clients.
    Automatically falls back to the secondary model
    when the primary hits a 429 rate limit error.
    """

    def __init__(self, primary: ChatGroq, fallback: ChatGroq) -> None:
        self.primary = primary
        self.fallback = fallback
        self._using_fallback = False

    def invoke(self, prompt):
        # If we already know primary is exhausted, go straight to fallback
        if self._using_fallback:
            logger.info("Using fallback model '%s'.", GROQ_FALLBACK_MODEL)
            return self.fallback.invoke(prompt)
        try:
            return self.primary.invoke(prompt)
        except RateLimitError:
            logger.warning(
                "Primary model '%s' hit daily rate limit (429). "
                "Automatically switching to fallback model '%s'.",
                GROQ_MODEL,
                GROQ_FALLBACK_MODEL,
            )
            self._using_fallback = True
            return self.fallback.invoke(prompt)

    def __getattr__(self, name):
        """Proxy any other attribute to the primary model."""
        return getattr(self.primary, name)


# ---------------------------------------------------
# Initialize Groq LLMs
# ---------------------------------------------------

try:
    _primary_llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=GROQ_TEMPERATURE,
        api_key=GROQ_API_KEY,
    )

    _fallback_llm = ChatGroq(
        model=GROQ_FALLBACK_MODEL,
        temperature=GROQ_TEMPERATURE,
        api_key=GROQ_API_KEY,
    )

    llm = FallbackLLM(primary=_primary_llm, fallback=_fallback_llm)

    logger.info(
        "Groq LLM initialized | Primary: %s | Fallback: %s",
        GROQ_MODEL,
        GROQ_FALLBACK_MODEL,
    )

except Exception as exc:
    logger.exception("Failed to initialize Groq LLM.")
    raise RuntimeError("Unable to initialize the Groq LLM.") from exc


# ---------------------------------------------------
# Public Exports
# ---------------------------------------------------

__all__ = ["llm"]