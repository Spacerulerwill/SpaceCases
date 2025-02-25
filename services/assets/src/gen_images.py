"""
Generate/download all images for CS2 skins, stickers and containers
"""

import os
import time
import random
import logging
import requests
from typing import Any
from datetime import datetime
from PIL import Image, ImageOps
from io import BytesIO
from common import (
    remove_skin_name_formatting,
)
from constants import OUTPUT_DIRECTORY, LOG_DIRECTORY, VANILLA_KNIVES
from util import get_all_conditions_for_float_range, Condition

CONDITION_IDX_TO_IMAGE_IDX = [0, 0, 1, 1, 2]


def create_symlink(source: str, destination: str) -> None:
    source = os.path.join(OUTPUT_DIRECTORY, source)
    destination = os.path.join(OUTPUT_DIRECTORY, destination)
    relative_source = os.path.relpath(source, os.path.dirname(destination))
    os.symlink(relative_source, destination)


def create_skin_symlink(condition_image: str, symlink_name: str) -> None:
    create_symlink(
        os.path.join("images", "raw", f"{condition_image}.png"),
        os.path.join("images", "unformatted", f"{symlink_name}.png"),
    )


def create_preview_symlink(condition_image: str, symlink_name: str) -> None:
    create_symlink(
        os.path.join("images", "raw", f"{condition_image}.png"),
        os.path.join("images", "preview", f"{symlink_name}.png"),
    )


with open("user_agents.txt") as f:
    user_agents = [line.strip() for line in f.readlines()]


def make_safe_request(url: str) -> requests.Response:
    time.sleep(1)
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    logging.info(f"Successfully made request to: {url}")
    return r


def process_normal_skin(
    name: str,
    images: dict[str, str],
    skin_datum: Any,
    available_conditions: set[Condition],
) -> None:
    logging.info(f"Processing skin: {name}")
    unformatted_name = remove_skin_name_formatting(name)
    for idx, conditions in [
        (0, [Condition.FactoryNew, Condition.MinimalWear]),
        (1, [Condition.FieldTested, Condition.WellWorn]),
        (2, [Condition.BattleScarred]),
    ]:
        for condition in conditions:
            if condition in available_conditions:
                if name == "MP5-SD | Lab Rats":
                    image_bytes = make_safe_request(
                        images[f"Souvenir {name} ({condition})"]
                    ).content
                else:
                    image_bytes = make_safe_request(
                        images[f"{name} ({condition})"]
                    ).content
                save_skin_image(f"{unformatted_name}{idx}", image_bytes)
                if skin_datum["stattrak"]:
                    save_skin_image(f"stattrak{unformatted_name}{idx}", image_bytes)
                if skin_datum["souvenir"]:
                    save_skin_image(f"souvenir{unformatted_name}{idx}", image_bytes)
                break

    for count, condition in enumerate(available_conditions):
        idx = CONDITION_IDX_TO_IMAGE_IDX[condition.value]
        unformatted_condition = remove_skin_name_formatting(str(condition))
        # create a preview skin link of the skins best quality
        if count == 0:
            create_preview_symlink(f"{unformatted_name}{idx}", unformatted_name)
        create_skin_symlink(
            f"{unformatted_name}{idx}", f"{unformatted_name}{unformatted_condition}"
        )
        if skin_datum["stattrak"]:
            create_skin_symlink(
                f"stattrak{unformatted_name}{idx}",
                f"stattrak{unformatted_name}{unformatted_condition}",
            )
        if skin_datum["souvenir"]:
            create_skin_symlink(
                f"souvenir{unformatted_name}{idx}",
                f"souvenir{unformatted_name}{unformatted_condition}",
            )


def process_doppler_skin(
    name: str,
    images: dict[str, str],
    skin_datum: Any,
    available_conditions: set[Condition],
) -> None:
    logging.info(f"Processing doppler skin: {name} - {skin_datum['phase']}")
    unformatted_name = remove_skin_name_formatting(name)
    unformatted_phase = remove_skin_name_formatting(skin_datum["phase"])
    for idx, conditions in [
        (0, [Condition.FactoryNew, Condition.MinimalWear]),
        (1, [Condition.FieldTested, Condition.WellWorn]),
        (2, [Condition.BattleScarred]),
    ]:
        for condition in conditions:
            if condition in available_conditions:
                image_bytes = make_safe_request(
                    images[f"{name} ({condition}) - {skin_datum['phase']}"]
                ).content
                save_skin_image(
                    f"{unformatted_name}{unformatted_phase}{idx}", image_bytes
                )
                if skin_datum["stattrak"]:
                    save_skin_image(
                        f"stattrak{unformatted_name}{unformatted_phase}{idx}",
                        image_bytes,
                    )
                if skin_datum["souvenir"]:
                    save_skin_image(
                        f"souvenir{unformatted_name}{unformatted_phase}{idx}",
                        image_bytes,
                    )
                break

    for count, condition in enumerate(available_conditions):
        idx = CONDITION_IDX_TO_IMAGE_IDX[condition.value]
        unformatted_condition = remove_skin_name_formatting(str(condition))
        # create a preview skin link of the skins best quality
        if count == 0:
            create_preview_symlink(
                f"{unformatted_name}{unformatted_phase}{idx}",
                f"{unformatted_name}{unformatted_phase}",
            )
        create_skin_symlink(
            f"{unformatted_name}{unformatted_phase}{idx}",
            f"{unformatted_name}{unformatted_phase}{unformatted_condition}",
        )
        if skin_datum["stattrak"]:
            create_skin_symlink(
                f"stattrak{unformatted_name}{unformatted_phase}{idx}",
                f"stattrak{unformatted_name}{unformatted_phase}{unformatted_condition}",
            )
        if skin_datum["souvenir"]:
            create_skin_symlink(
                f"souvenir{unformatted_name}{unformatted_phase}{idx}",
                f"souvenir{unformatted_name}{unformatted_phase}{unformatted_condition}",
            )


def process_vanilla_knife(name: str, images: dict[str, str]) -> None:
    logging.info(f"Processing vanilla knife: {name}")
    # save normal and stattrak version
    unformatted_name = remove_skin_name_formatting(name)
    image_url = images[name]
    image_bytes = make_safe_request(image_url).content
    save_skin_image(unformatted_name, image_bytes)
    save_skin_image(f"stattrak{unformatted_name}", image_bytes)
    # create symlinks
    for count, condition in enumerate(Condition):
        unformatted_condition = remove_skin_name_formatting(str(condition))
        full_name = f"{unformatted_name}{unformatted_condition}"
        # create a preview skin link of the skins best quality
        if count == 0:
            create_preview_symlink(f"{unformatted_name}", unformatted_name)
        create_skin_symlink(unformatted_name, full_name)
        create_skin_symlink(f"stattrak{unformatted_name}", f"stattrak{full_name}")


def save_skin_image(name: str, bytes: bytes) -> None:
    if name.startswith("souvenir"):
        image = Image.open(BytesIO(bytes))
        bordered_image = ImageOps.expand(image, border=3, fill="#CF6A32")
        bordered_image.save(f"{OUTPUT_DIRECTORY}/images/raw/{name}.png")
    elif name.startswith("stattrak"):
        image = Image.open(BytesIO(bytes))
        bordered_image = ImageOps.expand(image, border=3, fill="#FFD700")
        bordered_image.save(f"{OUTPUT_DIRECTORY}/images/raw/{name}.png")
    else:
        with open(f"{OUTPUT_DIRECTORY}/images/raw/{name}.png", "wb+") as f:
            f.write(bytes)


def run_for_skins() -> None:
    logging.info("Starting skins")
    grouped_skin_data = requests.get(
        "https://bymykel.github.io/CSGO-API/api/en/skins.json"
    ).json()
    ungrouped_skin_data = requests.get(
        "https://bymykel.github.io/CSGO-API/api/en/skins_not_grouped.json"
    ).json()
    # images for each
    images = {}
    for datum in ungrouped_skin_data:
        if "image" not in datum:
            continue
        if "Doppler" in datum["name"]:
            images[f"{datum['name']} - {datum['phase']}"] = datum["image"]
        else:
            images[datum["name"]] = datum["image"]

    for count, skin_datum in enumerate(grouped_skin_data, start=1):
        formatted_name = skin_datum["name"]

        logging.info(
            f"Starting item {count}/{len(grouped_skin_data)}: {formatted_name}"
        )

        # Vanilla knives handled separately
        if formatted_name in VANILLA_KNIVES:
            process_vanilla_knife(formatted_name, images)
            continue

        available_conditions = set(
            get_all_conditions_for_float_range(
                skin_datum["min_float"], skin_datum["max_float"]
            )
        )

        # Doppler skins handled separately
        if "Doppler" in formatted_name:
            process_doppler_skin(
                formatted_name, images, skin_datum, available_conditions
            )
            continue

        process_normal_skin(formatted_name, images, skin_datum, available_conditions)


def download_images_from_api_data(api_data: Any) -> None:
    for count, datum in enumerate(api_data, start=1):
        formatted_name = datum["name"]
        logging.info(f"Starting item {count}/{len(api_data)}: {formatted_name}")
        unformatted_name = remove_skin_name_formatting(formatted_name)
        image_bytes = make_safe_request(datum["image"]).content
        with open(
            f"{OUTPUT_DIRECTORY}/images/unformatted/{unformatted_name}.png", "wb+"
        ) as f:
            f.write(image_bytes)


def run_for_stickers() -> None:
    logging.info("Starting stickers")
    sticker_data = requests.get(
        "https://bymykel.github.io/CSGO-API/api/en/stickers.json"
    ).json()
    download_images_from_api_data(sticker_data)


def run_for_containters() -> None:
    logging.info("Starting containers")
    container_data = requests.get(
        "https://bymykel.github.io/CSGO-API/api/en/crates.json"
    ).json()
    # only include skin cases, souvenir packages and sticker capsules
    filtered_container_data = [
        datum
        for datum in container_data
        if datum["type"] in {"Case", "Souvenir", "Sticker Capsule"}
    ]
    download_images_from_api_data(filtered_container_data)


if __name__ == "__main__":
    # directories
    os.makedirs(f"{OUTPUT_DIRECTORY}/images/raw", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIRECTORY}/images/unformatted", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIRECTORY}/images/preview", exist_ok=True)
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    # logging
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_filename = f"gen_skin_data_{current_time}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{LOG_DIRECTORY}/{log_filename}", mode="w+"),
            logging.StreamHandler(),
        ],
    )
    run_for_skins()
    run_for_stickers()
    run_for_containters()
