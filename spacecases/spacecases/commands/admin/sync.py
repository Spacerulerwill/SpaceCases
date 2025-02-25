import discord
from spacecases.bot import SpaceCasesBot
from spacecases.ui.embed import send_success_embed, send_err_embed
from typing import Literal

type SyncType = Literal["global"] | Literal["local"]


async def sync(
    bot: SpaceCasesBot, interaction: discord.Interaction, type: SyncType
) -> None:
    if interaction.user.id != bot.owner_id:
        await send_err_embed(
            interaction, "You do **not** have permission to use this command."
        )
        return
    if type == "global":
        await bot.sync_commands(None)
    elif type == "local":
        if interaction.guild:
            await bot.sync_commands(interaction.guild.id)
        else:
            await send_err_embed(
                interaction, "You can only sync locally in a **guild**"
            )
    await send_success_embed(interaction, "Commands **successfully** synced")
