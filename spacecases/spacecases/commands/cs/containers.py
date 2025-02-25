import discord
from itertools import batched, groupby
from typing import Optional
from spacecases.bot import SpaceCasesBot
from spacecases.strutils import currency_str_format
from spacecases.constants import KEY_PRICE
from spacecases.ui.embed import send_err_embed
from spacecases.ui import SpaceCasesView
from dataclasses import dataclass
from common import Container, SkinCase, SouvenirPackage, StickerCapsule

MAX_ITEMS_PER_PAGE = 10


def get_page_title(container: Container) -> str:
    if isinstance(container, SkinCase):
        return "Cases"
    elif isinstance(container, SouvenirPackage):
        return "Souvenir Packages"
    elif isinstance(container, StickerCapsule):
        return "Sticker Capsules"


@dataclass
class PageSection:
    title: str
    items: list[str]


@dataclass
class Page:
    sections: list[PageSection]


def format_container(container: Container) -> str:
    if container.requires_key:
        return f"• {container.formatted_name} - **{currency_str_format(container.price)}** + **{currency_str_format(KEY_PRICE)}** (**{currency_str_format(container.price + KEY_PRICE)}**)"
    else:
        return (
            f"• {container.formatted_name} - **{currency_str_format(container.price)}**"
        )


def get_pages(
    containers: dict[str, Container], container_types: set[type[Container]]
) -> list[Page]:
    all_names = list(
        batched(
            (
                container_unformatted_name
                for container_unformatted_name, container in containers.items()
                if type(container) in container_types
            ),
            MAX_ITEMS_PER_PAGE,
        )
    )

    pages: list[Page] = []
    for group in all_names:
        page_sections = []
        for _, section in groupby(group, key=lambda name: type(containers[name])):
            temp_section = list(section)
            page_title = get_page_title(containers[temp_section[0]])
            page_sections.append(
                PageSection(
                    page_title,
                    [
                        format_container(containers[container])
                        for container in temp_section
                    ],
                )
            )
        pages.append(Page(page_sections))
    return pages


class ContainersView(SpaceCasesView):
    def __init__(self, owner_id: int, pages: list[Page]):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.pages = pages
        self.current_page = 0

    @discord.ui.button(emoji="◀", style=discord.ButtonStyle.gray)
    async def left_arrow_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.owner_id:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        self.current_page = (self.current_page - 1) % len(self.pages)
        await self.update_embed(interaction)

    @discord.ui.button(emoji="▶", style=discord.ButtonStyle.gray)
    async def right_arrow_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.owner_id:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        self.current_page = (self.current_page + 1) % len(self.pages)
        await self.update_embed(interaction)

    def build_embed(self) -> discord.Embed:
        page = self.pages[self.current_page]
        embed = discord.Embed(title=f"Page {self.current_page + 1} / {len(self.pages)}")
        for section in page.sections:
            embed.add_field(
                name=section.title, value="\n".join(section.items), inline=False
            )
        return embed

    async def update_embed(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


async def containers(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    container_type: Optional[discord.app_commands.Choice[str]],
) -> None:
    # Determine which container types to include based on the selection
    selected_container_types: set[type[Container]] = set()
    if container_type is None:
        selected_container_types = selected_container_types.union(
            (SkinCase, SouvenirPackage, StickerCapsule)
        )
    elif container_type.value == "cases":
        selected_container_types.add(SkinCase)
    elif container_type.value == "souvenirpackages":
        selected_container_types.add(SouvenirPackage)
    elif container_type.value == "stickercapsules":
        selected_container_types.add(StickerCapsule)

    # Get pages based on selected container types
    pages = get_pages(bot.containers, selected_container_types)

    # Create the view with the pages
    view = ContainersView(interaction.user.id, pages)
    embed = view.build_embed()
    await interaction.response.send_message(embed=embed, view=view)
