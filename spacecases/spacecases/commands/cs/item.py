import discord
import random
from itertools import islice
from spacecases.bot import SpaceCasesBot
from spacecases.strutils import currency_str_format
from spacecases.exceptions import ItemDoesNotExistError
from spacecases.ui.embed import get_rarity_embed_color
from common import (
    remove_skin_name_formatting,
    SkinMetadatum,
    StickerMetadatum,
)


async def item(bot: SpaceCasesBot, interaction: discord.Interaction, name: str) -> None:
    # remove our items name formatting
    unformatted_name = remove_skin_name_formatting(name)
    # check our item exists
    try:
        item_metadata = bot.item_metadata[unformatted_name]
    except KeyError:
        raise ItemDoesNotExistError(name)
    # create the embed to send to the user
    item_metadata = bot.item_metadata[unformatted_name]
    e = discord.Embed(
        title=item_metadata.formatted_name,
        color=get_rarity_embed_color(item_metadata.rarity),
    )
    e.set_image(url=item_metadata.image_url)
    e.add_field(name="Price", value=currency_str_format(item_metadata.price))
    # if its a skin, it has a rarity and float range
    if isinstance(item_metadata, SkinMetadatum):
        e.add_field(name="Rarity", value=item_metadata.rarity.get_name_for_skin())
        e.add_field(
            name="Float Range",
            value=f"{item_metadata.min_float:.2f} - {item_metadata.max_float:.2f}",
        )
        e.description = item_metadata.description
    # if its a sticker, only a rarity
    elif isinstance(item_metadata, StickerMetadatum):
        e.add_field(
            name="Rarity", value=item_metadata.rarity.get_name_for_regular_item()
        )
    await interaction.response.send_message(embed=e)


async def item_name_autocomplete(
    bot: SpaceCasesBot, current: str
) -> list[discord.app_commands.Choice]:
    unformatted_current = remove_skin_name_formatting(current)
    if len(unformatted_current) == 0:
        options = random.sample(bot.item_unformatted_names, 25)
    else:
        options = list(islice(bot.item_trie.keys(unformatted_current), 25))

    return [
        discord.app_commands.Choice(
            name=bot.item_metadata[unformatted_name].formatted_name,
            value=bot.item_metadata[unformatted_name].formatted_name,
        )
        for unformatted_name in options
    ]
