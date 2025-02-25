import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
from spacecases.database import Database, COUNT_USERS
from spacecases.ui.embed import send_exception_embed
from marisa_trie import Trie
from common import (
    ItemMetadatum,
    Container,
    get_skin_metadata,
    get_sticker_metadata,
    get_skin_cases,
    get_souvenir_packages,
    get_sticker_capsules,
    get_logger,
)
from spacecases.leaderboard import Leaderboard
from typing import Optional
from contextlib import suppress

logger = get_logger(__name__)

MARKER_FILE_TEXT = """This file indicates the bot has globally synchronised its slash commands for bot user %i at least once. 
If you need to sync them again, either globally or for a specific guild, use the /sync command in the bot itself. 
If that command is not present, delete this file and restart the bot. Check for the /sync command again."""


class SpaceCasesCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Debug logging
        user = interaction.user
        guild = interaction.guild if interaction.guild else "DM"
        # Check if it's a slash command and log the parameters
        if (
            interaction.type == discord.InteractionType.application_command
            and interaction.command is not None
        ):
            command_name = interaction.command.name
            if interaction.data is not None:
                options = interaction.data.get("options", [])
            else:
                options = []

            logger.debug(
                f"Slash command '{command_name}' invoked by {user} ({user.id}) in {guild} with options: {options}"
            )

        else:
            # Other interaction types
            logger.debug(
                f"Interaction '{interaction.type}' invoked by {user} ({user.id}) in {guild}"
            )
        return True

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        await send_exception_embed(interaction, error)


class SpaceCasesBot(commands.Bot):
    def __init__(
        self,
        pool: Database,
        asset_domain: str,
        leaderboards_domain: str,
        owner_id: int,
    ):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="", intents=intents, tree_cls=SpaceCasesCommandTree
        )
        self.db = pool
        # items
        self.item_metadata: dict[str, ItemMetadatum] = {}
        self.item_unformatted_names: list[str] = []
        self.item_trie = Trie()
        # containers
        self.containers: dict[str, Container] = {}
        self.container_unformatted_names: list[str] = []
        self.container_trie = Trie()
        # other stuff
        self.command_ids: dict[str, int] = {}
        self.status_int = 0
        self.user_count = 0
        # environment variables
        self.asset_domain = asset_domain
        self.leaderboards_domain = leaderboards_domain
        self.owner_id = owner_id
        # leaderboards
        self.global_leaderboard = Leaderboard({})
        self.guild_leaderboards: dict[int, Leaderboard] = {}

    def get_asset_url(self, path: str) -> str:
        return os.path.join(self.asset_domain, path)

    async def refresh_item_metadata(self) -> None:
        skin_metadata = await get_skin_metadata(self.asset_domain)
        sticker_metadata = await get_sticker_metadata(self.asset_domain)
        self.item_metadata = skin_metadata | sticker_metadata
        self.item_unformatted_names = list(skin_metadata.keys()) + list(
            sticker_metadata.keys()
        )
        self.item_trie = Trie(self.item_unformatted_names)

    async def refresh_containers(self) -> None:
        skin_cases = await get_skin_cases(self.asset_domain)
        souvenir_packages = await get_souvenir_packages(self.asset_domain)
        sticker_capsules = await get_sticker_capsules(self.asset_domain)
        self.containers = skin_cases | souvenir_packages | sticker_capsules
        self.container_unformatted_names = (
            list(skin_cases.keys())
            + list(souvenir_packages.keys())
            + list(sticker_capsules.keys())
        )
        self.container_trie = Trie(self.container_unformatted_names)

    @tasks.loop(minutes=15)
    async def refresh_data_loop(self) -> None:
        await self.refresh_item_metadata()
        await self.refresh_containers()

    @tasks.loop(seconds=10)
    async def bot_status_loop(self) -> None:
        await self.wait_until_ready()
        self.status_int = (self.status_int + 1) % 2
        match self.status_int:
            case 0:
                await self.change_presence(activity=discord.Game(name="/register"))
            case 1:
                await self.change_presence(
                    activity=discord.Game(
                        name=f"{self.user_count} users | {len(self.guilds)} servers"
                    )
                )
            case _:
                raise ValueError("Invalid status int")

    @tasks.loop(minutes=5)
    async def refresh_leaderboards_loop(self) -> None:
        self.global_leaderboard = await Leaderboard.from_remote_json(
            self.leaderboards_domain
        )
        async for guild in self.fetch_guilds():
            self.guild_leaderboards[guild.id] = await Leaderboard.from_remote_json(
                self.leaderboards_domain, guild.id
            )

    async def close(self) -> None:
        if self.user:
            logger.info(f"Goodbye from {self.user}")
        else:
            logger.info("Goodbye!")

    async def setup_hook(self) -> None:
        self.user_count = (await self.db.fetch_from_file(COUNT_USERS))[0]["count"]
        await self._load_cogs()
        for command in await self.tree.fetch_commands():
            self.command_ids[command.name] = command.id
        self.refresh_data_loop.start()
        self.refresh_leaderboards_loop.start()
        self.bot_status_loop.start()

    async def sync_commands(self, guild_id: Optional[int]) -> None:
        if guild_id is not None:
            guild = discord.Object(id=guild_id)
            logger.info(f"Syncing commands for guild with id: {guild_id}...")
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(
                f"Successfully synced the following commands for {guild_id}: {synced}"
            )
        else:
            logger.info("Syncing commands globally...")
            synced = await self.tree.sync()
            logger.info(
                f"Successfully synced the following commands globally: {synced}"
            )

    async def on_ready(self) -> None:
        # sync slash commands only if marker file not present
        if self.user:
            marker_file = f".synced-{self.user.id}"
            with suppress(FileExistsError):
                with open(f"synced/{marker_file}", "x") as f:
                    f.write(MARKER_FILE_TEXT.format(self.user.id))
                await self.sync_commands(None)
        else:
            raise ValueError(
                "Bot client user is None when on_ready is called... discord.py bug?"
            )

        logger.info(f"Bot is logged in as {self.user}")
        logger.info("Bot is ready to receive commands - press CTRL+C to stop")

    def get_welcome_embed(self) -> discord.Embed:
        if self.user:
            name = self.user.display_name
        else:
            name = "SpaceCases"
        e = discord.Embed(
            description=f"""Hello! My name is **{name}**

I am CS:GO case unboxing and economy bot. With me you can:
• Unbox your dream skins
• Trade them with other users
• Take a risk and upgrade them
• And more coming soon
Use {self.get_slash_command_mention_string("register")} to get started!

Enjoy! - [Spacerulerwill](https://github.com/Spacerulerwill)""",
            color=discord.Color.dark_theme(),
        )
        if self.user:
            e.set_thumbnail(url=self.user.display_avatar.url)
        return e

    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.info(f"Joined new guild {guild.name} ({guild.id})")
        if (
            guild.system_channel
            and guild.system_channel.permissions_for(guild.me).send_messages
        ):
            await guild.system_channel.send(embed=self.get_welcome_embed())
        else:
            if guild.owner:
                await guild.owner.send(embed=self.get_welcome_embed())

    async def _load_cogs(self) -> None:
        for filename in os.listdir("spacecases/cogs"):
            if filename.endswith(".py"):
                cog_name = filename.removesuffix(".py")
                await self.load_extension(f"spacecases.cogs.{cog_name}")
                logger.info(f"Loaded cog: {cog_name}")

    async def on_message(self, _: discord.Message) -> None:
        # Disabling chat commands
        pass

    def get_slash_command_mention_string(self, name: str) -> str:
        return f"</{name}:{self.command_ids[name]}>"
