import discord
from typing import Literal
from itertools import batched
from spacecases.bot import SpaceCasesBot
from spacecases.ui.embed import send_err_embed
from spacecases.leaderboard import Leaderboard
from spacecases.strutils import currency_str_format
from spacecases.ui.embed import send_paginated_embed

LEADERBOARD_PAGE_SIZE = 10


async def leaderboard(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    type: Literal["global", "local"],
    page: int,
) -> None:
    if page < 0:
        await send_err_embed(interaction, "**page** cannot be less than **one**")
        return

    if type == "global":
        leaderboard = bot.global_leaderboard
        leaderboard_title = "Global Leaderboard"
    elif type == "local":
        if not interaction.guild:
            await send_err_embed(
                interaction, "You can only access a local leaderboard in a **guild**"
            )
            return
        leaderboard = bot.guild_leaderboards.get(interaction.guild.id, Leaderboard({}))
        leaderboard_title = f"{interaction.guild.name}'s Leaderboard"

    # no leaderboard data found
    if len(leaderboard) == 0:
        await send_err_embed(
            interaction, f"**No data** found for **{leaderboard_title}**"
        )
        return

    embeds = []
    page_count = len(leaderboard) // LEADERBOARD_PAGE_SIZE + 1
    # check we have a valid page
    if page > page_count:
        await send_err_embed(
            interaction, f"**{leaderboard_title}** does not have a page **{page}**"
        )
        return

    # generate embeds
    for page, batch in enumerate(
        batched(leaderboard.entries.values(), LEADERBOARD_PAGE_SIZE), start=1
    ):
        e = discord.Embed(
            title=f"{leaderboard_title} - Page {page}/{page_count}",
            color=discord.Color.dark_theme(),
        )
        lines = []
        for elem in batch:
            lines.append(
                f"**{elem.position}**) {elem.name} - **{currency_str_format(elem.inventory_value)}**"
            )
        e.description = "\n".join(lines)
        e.set_footer(text="Leaderboards update every 5 minutes")
        embeds.append(e)

    await send_paginated_embed(interaction, embeds, page)
