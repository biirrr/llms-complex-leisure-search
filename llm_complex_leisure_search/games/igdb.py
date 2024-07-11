# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""IGDB API functions."""

from httpx import Client

from llm_complex_leisure_search.settings import settings


def search(name: str) -> list[dict]:
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
                    ("Client-ID", "16it1d24qglzpuelk8wjzrs3gvjtz6"),
                    ("Authorization", f"Bearer {auth_data['access_token']}"),
                    ("Accept", "application/json"),
                ],
                data=f'fields id,name,url,parent_game;limit 100;search "{name}";',
            )
            return response.json()
        return []
