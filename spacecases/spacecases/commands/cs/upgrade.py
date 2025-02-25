import discord
import random
import json
from spacecases.bot import SpaceCasesBot
from spacecases.database import Database, GET_ITEM
from spacecases.exceptions import (
    UserNotRegisteredError,
    UserDoesNotOwnItemError,
    ItemDoesNotExistError,
)
from spacecases.ui.embed import send_err_embed
from common import (
    ItemType,
    remove_skin_name_formatting,
    ItemMetadatum,
    SkinMetadatum,
    StickerMetadatum,
)


EXPONENT = 2
MAX_UPGRADE_CHANCE = 0.9


class UpgradeView(discord.ui.View):
    TIMEOUT_TIME = 30

    def __init__(
        self,
        db: Database,
        interaction: discord.Interaction,
        original_embed: discord.Embed,
        start_item_id: int,
        target_item: str,
        target_item_metadatum: ItemMetadatum,
        upgrade_chance: float,
    ):
        self.db = db
        self.interaction = interaction
        self.original_embed = original_embed
        self.start_item_id = start_item_id
        self.target_item = target_item
        self.target_item_metadatum = target_item_metadatum
        self.upgrade_chance = upgrade_chance
        super().__init__(timeout=self.TIMEOUT_TIME)

    @discord.ui.button(label="Upgrade", style=discord.ButtonStyle.green)
    async def upgrade(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user != self.interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return

        if random.random() < self.upgrade_chance:
            new_color = discord.Color.green()
            new_footer = "Upgrade successful"

            # generate new item
            args = []
            if isinstance(self.target_item_metadatum, SkinMetadatum):
                # new float required
                float = self.target_item_metadatum.condition.get_float(
                    self.target_item_metadatum.min_float,
                    self.target_item_metadatum.max_float,
                )
                args = [
                    "skin",
                    self.target_item,
                    json.dumps({"float": float}),
                ]
            elif isinstance(self.target_item_metadatum, StickerMetadatum):
                args = [
                    "sticker",
                    self.target_item,
                    json.dumps({}),
                ]
            query = "inventory/edit_item.sql"
        else:
            new_color = discord.Color.red()
            new_footer = "Upgrade failed"
            query = "inventory/delete_item.sql"
            args = []

        # take action
        result = await self.db.fetch_from_file(
            query, interaction.user.id, self.start_item_id, *args
        )
        if len(result) == 0:
            await send_err_embed(
                interaction,
                "Upgrade **failed** as the start item is no longer in your inventory.",
                ephemeral=True,
            )
            return
        self.original_embed.colour = new_color
        self.original_embed.set_footer(
            text=new_footer, icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.edit_message(embed=self.original_embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user != self.interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        await interaction.response.edit_message(view=None)

    async def on_timeout(self) -> None:
        await self.interaction.edit_original_response(view=None)


async def upgrade(
    bot: SpaceCasesBot, interaction: discord.Interaction, item_id: int, target_item: str
) -> None:
    target_item = remove_skin_name_formatting(target_item)
    exists, item = (
        await bot.db.fetch_from_file(GET_ITEM, interaction.user.id, item_id)
    )[0]
    if not exists:
        raise UserNotRegisteredError(interaction.user)
    if item is None:
        raise UserDoesNotOwnItemError(interaction.user, item_id)
    name: str
    type: ItemType
    name, type, details = item
    start_item_metadatum = bot.item_metadata[name]
    try:
        target_item_metadatum = bot.item_metadata[target_item]
    except KeyError:
        raise ItemDoesNotExistError(target_item)
    if target_item_metadatum.price < start_item_metadatum.price:
        await send_err_embed(interaction, "You **cannot** upgrade to a cheaper item")
        return
    price_multiplier = target_item_metadatum.price / start_item_metadatum.price
    if target_item_metadatum.price == 0:
        await send_err_embed(
            interaction,
            "Upgrade **cannot** be performed as the target item is so rare it has no price data",
        )
        return
    if start_item_metadatum.price == 0:
        await send_err_embed(
            interaction,
            "Upgrade **cannot** be performed as the item you wish to upgrade so rare it has no price data",
        )
        return
    chance = 1.0 / (price_multiplier**EXPONENT)
    if chance > MAX_UPGRADE_CHANCE:
        await send_err_embed(interaction, "This chance of this upgrade is **too high**")
        return
    e = discord.Embed(
        description=f"Upgrading: **{start_item_metadatum.formatted_name}**\nTo: **{target_item_metadatum.formatted_name}**",
        color=discord.Color.dark_theme(),
    )
    e.add_field(name="Price Multiplier", value=f"{price_multiplier}X")
    e.add_field(name="Chance", value=f"{chance * 100:.2g}%")
    e.set_thumbnail(url=start_item_metadatum.image_url)
    e.set_image(url=target_item_metadatum.image_url)
    e.set_footer(
        text=f"You have {UpgradeView.TIMEOUT_TIME} seconds to respond",
        icon_url=interaction.user.display_avatar.url,
    )
    await interaction.response.send_message(
        embed=e,
        view=UpgradeView(
            bot.db, interaction, e, item_id, target_item, target_item_metadatum, chance
        ),
    )
