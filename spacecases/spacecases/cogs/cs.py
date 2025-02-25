import discord
from discord.ext import commands
from spacecases.bot import SpaceCasesBot
from spacecases.commands.cs.item import item, item_name_autocomplete
from spacecases.commands.cs.open import open, open_name_autocomplete
from spacecases.commands.cs.containers import containers
from spacecases.commands.cs.upgrade import upgrade
from spacecases.autocomplete import inventory_item_autocomplete
from typing import Optional


class Unbox(commands.Cog):
    def __init__(self, bot: SpaceCasesBot):
        self.bot = bot

    @discord.app_commands.command(name="item", description="Inspect an item")
    @discord.app_commands.describe(name="Name of the item you want to inspect")
    async def item(self, interaction: discord.Interaction, name: str) -> None:
        await item(self.bot, interaction, name)

    @item.autocomplete("name")
    async def item_autocomplete(
        self, _: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice]:
        return await item_name_autocomplete(self.bot, current)

    @discord.app_commands.command(name="open", description="Open a container")
    @discord.app_commands.describe(name="Name of the container you want to open")
    async def open(self, interaction: discord.Interaction, name: str) -> None:
        await open(self.bot, interaction, name)

    @open.autocomplete("name")
    async def open_autocomplete(
        self, _: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice]:
        return await open_name_autocomplete(self.bot, current)

    @discord.app_commands.command(
        name="containers", description="View all available containers"
    )
    @discord.app_commands.choices(
        container_type=[
            discord.app_commands.Choice(name="Cases", value="cases"),
            discord.app_commands.Choice(
                name="Souvenir Packages", value="souvenirpackages"
            ),
            discord.app_commands.Choice(
                name="Sticker Capsules", value="stickercapsules"
            ),
        ]
    )
    async def containers(
        self,
        interaction: discord.Interaction,
        container_type: Optional[discord.app_commands.Choice[str]],
    ) -> None:
        await containers(self.bot, interaction, container_type)

    @discord.app_commands.command(
        name="upgrade",
        description="Take a chance to upgrade a skin at risk of losing it",
    )
    @discord.app_commands.describe(item_id="ID of the item to upgrade")
    async def upgrade(
        self, interaction: discord.Interaction, item_id: int, target_item: str
    ) -> None:
        await upgrade(self.bot, interaction, item_id, target_item)

    @upgrade.autocomplete("item_id")
    async def upgrade_item_id_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice]:
        return await inventory_item_autocomplete(self.bot, interaction.user, current)

    @upgrade.autocomplete("target_item")
    async def upgrade_target_item_autocomplete(
        self, _: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice]:
        return await item_name_autocomplete(self.bot, current)


async def setup(bot: SpaceCasesBot) -> None:
    await bot.add_cog(Unbox(bot))
