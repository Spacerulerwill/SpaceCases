"""
Generate all metadata for CS2 skins and stickers
"""

import os
import re
import json
import requests
from typing import NamedTuple, Any
from constants import OUTPUT_DIRECTORY, DEFAULT_ASSET_DOMAIN
from common import (
    remove_skin_name_formatting,
    SkinMetadatum,
    StickerMetadatum,
    Rarity,
)
from constants import VANILLA_KNIVES
from util import Condition, create_image_url, get_rarity_from_string
from dotenv import load_dotenv


class Result(NamedTuple):
    skin_metadata: dict[str, SkinMetadatum]
    sticker_metadata: dict[str, StickerMetadatum]


def process_skin_json(
    metadata: dict[str, SkinMetadatum], datum: Any, asset_domain: str
) -> None:
    if datum["name"] in VANILLA_KNIVES:
        process_vanilla_knife(metadata, datum, asset_domain)
    else:
        process_non_vanilla_knife(metadata, datum, asset_domain)


def process_vanilla_knife(
    metadata: dict[str, SkinMetadatum], datum: Any, asset_domain: str
) -> None:
    formatted_name_no_wear = datum["name"]
    for condition in Condition:
        formatted_name = f"{formatted_name_no_wear} ({condition})"
        unformatted_name = remove_skin_name_formatting(formatted_name)
        rarity = Rarity.Ancient
        min_float = 0.0
        max_float = 1.0
        description = None
        image_url = create_image_url(unformatted_name, asset_domain)
        metadata[unformatted_name] = SkinMetadatum(
            formatted_name=formatted_name,
            condition=condition,
            rarity=rarity,
            price=0,
            image_url=image_url,
            description=description,
            min_float=min_float,
            max_float=max_float,
        )


def process_non_vanilla_knife(
    metadata: dict[str, SkinMetadatum], datum: Any, asset_domain: str
) -> None:
    # name
    formatted_name = datum["name"]
    if "Doppler" in formatted_name:
        phase = datum["phase"]
        split = formatted_name.split("(")
        name_no_wear = split[0].strip()
        condition_string = f"({split[1].strip()}"
        formatted_name = f"{name_no_wear} - {phase} {condition_string}"
    # determine condition
    for condition_string, condition in [
        ("Factory New", Condition.FactoryNew),
        ("Minimal Wear", Condition.MinimalWear),
        ("Field-Tested", Condition.FieldTested),
        ("Well-Worn", Condition.WellWorn),
        ("Battle-Scarred", Condition.BattleScarred),
    ]:
        if condition_string in formatted_name:
            break
    else:
        raise ValueError(f"No condition found for {formatted_name}")
    unformatted_name = remove_skin_name_formatting(formatted_name)
    # rarity
    rarity = get_rarity_from_string(datum["rarity"]["id"])
    # float range
    min_float = datum.get("min_float", 0.0)
    max_float = datum.get("max_float", 1.0)
    # description
    description_match = re.search(r"<i>(.*?)</i>", datum["description"])
    if description_match:
        description = description_match.group(1)
    else:
        description = None
    # image url
    image_url = create_image_url(unformatted_name, asset_domain)
    # insert
    skin_datum = SkinMetadatum(
        formatted_name=formatted_name,
        condition=condition,
        rarity=rarity,
        price=0,
        image_url=image_url,
        description=description,
        min_float=min_float,
        max_float=max_float,
    )
    metadata[unformatted_name] = skin_datum


def process_sticker_json(
    metadata: dict[str, StickerMetadatum], datum: Any, asset_domain: str
) -> None:
    formatted_name = datum["name"]
    unformatted_name = remove_skin_name_formatting(formatted_name)
    rarity = get_rarity_from_string(datum["rarity"]["id"])
    image_url = create_image_url(unformatted_name, asset_domain)
    metadata[unformatted_name] = StickerMetadatum(
        formatted_name=formatted_name, rarity=rarity, price=0, image_url=image_url
    )


def run(api_data: Any, asset_domain: str) -> Result:
    skin_metadata: dict[str, SkinMetadatum] = {}
    sticker_metadata: dict[str, StickerMetadatum] = {}
    for name, datum in api_data.items():
        if "skin" in name:
            process_skin_json(skin_metadata, datum, asset_domain)
        elif "sticker" in name:
            process_sticker_json(sticker_metadata, datum, asset_domain)
    return Result(skin_metadata, sticker_metadata)


if __name__ == "__main__":
    load_dotenv(override=True)
    asset_domain = os.environ.get("ASSET_DOMAIN", DEFAULT_ASSET_DOMAIN)
    # folder structure
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    # get api data
    api_data = requests.get("https://bymykel.github.io/CSGO-API/api/en/all.json").json()
    # run
    skin_metadata, sticker_metadata = run(api_data, asset_domain)
    # output
    with open(f"{OUTPUT_DIRECTORY}/skin_metadata.json", "w+", encoding="utf-8") as f:
        json.dump(
            {key: value.model_dump() for key, value in skin_metadata.items()},
            f,
            ensure_ascii=False,
            indent=4,
        )
    with open(f"{OUTPUT_DIRECTORY}/sticker_metadata.json", "w+", encoding="utf-8") as f:
        json.dump(
            {key: value.model_dump() for key, value in sticker_metadata.items()},
            f,
            ensure_ascii=False,
            indent=4,
        )
