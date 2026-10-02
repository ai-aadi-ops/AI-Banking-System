import os
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL


def get_engine():
    db_url = os.getenv("DATABASE_URL") or DATABASE_URL

    # If configured with Docker hostname 'postgres' but running outside Docker, verify connectivity
    if db_url and "@postgres:" in db_url:
        can_resolve = False
        try:
            socket.gethostbyname("postgres")
            can_resolve = True
        except Exception:
            can_resolve = False

        if not can_resolve:
            # Check if localhost:5433 is listening before attempting connection
            local_listening = False
            try:
                with socket.create_connection(("127.0.0.1", 5433), timeout=0.5):
                    local_listening = True
            except Exception:
                local_listening = False

            if local_listening:
                alt_url = db_url.replace("@postgres:5432", "@localhost:5433")
                return create_engine(alt_url)
            else:
                print("Notice: Using SQLite fallback: finance.db")
                db_url = "sqlite:///./finance.db"

    if not db_url:
        db_url = "sqlite:///./finance.db"

    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, connect_args=connect_args)


engine = get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
