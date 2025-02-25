import discord
from discord.ui import Button, View
from typing import Callable, Coroutine, Optional, Any
from . import send_err_embed, create_err_embed
from .. import SpaceCasesView

type ButtonCallbackType = Callable[[discord.Interaction], Coroutine[Any, Any, None]]


class YesNoEmbedView(SpaceCasesView):
    def __init__(
        self,
        on_yes: ButtonCallbackType,
        on_no: ButtonCallbackType,
        interaction: discord.Interaction,
        timeout: Optional[float] = 30,
    ):
        self.on_yes = on_yes
        self.on_no = on_no
        self.responded = False
        self.interaction = interaction
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: Button[View]) -> None:
        if interaction.user != self.interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        await self.on_yes(interaction)
        self.responded = True

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: Button[View]) -> None:
        if interaction.user != self.interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        await self.on_no(interaction)
        self.responded = True

    async def on_timeout(self) -> None:
        if self.responded:
            return
        message = await self.interaction.original_response()
        new_embed = create_err_embed("You did **not** respond in time")
        await message.edit(embed=new_embed, view=None)


async def yes_no_embed(
    interaction: discord.Interaction,
    msg_content: str,
    on_yes: ButtonCallbackType,
    on_no: ButtonCallbackType,
    timeout: Optional[float] = 30,
) -> None:
    embed = discord.Embed(description=msg_content, color=discord.Color.dark_theme())
    await interaction.response.send_message(
        embed=embed, view=YesNoEmbedView(on_yes, on_no, interaction, timeout)
    )
