"""
Generate metadata for CS2 skin cases, soveunir packages and sticker capsules
"""

import os
import json
from dotenv import load_dotenv
import requests
from typing import NamedTuple, Optional, Any
from collections import defaultdict
from constants import OUTPUT_DIRECTORY, DEFAULT_ASSET_DOMAIN
from common import (
    SkinCase,
    Rarity,
    SkinContainerEntry,
    ItemContainerEntry,
    SouvenirPackage,
    StickerCapsule,
    PhaseGroup,
    remove_skin_name_formatting,
)
from util import create_image_url, get_rarity_from_string


class Result(NamedTuple):
    skin_cases: dict[str, SkinCase]
    souvenir_packages: dict[str, SouvenirPackage]
    sticker_capsules: dict[str, StickerCapsule]


def get_phase_group_from_unformatted_name(
    unformatted_name: str,
) -> Optional[PhaseGroup]:
    if "gammadoppler" in unformatted_name:
        return PhaseGroup.GAMMA_DOPPLER
    elif "doppler" in unformatted_name:
        return PhaseGroup.DOPPLER
    else:
        return None


def create_skin_container_entry_from_datum(
    asset_domain: str, datum: Any
) -> SkinContainerEntry:
    item_formatted_name = datum["name"]
    item_unformatted_name = remove_skin_name_formatting(item_formatted_name)
    min_float, max_float = float_ranges[item_unformatted_name]
    phase_group = get_phase_group_from_unformatted_name(item_unformatted_name)
    image_url = os.path.join(
        asset_domain, "generated", "images", "preview", f"{item_unformatted_name}.png"
    )
    return SkinContainerEntry(
        unformatted_name=item_unformatted_name,
        min_float=min_float,
        max_float=max_float,
        phase_group=phase_group,
        image_url=image_url,
    )


def process_skin_case(
    skin_cases: dict[str, SkinCase], asset_domain: str, api_datum: Any
) -> None:
    formatted_name = api_datum["name"]
    unformatted_name = remove_skin_name_formatting(formatted_name)
    contains: dict[Rarity, list[SkinContainerEntry]] = defaultdict(
        list[SkinContainerEntry]
    )
    for item in api_datum["contains"]:
        rarity = get_rarity_from_string(item["rarity"]["id"])
        contains[rarity].append(
            create_skin_container_entry_from_datum(asset_domain, item)
        )
    contains_rare = [
        create_skin_container_entry_from_datum(asset_domain, item)
        for item in api_datum["contains_rare"]
    ]
    skin_cases[unformatted_name] = SkinCase(
        formatted_name=formatted_name,
        price=0,
        image_url=create_image_url(unformatted_name, asset_domain),
        requires_key=True,
        contains=contains,
        contains_rare=contains_rare,
    )


def process_souvenir_package(
    souvenir_packages: dict[str, SouvenirPackage], asset_domain: str, api_datum: Any
) -> None:
    formatted_name = api_datum["name"]
    unformatted_name = remove_skin_name_formatting(formatted_name)
    contains: dict[Rarity, list[SkinContainerEntry]] = defaultdict(
        list[SkinContainerEntry]
    )
    for item in api_datum["contains"]:
        rarity = get_rarity_from_string(item["rarity"]["id"])
        contains[rarity].append(
            create_skin_container_entry_from_datum(asset_domain, item)
        )
    souvenir_packages[unformatted_name] = SouvenirPackage(
        formatted_name=formatted_name,
        price=0,
        image_url=create_image_url(unformatted_name, asset_domain),
        requires_key=False,
        contains=contains,
        contains_rare=[],
    )


STICKER_CAPSULES_THAT_REQUIRE_KEYS = {
    remove_skin_name_formatting("Sticker Capsule"),
    remove_skin_name_formatting("Sticker Capsule 2"),
}


def process_sticker_capsule(
    sticker_capsules: dict[str, StickerCapsule], asset_domain: str, api_datum: Any
) -> None:
    formatted_name = api_datum["name"]
    unformatted_name = remove_skin_name_formatting(formatted_name)
    contains: dict[Rarity, list[ItemContainerEntry]] = defaultdict(
        list[ItemContainerEntry]
    )
    for item in api_datum["contains"]:
        item_formatted_name = f"Sticker | {item['name']}"
        item_unformatted_name = remove_skin_name_formatting(item_formatted_name)
        rarity = get_rarity_from_string(item["rarity"]["id"])
        contains[rarity].append(
            ItemContainerEntry(
                unformatted_name=item_unformatted_name,
                image_url=os.path.join(
                    asset_domain,
                    "generated",
                    "images",
                    "unformatted",
                    f"{item_unformatted_name}.png",
                ),
            )
        )
    sticker_capsules[unformatted_name] = StickerCapsule(
        formatted_name=formatted_name,
        price=0,
        image_url=create_image_url(unformatted_name, asset_domain),
        requires_key=unformatted_name in STICKER_CAPSULES_THAT_REQUIRE_KEYS,
        contains=contains,
        contains_rare=[],
    )


def run(asset_domain: str, api_data: Any) -> Result:
    skin_cases: dict[str, SkinCase] = {}
    souvenir_packages: dict[str, SouvenirPackage] = {}
    sticker_capsules: dict[str, StickerCapsule] = {}
    for datum in api_data:
        match datum["type"]:
            case "Case":
                process_skin_case(skin_cases, asset_domain, datum)
            case "Souvenir":
                process_souvenir_package(souvenir_packages, asset_domain, datum)
            case "Sticker Capsule":
                process_sticker_capsule(sticker_capsules, asset_domain, datum)
    return Result(skin_cases, souvenir_packages, sticker_capsules)


def get_skin_float_ranges() -> dict[str, tuple[float, float]]:
    skin_data = requests.get(
        "https://bymykel.github.io/CSGO-API/api/en/skins.json"
    ).json()
    float_ranges = {}
    for datum in skin_data:
        unformatted_name = remove_skin_name_formatting(datum["name"])
        min_float = datum["min_float"]
        if not min_float:
            min_float = 0.0
        max_float = datum["max_float"]
        if not max_float:
            max_float = 1.0
        float_ranges[unformatted_name] = (min_float, max_float)
    return float_ranges


if __name__ == "__main__":
    load_dotenv(override=True)
    asset_domain = os.environ.get("ASSET_DOMAIN", DEFAULT_ASSET_DOMAIN)
    # folder structure
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    # obtain float ranges
    float_ranges = get_skin_float_ranges()
    # container api data
    api_data = requests.get(
        "https://bymykel.github.io/CSGO-API/api/en/crates.json"
    ).json()
    # run script body
    skin_cases, souvenir_packages, sticker_capsules = run(asset_domain, api_data)
    # output to json
    with open(f"{OUTPUT_DIRECTORY}/skin_cases.json", "w+", encoding="utf-8") as f:
        json.dump(
            {key: value.model_dump() for key, value in skin_cases.items()},
            f,
            ensure_ascii=False,
            indent=4,
        )
    with open(
        f"{OUTPUT_DIRECTORY}/souvenir_packages.json", "w+", encoding="utf-8"
    ) as f:
        json.dump(
            {key: value.model_dump() for key, value in souvenir_packages.items()},
            f,
            ensure_ascii=False,
            indent=4,
        )
    with open(f"{OUTPUT_DIRECTORY}/sticker_capsules.json", "w+", encoding="utf-8") as f:
        json.dump(
            {key: value.model_dump() for key, value in sticker_capsules.items()},
            f,
            ensure_ascii=False,
            indent=4,
        )
