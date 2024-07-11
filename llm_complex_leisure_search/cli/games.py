# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Games-related CLI commands."""

from rich import print as console
from typer import Typer

from llm_complex_leisure_search.games.igdb import search as igdb_search

group = Typer(name="games", help="Commands for game-related processing")


@group.command()
def search(name: str) -> None:
    """Search for a game by name on IGDB."""
    console(igdb_search(name))
