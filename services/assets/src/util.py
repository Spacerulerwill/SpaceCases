import os
from common import Rarity, Condition


def _get_best_condition_idx(min_float: float) -> int:
    if min_float > 1.0:
        raise ValueError("min_float must be <= 1.0")
    for idx, min in reversed(list(enumerate([0.0, 0.07, 0.15, 0.38, 0.45]))):
        if min_float >= min:
            return idx
    raise ValueError(
        f"Unexpected min_float value: {min_float}. No matching condition found."
    )


def _get_worst_condition_idx(max_float: float) -> int:
    if max_float == 0.0:
        return 0
    if max_float > 1.0:
        raise ValueError("max_float must be <= 1.0")
    for idx, min in reversed(list(enumerate([0.0, 0.07, 0.15, 0.38, 0.45]))):
        if max_float > min:
            return idx
    raise ValueError(
        f"Unexpected max_float value: {max_float}. No matching condition found."
    )


def get_all_conditions_for_float_range(
    min_float: float, max_float: float
) -> list[Condition]:
    if min_float >= max_float:
        raise ValueError("min_float must be < max_float")
    min_idx = _get_best_condition_idx(min_float)
    max_idx = _get_worst_condition_idx(max_float)
    return [Condition(i) for i in range(min_idx, max_idx + 1)]


def create_image_url(name: str, asset_domain: str) -> str:
    return os.path.join(
        asset_domain,
        "generated",
        "images",
        "unformatted",
        f"{name}.png",
    )


def get_rarity_from_string(string: str) -> Rarity:
    return {
        "rarity_common_weapon": Rarity.Common,
        "rarity_uncommon_weapon": Rarity.Uncommon,
        "rarity_rare_weapon": Rarity.Rare,
        "rarity_mythical_weapon": Rarity.Mythical,
        "rarity_legendary_weapon": Rarity.Legendary,
        "rarity_ancient_weapon": Rarity.Ancient,
        "rarity_contraband_weapon": Rarity.Contraband,
        "rarity_default": Rarity.Common,
        "rarity_rare": Rarity.Rare,
        "rarity_mythical": Rarity.Mythical,
        "rarity_legendary": Rarity.Legendary,
        "rarity_ancient": Rarity.Ancient,
        "rarity_contraband": Rarity.Contraband,
    }[string]
