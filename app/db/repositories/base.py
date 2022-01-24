from typing import Optional
from asyncpg.connection import Connection


class BaseRepository:
    def __init__(self, conn: Optional[Connection] = None) -> None:
        self._conn = conn

    @property
    def connection(self) -> Connection:
        # pragma: prisma refactor
        conn = self._conn
        assert (
            conn is not None
        ), "Attemped to retrieve connection from a connection-less repository"
        return conn
