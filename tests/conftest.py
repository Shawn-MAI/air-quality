"""Shared fixtures for tests that need the local stack."""

import os

import psycopg
import pytest


@pytest.fixture(scope="session")
def app_conn():
    try:
        conn = psycopg.connect(
            host="127.0.0.1",
            port=os.environ["POSTGRES_PORT"],
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["APP_DB_USER"],
            password=os.environ["APP_DB_PASSWORD"],
            connect_timeout=5,
        )
    except psycopg.OperationalError as exc:
        pytest.fail(f'Stack is not running. Run "make up" first. ({exc})', pytrace=False)
    yield conn
    conn.close()
