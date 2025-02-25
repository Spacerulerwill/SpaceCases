import json
import discord
from spacecases.bot import SpaceCasesBot
from spacecases.database import GET_INVENTORY_CHECK_EXIST, GET_ITEM
from spacecases.strutils import currency_str_format
from spacecases.autocomplete import inventory_item_autocomplete
from spacecases.ui.embed import get_rarity_embed_color
from spacecases.exceptions import (
    UserNotRegisteredError,
    UserInventoryEmptyError,
    UserDoesNotOwnItemError,
)
from common import SkinMetadatum, ItemType
from typing import Optional, cast, Any


async def inventory(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    user: Optional[discord.User],
    item_id: Optional[int],
) -> None:
    if user is None:
        target_user = interaction.user
    else:
        target_user = user

    if item_id is None:
        await show_user_inventory(interaction, bot, target_user)
    else:
        await show_item_from_user_inventory(interaction, bot, target_user, item_id)


async def show_user_inventory(
    interaction: discord.Interaction,
    bot: SpaceCasesBot,
    user: discord.Member | discord.User,
) -> None:
    user_exists, inventory_capacity, items = (
        await bot.db.fetch_from_file(GET_INVENTORY_CHECK_EXIST, user.id)
    )[0]
    if not user_exists:
        raise UserNotRegisteredError(user)

    # empty inventory
    if len(items) == 0:
        raise UserInventoryEmptyError(user)

    # create embed
    inventory_value = sum(bot.item_metadata[item[2]].price for item in items)
    e = discord.Embed(
        title=f"{user.display_name}'s Inventory",
        description=f"Total Value: **{currency_str_format(inventory_value)}**\nSlots Used: **{len(items)}/{inventory_capacity}**",
    )
    item_strings = []
    for id, _, name, _ in items:
        metadata = bot.item_metadata[name]
        item_strings.append(
            f"{metadata.formatted_name} - **{currency_str_format(metadata.price)}** (ID: **{id}**)"
        )
    e.add_field(name="Items", value="\n".join(item_strings))
    e.set_thumbnail(url=user.display_avatar.url)
    await interaction.response.send_message(embed=e)


async def show_item_from_user_inventory(
    interaction: discord.Interaction,
    bot: SpaceCasesBot,
    user: discord.Member | discord.User,
    item_id: int,
) -> None:
    user_exists: bool
    item: Optional[tuple[str, ItemType, Any]]
    user_exists, item = (await bot.db.fetch_from_file(GET_ITEM, user.id, item_id))[0]
    if not user_exists:
        raise UserNotRegisteredError(user)
    if item is None:
        raise UserDoesNotOwnItemError(user, item_id)
    name, type, details = item
    details = json.loads(details)
    metadatum = bot.item_metadata[name]
    e = discord.Embed(
        title=metadatum.formatted_name, color=get_rarity_embed_color(metadatum.rarity)
    )
    e.add_field(name="Price", value=currency_str_format(metadatum.price))
    e.set_image(url=metadatum.image_url)
    e.set_footer(text=f"Owned by {user.display_name}", icon_url=user.display_avatar)
    match type:
        case ItemType.Skin:
            metadatum = cast(SkinMetadatum, metadatum)
            e.description = metadatum.description
            float_val: float = details["float"]
            e.add_field(name="Float", value=float_val)
            rarity = metadatum.rarity.get_name_for_skin()
        case ItemType.Sticker:
            rarity = metadatum.rarity.get_name_for_skin()
    e.add_field(name="Rarity", value=rarity)
    await interaction.response.send_message(embed=e)


async def item_id_autocomplete(
    bot: SpaceCasesBot, interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice]:
    # what user are they trying to view the inventory of?
    try:
        user = interaction.namespace["user"]
    except KeyError:
        user = interaction.user

    return await inventory_item_autocomplete(bot, user, current)
