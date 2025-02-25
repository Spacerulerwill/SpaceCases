import discord
from spacecases.ui.embed import create_err_embed


class PaginatedEmbedView(discord.ui.View):
    def __init__(
        self,
        interaction: discord.Interaction,
        pages: list[discord.Embed],
        start_page: int = 0,
    ):
        self.interaction = interaction
        self.pages = pages
        self.page = start_page
        super().__init__(timeout=30)

    @discord.ui.button(emoji="◀", style=discord.ButtonStyle.gray)
    async def left_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message(
                embed=create_err_embed("This is **not** your button!"), ephemeral=True
            )
            return
        self.page = (self.page - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.page])

    @discord.ui.button(emoji="▶", style=discord.ButtonStyle.gray)
    async def right_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message(
                embed=create_err_embed("This is **not** your button!"), ephemeral=True
            )
            return
        self.page = (self.page + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.page])

    async def on_timeout(self) -> None:
        message = await self.interaction.original_response()
        await message.edit(embed=self.pages[self.page], view=None)


async def send_paginated_embed(
    interaction: discord.Interaction, pages: list[discord.Embed], start_page: int = 1
) -> None:
    if len(pages) == 0:
        raise ValueError("Can't provide 0 embed pages")
    else:
        await interaction.response.send_message(
            embed=pages[start_page - 1],
            view=PaginatedEmbedView(interaction, pages, start_page - 1),
        )
