import discord
from spacecases.bot import SpaceCasesBot
from spacecases.database import BALANCE
from spacecases.strutils import currency_str_format
from typing import Optional
from spacecases.exceptions import UserNotRegisteredError


async def balance(
    bot: SpaceCasesBot, interaction: discord.Interaction, user: Optional[discord.User]
) -> None:
    if user is None:
        target_user = interaction.user
    else:
        target_user = user

    rows = await bot.db.fetch_from_file(BALANCE, target_user.id)
    if len(rows) > 0:
        balance = rows[0]["balance"]
        e = discord.Embed(
            title=f"{target_user.display_name}'s Balance",
            color=discord.Color.dark_theme(),
        )
        e.set_thumbnail(url=target_user.display_avatar.url)
        e.add_field(name="Current Balance", value=currency_str_format(balance))
        await interaction.response.send_message(embed=e)
    else:
        raise UserNotRegisteredError(target_user)
