import discord
from discord.ext import commands
from spacecases.bot import SpaceCasesBot
from spacecases.commands.user.close import close
from spacecases.commands.user.register import register
from spacecases.commands.user.balance import balance
from spacecases.commands.user.transfer import transfer
from spacecases.commands.user.claim import claim
from spacecases.commands.user import inventory, sell
from spacecases.commands.user.leaderboard import leaderboard
from spacecases.commands.user.ranking import ranking
from typing import Optional, Literal


class User(commands.Cog):
    def __init__(self, bot: SpaceCasesBot):
        self.bot = bot

    @discord.app_commands.command(
        name="register", description="Register for a SpaceCases account"
    )
    async def register(self, interaction: discord.Interaction) -> None:
        await register(self.bot, interaction)

    @discord.app_commands.command(
        name="close", description="Close your SpaceCases account"
    )
    async def close(self, interaction: discord.Interaction) -> None:
        await close(self.bot, interaction)

    @discord.app_commands.command(
        name="balance", description="Check your SpaceCases account balance"
    )
    @discord.app_commands.describe(
        user="The user whose balance you want to check. Defaults to your own balance if not specified."
    )
    async def balance(
        self, interaction: discord.Interaction, user: Optional[discord.User]
    ) -> None:
        await balance(self.bot, interaction, user)

    @discord.app_commands.command(
        name="transfer", description="Transfer balance to another SpaceCases account"
    )
    @discord.app_commands.describe(
        amount="Amount of balance to transfer", recipient="Recipient of the balance"
    )
    async def transfer(
        self, interaction: discord.Interaction, amount: str, recipient: discord.User
    ) -> None:
        await transfer(self.bot, interaction, amount, recipient)

    @discord.app_commands.command(name="claim", description="Claim your daily balance")
    async def claim(self, interaction: discord.Interaction) -> None:
        await claim(self.bot, interaction)

    @discord.app_commands.command(
        name="inventory",
        description="View a user's inventory or inspect a specific item.",
    )
    @discord.app_commands.describe(
        user="The user whose inventory you want to view.",
        item_id="The id of the specific item to inspect in the user's inventory.",
    )
    async def inventory(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.User],
        item_id: Optional[int],
    ) -> None:
        await inventory.inventory(self.bot, interaction, user, item_id)

    @inventory.autocomplete("item_id")
    async def inventory_item_id_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice]:
        return await inventory.item_id_autocomplete(self.bot, interaction, current)

    @discord.app_commands.command(
        name="sell",
        description="Sell an item from your inventory.",
    )
    @discord.app_commands.describe(
        item_id="The id of the item you want to sell.",
    )
    async def sell(self, interaction: discord.Interaction, item_id: int) -> None:
        await sell.sell(self.bot, interaction, item_id)

    @sell.autocomplete("item_id")
    async def sell_item_id_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice]:
        return await sell.item_id_autocomplete(self.bot, interaction, current)

    @discord.app_commands.command(
        name="leaderboard",
        description="View a leaderboard.",
    )
    @discord.app_commands.describe(
        type="Whether to view the global or server leaderboard"
    )
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        type: Literal["global", "local"] = "local",
        page: int = 1,
    ) -> None:
        await leaderboard(self.bot, interaction, type, page)

    @discord.app_commands.command(
        name="ranking", description="View your ranking on a leaderboard"
    )
    @discord.app_commands.describe(
        type="Whether to view your ranking on the global or server leaderboard"
    )
    async def ranking(
        self,
        interaction: discord.Interaction,
        type: Literal["global", "local"] = "local",
    ) -> None:
        await ranking(self.bot, interaction, type)


async def setup(bot: SpaceCasesBot) -> None:
    await bot.add_cog(User(bot))
