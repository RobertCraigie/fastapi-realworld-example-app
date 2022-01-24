import asyncio
import inspect
from os import environ
from typing import AsyncIterator

import pytest
from asyncpg.pool import Pool
from fastapi import FastAPI
from httpx import AsyncClient

from prisma import get_client
from prisma.errors import ClientNotRegisteredError

from app.db.repositories.articles import ArticlesRepository
from app.db.repositories.users import UsersRepository
from app.models.domain.articles import Article
from app.models.domain.users import UserInDB
from app.services import jwt

environ["APP_ENV"] = "test"


@pytest.fixture(scope="session")
def app() -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture(scope="session")
async def initialized_app(app: FastAPI) -> AsyncIterator[FastAPI]:
    await app.router.startup()
    yield app


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


@pytest.fixture
def pool(initialized_app: FastAPI) -> Pool:
    return initialized_app.state.pool


@pytest.fixture
async def client(initialized_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        app=initialized_app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def authorization_prefix() -> str:
    from app.core.config import get_app_settings

    settings = get_app_settings()
    jwt_token_prefix = settings.jwt_token_prefix

    return jwt_token_prefix


@pytest.fixture
async def test_user() -> UserInDB:
    return await UsersRepository().create_user(
        email="test@test.com", password="password", username="username"
    )


@pytest.fixture
async def test_article(test_user: UserInDB, pool: Pool) -> Article:
    async with pool.acquire() as connection:
        articles_repo = ArticlesRepository(connection)
        return await articles_repo.create_article(
            slug="test-slug",
            title="Test Slug",
            description="Slug for tests",
            body="Test " * 100,
            author=test_user,
            tags=["tests", "testing", "pytest"],
        )


@pytest.fixture
def token(test_user: UserInDB) -> str:
    return jwt.create_access_token_for_user(test_user, environ["SECRET_KEY"])


@pytest.fixture
def authorized_client(
    client: AsyncClient, token: str, authorization_prefix: str
) -> AsyncClient:
    client.headers = {
        "Authorization": f"{authorization_prefix} {token}",
        **client.headers,
    }
    return client


@pytest.fixture(autouse=True)
async def _cleanup_prisma() -> None:
    try:
        client = get_client()
    except ClientNotRegisteredError:
        return

    if not client.is_connected():
        await client.connect()

    # TODO: this should be included in Prisma
    async with client.batch_() as batcher:
        for _, item in inspect.getmembers(batcher):
            if item.__class__.__name__.endswith("Actions"):
                item.delete_many()
