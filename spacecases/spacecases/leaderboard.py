import os
import aiohttp
from dataclasses import dataclass
from typing import Optional
from common import get_logger

logger = get_logger(__name__)


@dataclass
class LeaderboardEntry:
    inventory_value: int
    position: int
    name: str


class Leaderboard:
    def __init__(self, entries: dict[int, LeaderboardEntry]):
        self.users = list(entries.keys())
        self.entries = entries

    @classmethod
    async def from_remote_json(
        cls, leaderboard_domain: str, id: Optional[int] = None
    ) -> "Leaderboard":
        if id is None:
            url = os.path.join(leaderboard_domain, "global.json")
        else:
            url = os.path.join(leaderboard_domain, f"{id}.json")

        logger.info(f"Refreshing leaderboard: {url}")

        entries: dict[int, LeaderboardEntry] = {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    entries = {}
                    data = await response.json()
                    for key, val in data.items():
                        entries[int(key)] = LeaderboardEntry(
                            val["inventory_value"], val["place"], val["username"]
                        )
                elif response.status != 404:
                    response.raise_for_status()
        return Leaderboard(entries)

    def __str__(self) -> str:
        return str(self.entries)

    def __len__(self) -> int:
        return len(self.users)
