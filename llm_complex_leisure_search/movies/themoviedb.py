# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""IGDB API functions."""

from enum import Enum
from urllib.parse import quote_plus

from httpx import Client

from llm_complex_leisure_search.settings import settings


class SearchMode(str, Enum):
    """Search modes."""

    DEFAULT = "default"
    EXACT = "exact"


def search(name: str, search_mode: SearchMode = SearchMode.DEFAULT) -> list[dict]:
    """Search the TheMovieDB API by name."""
    with Client(timeout=30) as client:
        result = client.get(
            f"https://api.themoviedb.org/3/search/movie?query={quote_plus(name)}&include_adult=false&language=en-US&page=1",
            headers=[("Authorization", f"Bearer {settings.themoviedb.bearer_token}")],
        )
        if result.status_code == 200:  # noqa: PLR2004
            if search_mode == SearchMode.EXACT:
                return [
                    movie
                    for movie in result.json()["results"]
                    if movie["original_title"] == name or movie["original_title"] == name.replace(" and ", " & ")
                ]
            else:
                return result.json()["results"]
        return []
