from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---- Database connection details (from Member 1) ----
DB_USER = "root"
DB_PASSWORD = "Sadiyax@402"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "supportpilot"

from urllib.parse import quote_plus

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Provides a DB session to each request, closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()