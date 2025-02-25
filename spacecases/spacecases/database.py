import os
import asyncpg
from typing import Any, Self
from asyncpg import Record
from asyncpg.pool import PoolConnectionProxy
from common import ItemType, get_logger

logger = get_logger(__name__)

# root folder for sql queries
SQL_QUERIES_DIRECTORY = os.path.join("spacecases", "sql")

# where are our migrations stored
MIGRATIONS_DIRECTORY = os.path.join(SQL_QUERIES_DIRECTORY, "migrations")

# file locations for each query
BALANCE = "user/money/balance.sql"
BALANCE_FOR_UPDATE = "user/money/balance_for_update.sql"
CHANGE_BALANCE = "user/money/change_balance.sql"
CLAIM = "user/money/claim.sql"
TRY_DEDUCT_BALANCE = "user/money/try_deduct_balance.sql"
REGISTER = "user/register.sql"
CLOSE = "user/close.sql"
COUNT_USERS = "user/count_users.sql"
DOES_USER_EXIST_FOR_UPDATE = "user/does_user_exist_for_update.sql"
DOES_USER_EXIST = "user/does_user_exist.sql"
ADD_ITEM = "inventory/add_item.sql"
LOCK_ITEMS = "inventory/lock_items.sql"
GET_INVENTORY_CHECK_EXIST = "inventory/get_inventory_check_exist.sql"
GET_INVENTORY = "inventory/get_inventory.sql"
GET_ITEM = "inventory/get_item.sql"
REMOVE_ITEM = "inventory/remove_item.sql"


async def register_type_codecs(conn: PoolConnectionProxy) -> None:
    await conn.set_type_codec(
        "item_type", schema="public", encoder=str, decoder=ItemType, format="text"
    )


class Database:
    @classmethod
    async def create(
        cls, user: str, password: str, database: str, host: str, port: str
    ) -> "Database":
        # create pool
        pool = await asyncpg.create_pool(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port,
        )
        # bruh
        if pool is None:
            logger.error("Database pool is None. Cannot execute queries.")
            raise ConnectionError("Database connection pool is not established.")
        # give them the db instance
        logger.info(
            f"Connected to database '{database}' as user '{user}' on {host}:{port}"
        )
        db_instance = Database(pool)
        await db_instance.run_migrations()
        return db_instance

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def run_migrations(self) -> None:
        async with self.pool.acquire() as connection:
            # create our migrations table if not already present
            await connection.execute(
                """CREATE TABLE IF NOT EXISTS migrations (
                    name TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            logger.info("Running migrationss")
            # run migrations if not already runs
            for entry in sorted(
                os.scandir(MIGRATIONS_DIRECTORY), key=lambda entry: entry.name
            ):
                if not entry.is_file():
                    continue

                # check if migration is already present
                already_present = await connection.fetch(
                    "SELECT 1 FROM migrations WHERE name = $1 LIMIT 1", entry.name
                )

                # skip this migration
                if already_present:
                    logger.info(f"Migration {entry.name} already applied... skipping!")
                    continue

                # apply the migration
                logger.info(f"Applying migration: {entry.name}")
                with open(entry.path, "r") as file:
                    print(entry.path)
                    sql = file.read()
                await connection.execute(sql)

                # add to migration table
                await connection.execute(
                    "INSERT INTO migrations (name) VALUES ($1)", entry.name
                )
                logger.info(f"Applied migration: {entry.name}")

    async def execute(self, query: str, *params: Any) -> None:
        async with self.pool.acquire() as connection:
            await register_type_codecs(connection)
            await connection.execute(query, *params)

    async def execute_from_file(self, filename: str, *params: Any) -> None:
        with open(os.path.join(SQL_QUERIES_DIRECTORY, filename)) as f:
            await self.execute(f.read(), *params)
        logger.debug(
            f"Ran execute query from file: '{filename}' with params: ({', '.join(map(str, params))})"
        )

    async def execute_from_file_with_connection(
        self, filename: str, connection: PoolConnectionProxy, *params: Any
    ) -> None:
        with open(os.path.join(SQL_QUERIES_DIRECTORY, filename)) as f:
            await connection.execute(f.read(), *params)
        logger.debug(
            f"Ran execute query from file: '{filename}' with params: ({', '.join(map(str, params))})"
        )

    async def fetch(self, query: str, *params: Any) -> list[Record]:
        async with self.pool.acquire() as connection:
            await register_type_codecs(connection)
            result = await connection.fetch(query, *params)
        return result

    async def fetch_from_file(self, filename: str, *params: Any) -> list[Record]:
        with open(os.path.join(SQL_QUERIES_DIRECTORY, filename)) as f:
            val = await self.fetch(f.read(), *params)
        logger.debug(
            f"Ran fetch query from file: '{filename}' with params: ({', '.join(map(str, params))})"
        )
        return val

    async def fetch_from_file_with_connection(
        self, filename: str, connection: PoolConnectionProxy, *params: Any
    ) -> list[Record]:
        with open(os.path.join(SQL_QUERIES_DIRECTORY, filename)) as f:
            val = await connection.fetch(f.read(), *params)
        logger.debug(
            f"Ran fetch query from file: '{filename}' with params: ({', '.join(map(str, params))})"
        )
        return val

    async def close(self) -> None:
        await self.pool.close()
        logger.info("Closed database")

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()
