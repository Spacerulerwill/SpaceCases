import discord
from discord.ext import commands
from spacecases.bot import SpaceCasesBot
from spacecases.commands.admin.sync import sync, SyncType
from typing import cast


class Admin(commands.Cog):
    def __init__(self, bot: SpaceCasesBot):
        self.bot = bot

    @discord.app_commands.command(name="sync", description="Synchronise slash commands")
    @discord.app_commands.choices(
        type=[
            discord.app_commands.Choice(name="Global", value="global"),
            discord.app_commands.Choice(name="Local", value="local"),
        ]
    )
    async def sync(
        self, interaction: discord.Interaction, type: discord.app_commands.Choice[str]
    ) -> None:
        value = cast(SyncType, type.value)
        await sync(self.bot, interaction, value)


async def setup(bot: SpaceCasesBot) -> None:
    await bot.add_cog(Admin(bot))
