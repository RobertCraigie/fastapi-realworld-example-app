import asyncpg
from fastapi import FastAPI
from loguru import logger
from prisma import Client

from app.core.settings.app import AppSettings


# NOTE: we're keeping the old asyncpg connection here to
# make migrating to prisma easier, it will be removed in
# the future


async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to {0}", repr(settings.database_url))

    app.state.pool = await asyncpg.create_pool(
        str(settings.database_url),
        min_size=settings.min_connection_count,
        max_size=settings.max_connection_count,
    )

    # TODO: respect min and max_connection_count
    app.state.prisma = prisma = Client(
        auto_register=True,
        datasource={"url": settings.database_url},
    )
    await prisma.connect()

    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.pool.close()
    await app.state.prisma.disconnect()

    logger.info("Connection closed")
