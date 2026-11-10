import os

import pytest

TEST_DB = os.environ.get("TEST_DATABASE_URL")
if TEST_DB:
    # Must be set before the app (and its engine) is imported.
    os.environ["DATABASE_URL"] = TEST_DB
    os.environ.pop("API_TOKEN", None)


def pytest_collection_modifyitems(config, items):
    if TEST_DB:
        return
    skip = pytest.mark.skip(reason="TEST_DATABASE_URL not set")
    for item in items:
        if "db" in item.keywords:
            item.add_marker(skip)


def pytest_configure(config):
    config.addinivalue_line("markers", "db: needs a real Postgres (TEST_DATABASE_URL)")


@pytest.fixture(scope="session")
async def client():
    from alembic.config import Config
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    from alembic import command

    reset = create_async_engine(TEST_DB)
    async with reset.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    await reset.dispose()

    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "alembic"))
    cfg.attributes["database_url"] = TEST_DB
    import asyncio

    await asyncio.to_thread(command.upgrade, cfg, "head")

    from app.db import SessionLocal, engine
    from app.main import app
    from app.seed.__main__ import seed

    async with SessionLocal() as session:
        await seed(session)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    await engine.dispose()
