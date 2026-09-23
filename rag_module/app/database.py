"""
SupportPilot AI

Database Configuration

Creates the SQLAlchemy engine,
session factory, and Base class.
"""

from __future__ import annotations

import os
import logging
from collections.abc import Generator
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Load Environment Variables
load_dotenv()

# Database Configuration
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Root@123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "supportpilot")

primary_url = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Try MySQL first, fallback to SQLite if MySQL is offline
try:
    test_engine = create_engine(primary_url, connect_args={"connect_timeout": 3}, pool_pre_ping=True)
    with test_engine.connect() as conn:
        logger.info("Successfully connected to MySQL database.")
    DATABASE_URL = primary_url
    engine = test_engine
except Exception as err:
    # Try alternative password Amael@2004 before fallback
    alt_url = f"mysql+pymysql://{DB_USER}:{quote_plus('Amael@2004')}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    try:
        alt_engine = create_engine(alt_url, connect_args={"connect_timeout": 3}, pool_pre_ping=True)
        with alt_engine.connect() as conn:
            logger.info("Successfully connected to MySQL database with alternative password.")
        DATABASE_URL = alt_url
        engine = alt_engine
    except Exception:
        logger.warning(f"MySQL unavailable ({err}). Falling back to local SQLite database.")
        DATABASE_URL = "sqlite:///./supportpilot.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Base Class
Base = declarative_base()

# Database Dependency
def get_db() -> Generator[Session, None, None]:
    """
    Creates a database session for each request.

    The session is automatically closed after
    the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Public Exports
__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
]