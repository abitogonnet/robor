import os
import sqlite3
from contextlib import contextmanager
from urllib.parse import urlparse


def get_db_url(env_name: str) -> str | None:
    return os.environ.get(env_name)


def is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite://") or url.startswith("sqlite:///")


def is_postgres_url(url: str) -> bool:
    return url.startswith("postgres://") or url.startswith("postgresql://")


def parse_sqlite_path(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme == "sqlite" and parsed.path:
        return parsed.path
    raise ValueError("Invalid SQLite URL")


def normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url
    if is_sqlite_url(url):
        return url
    raise ValueError("Unsupported DB URL scheme")


def has_db(env_name: str) -> bool:
    return bool(get_db_url(env_name))

@contextmanager
def get_connection(env_name: str):
    db_url = get_db_url(env_name)
    if not db_url:
        raise RuntimeError(f"Database URL not configured for {env_name}")
    db_url = normalize_db_url(db_url)
    if is_sqlite_url(db_url):
        path = parse_sqlite_path(db_url)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    elif is_postgres_url(db_url):
        try:
            import psycopg2
        except ImportError as exc:
            raise RuntimeError("psycopg2 is required for PostgreSQL integration") from exc
        conn = psycopg2.connect(db_url)
        try:
            yield conn
        finally:
            conn.close()
    else:
        raise ValueError("Unsupported database URL")
