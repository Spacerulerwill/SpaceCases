import discord
from common import Rarity


def create_embed(
    msg_content: str, color: discord.Color = discord.Color.dark_theme()
) -> discord.Embed:
    return discord.Embed(description=msg_content, color=color)


def create_success_embed(msg_content: str) -> discord.Embed:
    return create_embed(msg_content, discord.Color.green())


def create_err_embed(msg_content: str) -> discord.Embed:
    return create_embed(msg_content, discord.Color.red())


async def send_embed(
    interaction: discord.Interaction,
    msg_content: str,
    color: discord.Color = discord.Color.dark_theme(),
    ephemeral: bool = False,
) -> None:
    embed = create_embed(msg_content, color)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


async def send_success_embed(
    interaction: discord.Interaction, msg_content: str, ephemeral: bool = False
) -> None:
    embed = create_success_embed(msg_content)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


async def send_err_embed(
    interaction: discord.Interaction, msg_content: str, ephemeral: bool = False
) -> None:
    embed = create_err_embed(msg_content)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


def get_rarity_embed_color(rarity: Rarity) -> int:
    return [0xB0C3D9, 0x5E98D9, 0x4B69FF, 0x8847FF, 0xD32CE6, 0xEB4B4B, 0xE4AE39][
        rarity.value
    ]
