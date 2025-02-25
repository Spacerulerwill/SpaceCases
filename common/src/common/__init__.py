import re
import os
import logging
import aiohttp
import string
import discord
import random
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional
from enum import IntEnum


def get_logger(name: str) -> logging.Logger:
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


_logger = get_logger(__name__)


class Rarity(IntEnum):
    Common = 0
    Uncommon = 1
    Rare = 2
    Mythical = 3
    Legendary = 4
    Ancient = 5
    Contraband = 6

    def get_name_for_skin(self) -> str:
        """
        Get the rarity string if the item is a skin
        """
        return [
            "Consumer Grade",
            "Industrial Grade",
            "Mil-Spec",
            "Restricted",
            "Classified",
            "Covert",
            "Contraband",
        ][self.value]

    def get_name_for_regular_item(self) -> str:
        """
        Get the rarity string if the item is a regular item
        """
        return [
            "Base Grade",
            "Industrial Grade",
            "High Grade",
            "Remarkable",
            "Exotic",
            "Extraordinary",
            "Contraband",
        ][self.value]


class Condition(IntEnum):
    FactoryNew = 0
    MinimalWear = 1
    FieldTested = 2
    WellWorn = 3
    BattleScarred = 4

    def __str__(self) -> str:
        return [
            "Factory New",
            "Minimal Wear",
            "Field-Tested",
            "Well-Worn",
            "Battle-Scarred",
        ][self.value]

    def get_min_float(self) -> float:
        return [0.45, 0.38, 0.15, 0.07, 0.0][self.value]

    def get_max_float(self) -> float:
        return [1.0, 0.45, 0.38, 0.15, 0.07][self.value]

    def get_float(self, min_float: float, max_float: float) -> float:
        _min = max(self.get_min_float(), min_float)
        _max = min(self.get_max_float(), max_float)
        diff = _max - _min
        return _min + random.random() * diff


class SkinMetadatum(BaseModel):
    formatted_name: str
    condition: Condition
    rarity: Rarity
    price: int
    image_url: str
    description: Optional[str]
    min_float: float
    max_float: float


class StickerMetadatum(BaseModel):
    formatted_name: str
    rarity: Rarity
    price: int
    image_url: str


type ItemMetadatum = SkinMetadatum | StickerMetadatum


class PhaseGroup(IntEnum):
    DOPPLER = 0
    GAMMA_DOPPLER = 1

    def get_phases(self) -> list[str]:
        return [
            [
                "Phase 1",
                "Phase 2",
                "Phase 3",
                "Phase 4",
                "Sapphire",
                "Ruby",
                "Black Pearl",
            ],
            ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Emerald"],
        ][self.value]


class SkinContainerEntry(BaseModel):
    unformatted_name: str
    min_float: float
    max_float: float
    phase_group: Optional[PhaseGroup]
    image_url: str


class ItemContainerEntry(BaseModel):
    unformatted_name: str
    image_url: str


type ContainerEntry = SkinContainerEntry | ItemContainerEntry


class GenericContainer[T: ContainerEntry](BaseModel):
    formatted_name: str
    price: int
    image_url: str
    requires_key: bool
    contains: dict[Rarity, list[T]]
    contains_rare: list[T]


class SkinCase(GenericContainer[SkinContainerEntry]):
    pass


class SouvenirPackage(GenericContainer[SkinContainerEntry]):
    pass


class StickerCapsule(GenericContainer[ItemContainerEntry]):
    pass


type Container = SkinCase | SouvenirPackage | StickerCapsule

_SPECIAL_CHARS_REGEX = re.compile(r"[™★♥\s]")


def remove_skin_name_formatting(skin_name: str) -> str:
    """
    Removes formatting from skin names:
    - Converts to lowercase
    - Removes punctuation, whitespace and special characters
    """
    skin_name = _SPECIAL_CHARS_REGEX.sub("", skin_name.lower())
    return skin_name.translate(str.maketrans("", "", string.punctuation))


class ItemType(Enum):
    Skin = "skin"
    Sticker = "sticker"


@dataclass
class SkinOwnership:
    owner: discord.User | discord.Member
    metadatum: SkinMetadatum
    floats: list[float]


@dataclass
class StickerOwnership:
    owner: discord.User | discord.Member
    metadatum: StickerMetadatum
    count: int


SKIN_METADATA_PATH = os.path.join("generated", "skin_metadata.json")
STICKER_METADATA_PATH = os.path.join("generated", "sticker_metadata.json")
SKIN_CASES_METADATA_PATH = os.path.join("generated", "skin_cases.json")
STICKER_CAPSULE_METADATA_PATH = os.path.join("generated", "sticker_capsules.json")
SOUVENIR_PACKAGE_METADATA_PATH = os.path.join("generated", "souvenir_packages.json")


# Helper function to parse the raw JSON data into a dictionary of model instances
async def parse_metadata[T: BaseModel](url: str, model: type[T]) -> dict[str, T]:
    _logger.info(f"Refreshing metadata from {url}...")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            raw_json = await response.json()
            metadata = {
                key: model.model_validate(value) for key, value in raw_json.items()
            }
    _logger.info(f"Metadata refreshed from {url}")
    return metadata


async def parse_metadata_from_asset_domain[T: BaseModel](
    asset_domain: str, url: str, model: type[T]
) -> dict[str, T]:
    return await parse_metadata(os.path.join(asset_domain, url), model)


async def get_skin_metadata(asset_domain: str) -> dict[str, SkinMetadatum]:
    return await parse_metadata_from_asset_domain(
        asset_domain, SKIN_METADATA_PATH, SkinMetadatum
    )


async def get_sticker_metadata(asset_domain: str) -> dict[str, StickerMetadatum]:
    return await parse_metadata_from_asset_domain(
        asset_domain, STICKER_METADATA_PATH, StickerMetadatum
    )


async def get_skin_cases(asset_domain: str) -> dict[str, SkinCase]:
    return await parse_metadata_from_asset_domain(
        asset_domain, SKIN_CASES_METADATA_PATH, SkinCase
    )


async def get_souvenir_packages(asset_domain: str) -> dict[str, SouvenirPackage]:
    return await parse_metadata_from_asset_domain(
        asset_domain, SOUVENIR_PACKAGE_METADATA_PATH, SouvenirPackage
    )


async def get_sticker_capsules(asset_domain: str) -> dict[str, StickerCapsule]:
    return await parse_metadata_from_asset_domain(
        asset_domain, STICKER_CAPSULE_METADATA_PATH, StickerCapsule
    )
