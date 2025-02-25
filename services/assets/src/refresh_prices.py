"""
Refresh prices in the `skin_metadata.json` and `sticker_metadata.json` files
"""

import os
import json
import requests
import random
from typing import Any
from common import remove_skin_name_formatting, PhaseGroup
from constants import OUTPUT_DIRECTORY, VANILLA_KNIVES
from decimal import Decimal
from statistics import mean
from util import Condition


def fetch_skinport_data() -> Any:
    """Fetch data from Skinport API or local cache."""
    try:
        with open("skinport_prices.json") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("user_agents.txt") as f:
            user_agents = [line.strip() for line in f.readlines()]
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Encoding": "br, gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        response = requests.get(
            "https://api.skinport.com/v1/items",
            headers=headers,
        )
        response.raise_for_status()
        skinport_item_data = response.json()
        return skinport_item_data


def aggregate_skinport_prices(
    prices: dict[str, list[int]], skinport_item_data: Any
) -> None:
    """Aggregate prices from the Skinport data."""
    for datum in skinport_item_data:
        market_hash_name = datum["market_hash_name"]
        if market_hash_name not in prices:
            continue
        price = datum["suggested_price"]
        if price is None:
            continue
        price = int(Decimal(price) * 100)

        if market_hash_name in VANILLA_KNIVES:
            for condition in Condition:
                new_name = f"{market_hash_name} ({condition})"
                prices[new_name].append(price)
            continue

        if "Gamma Doppler" in market_hash_name:
            for phase in PhaseGroup.GAMMA_DOPPLER.get_phases():
                new_name = market_hash_name.replace("(", f"- {phase} (")
                if new_name not in prices:
                    continue
                prices[new_name].append(price)
        elif "Doppler" in market_hash_name:
            for phase in PhaseGroup.DOPPLER.get_phases():
                new_name = market_hash_name.replace("(", f"- {phase} (")
                if new_name not in prices:
                    continue
                prices[new_name].append(price)
        else:
            prices[market_hash_name].append(price)


def aggregate_prices_for(file: str, skinport_item_data: Any) -> None:
    """Process a single file and aggregate prices."""
    with open(os.path.join(OUTPUT_DIRECTORY, file)) as f:
        metadata = json.load(f)

    # Initialize the price aggregation dictionary
    prices: dict[str, list[int]] = {
        datum["formatted_name"]: [] for datum in metadata.values()
    }

    # Aggregate prices using Skinport data
    aggregate_skinport_prices(prices, skinport_item_data)

    # Calculate and assign mean prices to metadata
    for name, aggregated_prices in prices.items():
        unformatted_name = remove_skin_name_formatting(name)
        if len(aggregated_prices) == 0:
            price = 0
        else:
            mean_price = mean(aggregated_prices)
            price = int(mean_price)

        metadata[unformatted_name]["price"] = price

    # Write updated metadata back to file
    with open(os.path.join(OUTPUT_DIRECTORY, file), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Fetch Skinport data once
    skinport_data = fetch_skinport_data()

    # Process files using the shared Skinport data
    aggregate_prices_for("skin_metadata.json", skinport_data)
    aggregate_prices_for("sticker_metadata.json", skinport_data)
    aggregate_prices_for("skin_cases.json", skinport_data)
    aggregate_prices_for("sticker_capsules.json", skinport_data)
    aggregate_prices_for("souvenir_packages.json", skinport_data)
