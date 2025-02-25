import discord
from discord.ui import Item
from typing import Optional, Any


class SpaceCasesView(discord.ui.View):
    """View that will handle exceptions like the bot does"""

    def __init__(self, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: Item[Any]
    ) -> None:
        # this is disgusting
        from .embed import send_exception_embed

        await send_exception_embed(interaction, error, True)
