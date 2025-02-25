import os
import json
import asyncio
from dataclasses import dataclass
from dotenv import load_dotenv
from common import (
    get_skin_metadata,
    get_sticker_metadata,
    get_logger,
)
from collections import defaultdict
import aiohttp
import asyncpg

OUTPUT_DIRECTORY = "output"
DEFAULT_ASSET_DOMAIN = "https://assets.spacecases.xyz"

logger = get_logger(__name__)

RETRY_INTERVAL = 60


@dataclass
class Environment:
    bot_token: str
    asset_domain: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str

    @staticmethod
    def load() -> "Environment":
        load_dotenv(override=True)
        return Environment(
            bot_token=os.environ["BOT_TOKEN"],
            asset_domain=os.environ.get("ASSET_DOMAIN", DEFAULT_ASSET_DOMAIN),
            db_user=os.environ["DB_USER"],
            db_password=os.environ["DB_PASSWORD"],
            db_host=os.environ.get("DB_HOST", "localhost"),
            db_port=os.environ.get("DB_PORT", "5432"),
            db_name=os.environ["DB_NAME"],
        )


async def get_guild_ids(bot_token: str) -> list[int]:
    logger.info("Getting guild ids")
    url = "https://discord.com/api/v10/users/@me/guilds"
    headers = {
        "Authorization": f"Bot {bot_token}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            guilds = await response.json()
            return [int(guild["id"]) for guild in guilds]


@dataclass
class GuildMembers:
    guild_id: int
    member_ids: set[int]
    usernames: dict[int, str]


PER_PAGE = 1000


async def get_guild_member_ids(bot_token: str, guild_id: int) -> GuildMembers:
    url = f"https://discord.com/api/v10/guilds/{guild_id}/members?limit=1000"
    headers = {
        "Authorization": f"Bot {bot_token}",
    }
    logger.info(f"Starting member fetch for guild {guild_id}")
    member_ids = set()
    usernames = {}
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                members = await response.json()
                for member in members:
                    is_bot: bool = member["user"].get("bot", False)
                    if is_bot:
                        continue
                    id = int(member["user"]["id"])
                    username: str = member["user"]["username"]
                    member_ids.add(id)
                    usernames[id] = username

                # If we got less than PER_PAGE members, we have fetched all members
                if len(members) < PER_PAGE:
                    logger.info(f"Fetched {len(members)} members")
                    break
                else:
                    logger.info(f"Fetched {PER_PAGE} members")

                # Use pagination (before the last member_id to fetch the next batch)
                last_member_id = members[-1]["user"]["id"]
                url = f"https://discord.com/api/v10/guilds/{guild_id}/members?limit={PER_PAGE}&before={last_member_id}"
    return GuildMembers(guild_id, member_ids, usernames)


async def get_item_prices(asset_domain: str) -> dict[str, int]:
    logger.info("Generating item price table")
    skin_metadata = await get_skin_metadata(asset_domain)
    skin_prices = {
        unformatted_name: datum.price
        for unformatted_name, datum in skin_metadata.items()
    }
    sticker_metadata = await get_sticker_metadata(asset_domain)
    sticker_prices = {
        unformatted_name: datum.price
        for unformatted_name, datum in sticker_metadata.items()
    }
    result = skin_prices | sticker_prices
    logger.info("Item price table generated")
    return result


type Leaderboard = dict[int, int]


async def generate_leaderboard(
    name: str, inventory_values: dict[int, int], usernames: dict[int, str]
) -> None:
    sorted_leaderboard = {
        user_id: {
            "place": place,
            "inventory_value": inventory_value,
            "username": usernames[user_id],
        }
        for place, (user_id, inventory_value) in enumerate(
            sorted(inventory_values.items(), key=lambda item: item[1], reverse=True),
            start=1,
        )
    }
    with open(
        os.path.join(OUTPUT_DIRECTORY, f"{name}.json"),
        "w+",
        encoding="utf-8",
    ) as f:
        json.dump(sorted_leaderboard, f, ensure_ascii=False, indent=4)


async def generate_guild_leaderboard(
    guild_members: GuildMembers, inventory_values: dict[int, int]
) -> None:
    filtered_inventory = {
        id: value
        for id, value in inventory_values.items()
        if id in guild_members.member_ids
    }
    await generate_leaderboard(
        str(guild_members.guild_id), filtered_inventory, guild_members.usernames
    )


async def generate_global_leaderboard(
    inventory_values: dict[int, int], usernames: dict[int, str]
) -> None:
    await generate_leaderboard("global", inventory_values, usernames)


async def get_user_inventory_values(
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: str,
    db_name: str,
    item_prices: dict[str, int],
) -> dict[int, int]:
    logger.info("Fetching items from database")
    # Use asyncpg's context manager to manage the database connection
    conn = await asyncpg.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name,
    )
    rows = await conn.fetch("SELECT * from items;")
    # group all the items by users
    user_inventory_values: dict[int, int] = defaultdict(int)
    for row in rows:
        id = int(row["owner_id"])
        item_price = item_prices[row["name"]]
        user_inventory_values[id] += item_price
    await conn.close()
    return user_inventory_values


async def run() -> None:
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    environment = Environment.load()
    item_prices = await get_item_prices(environment.asset_domain)
    guild_ids = await get_guild_ids(environment.bot_token)
    while True:
        try:
            inventory_values = await get_user_inventory_values(
                environment.db_user,
                environment.db_password,
                environment.db_host,
                environment.db_port,
                environment.db_name,
                item_prices,
            )
            guild_member_tasks = [
                get_guild_member_ids(environment.bot_token, id) for id in guild_ids
            ]
            guild_members = await asyncio.gather(*guild_member_tasks)
            break
        except asyncpg.PostgresError as e:
            logger.warn(
                f"Failed to fetch inventory values: {e}... trying again in {RETRY_INTERVAL} seconds"
            )
            await asyncio.sleep(RETRY_INTERVAL)
            continue

    # all usernames (needed for global leaderboard)
    all_usernames: dict[int, str] = {}
    for guild_member in guild_members:
        all_usernames |= guild_member.usernames

    # generate all leaderboards
    guild_leaderboard_tasks = [
        generate_global_leaderboard(inventory_values, all_usernames)
    ] + [generate_guild_leaderboard(guild, inventory_values) for guild in guild_members]
    asyncio.gather(*guild_leaderboard_tasks)


if __name__ == "__main__":
    asyncio.run(run())
