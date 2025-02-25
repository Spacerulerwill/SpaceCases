import discord
from spacecases.bot import SpaceCasesBot
from spacecases.database import CLAIM
from spacecases.ui.embed import send_err_embed
from spacecases.strutils import currency_str_format
from spacecases.exceptions import UserNotRegisteredError


async def claim(bot: SpaceCasesBot, interaction: discord.Interaction) -> None:
    rows = await bot.db.fetch_from_file(CLAIM, interaction.user.id)
    if len(rows) == 0:
        raise UserNotRegisteredError(interaction.user)

    row = rows[0]
    if row["claimed"]:
        e = discord.Embed(
            title="You have successfully claimed your daily reward!",
            color=discord.Color.green(),
        )
        new_balance = row["balance"]
        amount = row["amount"]
        claim_streak = row["new_streak"]
        e.set_thumbnail(url=interaction.user.display_avatar.url)
        e.add_field(name="New Balance", value=currency_str_format(new_balance))
        e.add_field(name="Amount", value=currency_str_format(amount))
        e.add_field(name="Claim Streak ️‍🔥", value=str(claim_streak))
        e.set_footer(text="You can claim again tomorrow")
        await interaction.response.send_message(embed=e)
    else:
        await send_err_embed(interaction, "You have **already** claimed today!")
