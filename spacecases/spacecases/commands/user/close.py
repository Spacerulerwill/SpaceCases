import discord
from spacecases.bot import SpaceCasesBot
from spacecases.database import DOES_USER_EXIST, CLOSE
from spacecases.exceptions import UserNotRegisteredError
from spacecases.ui.embed import (
    yes_no_embed,
    create_success_embed,
    create_err_embed,
)

RESPONSE_TIME = 30


async def close(bot: SpaceCasesBot, interaction: discord.Interaction) -> None:
    # check if user has an account to delete
    does_user_exist = (
        await bot.db.fetch_from_file(DOES_USER_EXIST, interaction.user.id)
    )[0]["exists"]
    if not does_user_exist:
        raise UserNotRegisteredError(interaction.user)

    async def on_no(interaction: discord.Interaction) -> None:
        new_embed = create_err_embed("Account deletion **cancelled**")
        await interaction.response.edit_message(embed=new_embed, view=None)

    async def on_yes(interaction: discord.Interaction) -> None:
        rows = await bot.db.fetch_from_file(CLOSE, interaction.user.id)
        if len(rows) > 0:
            new_embed = create_success_embed(
                "You have successfully **deleted** your account"
            )
            await interaction.response.edit_message(embed=new_embed, view=None)
            bot.user_count -= 1
        else:
            new_embed = create_err_embed("Your account is **already** deleted")
            await interaction.response.edit_message(embed=new_embed, view=None)

    await yes_no_embed(
        interaction,
        f"Are you **sure** you want to close your account? This action is **permanent** and **irreversible**. You have **{RESPONSE_TIME} seconds** to respond",
        on_yes,
        on_no,
        RESPONSE_TIME,
    )
