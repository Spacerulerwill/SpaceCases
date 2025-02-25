import json
import discord
from spacecases.bot import SpaceCasesBot
from spacecases.autocomplete import inventory_item_autocomplete
from spacecases.ui.embed import yes_no_embed, create_err_embed
from spacecases.strutils import currency_str_format
from spacecases.exceptions import UserDoesNotOwnItemError, UserNotRegisteredError
from spacecases.database import GET_ITEM, REMOVE_ITEM, CHANGE_BALANCE
from common import ItemType
from typing import Optional, Any


async def sell(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    item_id: int,
) -> None:
    user_exists: bool
    item: Optional[tuple[str, ItemType, Any]]
    user_exists, item = (
        await bot.db.fetch_from_file(GET_ITEM, interaction.user.id, item_id)
    )[0]
    if not user_exists:
        raise UserNotRegisteredError(interaction.user)
    if item is None:
        raise UserDoesNotOwnItemError(interaction.user, item_id)
    name, _, details = item
    details = json.loads(details)
    metadatum = bot.item_metadata[name]

    async def on_yes(interaction: discord.Interaction) -> None:
        user_exists, item_removed = (
            await bot.db.fetch_from_file(REMOVE_ITEM, interaction.user.id, item_id)
        )[0]
        if not user_exists:
            raise UserNotRegisteredError(interaction.user)
        if not item_removed:
            raise UserDoesNotOwnItemError(interaction.user, item_id)
        _, balance = (
            await bot.db.fetch_from_file(
                CHANGE_BALANCE, interaction.user.id, metadatum.price
            )
        )[0]
        e = discord.Embed(
            title=f"You have **sold** your {metadatum.formatted_name}",
            description=f"New Balance: **{currency_str_format(balance)}**",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=e)

    async def on_no(interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(
            embed=create_err_embed("Sell cancelled"), view=None
        )

    await yes_no_embed(
        interaction,
        f"Are you **sure** you want to sell your **{metadatum.formatted_name}** for **{currency_str_format(metadatum.price)}?**",
        on_yes,
        on_no,
    )


async def item_id_autocomplete(
    bot: SpaceCasesBot, interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice]:
    return await inventory_item_autocomplete(bot, interaction.user, current)
