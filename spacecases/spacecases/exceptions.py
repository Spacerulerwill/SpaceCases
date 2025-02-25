import discord
from dataclasses import dataclass


@dataclass
class UserNotRegisteredError(discord.app_commands.AppCommandError):
    user: discord.Member | discord.User


@dataclass
class InsufficientBalanceError(discord.app_commands.AppCommandError):
    pass


@dataclass
class UserDoesNotOwnItemError(discord.app_commands.AppCommandError):
    user: discord.Member | discord.User
    id: int


@dataclass
class ItemDoesNotExistError(discord.app_commands.AppCommandError):
    item: str


@dataclass
class ContainerDoesNotExistError(discord.app_commands.AppCommandError):
    container: str


@dataclass
class UserInventoryEmptyError(discord.app_commands.AppCommandError):
    user: discord.Member | discord.User
