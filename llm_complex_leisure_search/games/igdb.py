# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""IGDB API functions."""

from enum import Enum
from time import sleep

from httpx import Client

from llm_complex_leisure_search.settings import settings


class SearchMode(str, Enum):
    """Search modes."""

    DEFAULT = "default"
    EXACT = "exact"


def get_game(game_id: str) -> dict | None:
    """Fetch the data for a single game."""
    sleep(0.3)
    with Client(timeout=30) as client:
        response = client.post(
            "https://id.twitch.tv/oauth2/token",
            params=[
                ("client_id", settings.igdb.client_id),
                ("client_secret", settings.igdb.client_secret),
                ("grant_type", "client_credentials"),
            ],
        )
        if response.status_code == 200:  # noqa: PLR2004
            auth_data = response.json()
            response = client.post(
                "https://api.igdb.com/v4/games",
                headers=[
                    ("Client-ID", settings.igdb.client_id),
                    ("Authorization", f"Bearer {auth_data['access_token']}"),
                    ("Accept", "application/json"),
                ],
                data=f"fields id,name,release_dates,url,parent_game;limit 100;where id = {game_id};",
            )
            results = response.json()
            for entry in results:
                if "release_dates" in entry:
                    sleep(0.3)
                    response = client.post(
                        "https://api.igdb.com/v4/release_dates",
                        headers=[
                            ("Client-ID", settings.igdb.client_id),
                            ("Authorization", f"Bearer {auth_data['access_token']}"),
                            ("Accept", "application/json"),
                        ],
                        data=f"fields y;limit 100;where id = ({','.join([str(v) for v in entry['release_dates']])});",
                    )
                    dates = response.json()
                    entry["release_years"] = list({date["y"] for date in dates if "y" in date})
                else:
                    entry["release_years"] = []
            if len(results) == 1:
                return results[0]
    return None


def search(name: str, search_mode: SearchMode = SearchMode.DEFAULT) -> list[dict]:
    """Search the IGDB API by name."""
    with Client(timeout=30) as client:
        response = client.post(
            "https://id.twitch.tv/oauth2/token",
            params=[
                ("client_id", settings.igdb.client_id),
                ("client_secret", settings.igdb.client_secret),
                ("grant_type", "client_credentials"),
            ],
        )
        if response.status_code == 200:  # noqa: PLR2004
            auth_data = response.json()
            response = client.post(
                "https://api.igdb.com/v4/games",
                headers=[
                    ("Client-ID", settings.igdb.client_id),
                    ("Authorization", f"Bearer {auth_data['access_token']}"),
                    ("Accept", "application/json"),
                ],
                data=f'fields id,name,release_dates,url,parent_game,rating,rating_count;limit 100;search "{name}";',
            )
            results = response.json()
            if search_mode == SearchMode.EXACT:
                results = [
                    entry for entry in results if name == entry["name"] or name.replace(" and ", " & ") == entry["name"]
                ]
            for entry in results:
                if "release_dates" in entry:
                    sleep(0.3)
                    response = client.post(
                        "https://api.igdb.com/v4/release_dates",
                        headers=[
                            ("Client-ID", settings.igdb.client_id),
                            ("Authorization", f"Bearer {auth_data['access_token']}"),
                            ("Accept", "application/json"),
                        ],
                        data=f"fields y;limit 100;where id = ({','.join([str(v) for v in entry['release_dates']])});",
                    )
                    dates = response.json()
                    entry["release_years"] = list({date["y"] for date in dates if "y" in date})
                else:
                    entry["release_years"] = []
            return results
        return []
