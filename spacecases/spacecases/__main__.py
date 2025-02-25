import os
import discord
import asyncio
from contextlib import suppress
from spacecases.database import Database
from spacecases.bot import SpaceCasesBot
from spacecases.environment import Environment


async def main(environment: Environment) -> None:
    async with await Database.create(
        environment.db_user,
        environment.db_password,
        environment.db_name,
        environment.db_host,
        environment.db_port,
    ) as db:
        bot = SpaceCasesBot(
            db,
            environment.asset_domain,
            environment.leaderboards_domain,
            environment.owner_id,
        )
        try:
            await bot.start(environment.bot_token)
        finally:
            await bot.close()


if __name__ == "__main__":
    # create folder to keep track of bot user slash command sync states
    os.makedirs("synced", exist_ok=True)
    # don't use the root logger, you bastard
    discord.utils.setup_logging(root=False)
    environment = Environment.load()
    # allows ctrl+c close cleanly
    with suppress(KeyboardInterrupt):
        asyncio.run(main(environment))
