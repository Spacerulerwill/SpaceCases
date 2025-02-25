import discord
from spacecases.bot import SpaceCasesBot
from spacecases.leaderboard import Leaderboard
from spacecases.ui.embed import send_err_embed, send_success_embed
from typing import Literal


async def ranking(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    type: Literal["global", "local"],
) -> None:
    if type == "global":
        leaderboard = bot.global_leaderboard
        leaderboard_title = "the global leaderboard"
    elif type == "local":
        if not interaction.guild:
            await send_err_embed(
                interaction, "You can only access a local leaderboard in a **guild**"
            )
            return
        leaderboard = bot.guild_leaderboards.get(interaction.guild.id, Leaderboard({}))
        leaderboard_title = f"{interaction.guild.name}'s leaderboard"

    if len(leaderboard) == 0:
        await send_err_embed(
            interaction, f"**No data** found for **{leaderboard_title}**"
        )
        return

    try:
        leaderboard_entry = leaderboard.entries[interaction.user.id]
        await send_success_embed(
            interaction,
            f"You are at position **#{leaderboard_entry.position}** on **{leaderboard_title}**",
        )
    except KeyError:
        await send_err_embed(
            interaction, f"You **do not** appear on **{leaderboard_title}**"
        )
