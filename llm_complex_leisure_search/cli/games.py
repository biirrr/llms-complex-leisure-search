# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Games-related CLI commands."""

import json
import os
from csv import DictReader

from rich import print as console
from typer import Typer

from llm_complex_leisure_search.games.data import (
    extract_solved_threads,
)
from llm_complex_leisure_search.games.igdb import (
    SearchMode as IGDBSearchMode,
)
from llm_complex_leisure_search.games.igdb import (
    search as igdb_search,
)

group = Typer(name="games", help="Commands for game-related processing")


@group.command()
def extract() -> None:
    """Extract all solved threads."""
    records = []
    for filename in ["posts01.csv", "posts02.csv"]:
        with open(os.path.join("data", "games", filename)) as in_f:
            reader = DictReader(in_f)
            for record in reader:
                records.append(record)
    solved = extract_solved_threads(records)
    with open(os.path.join("data", "games", "solved.json"), "w") as out_f:
        json.dump(solved, out_f)


@group.command()
def search(name: str, search_mode: IGDBSearchMode = IGDBSearchMode.DEFAULT) -> None:
    """Search for a game by name on IGDB."""
    console(igdb_search(name, search_mode=search_mode))


@group.command()
def stats() -> None:
    """Summary statistics for the games data-set."""
    thread_ids = set()
    for filename in ["posts01.csv", "posts02.csv"]:
        with open(os.path.join("data", "games", filename)) as in_f:
            reader = DictReader(in_f)
            for record in reader:
                thread_ids.add(record["thread_id"])
    total = len(thread_ids)
    solved = 0
    confirmed = 0
    with open(os.path.join("data", "games", "solved.json")) as in_f:
        tasks = json.load(in_f)
        for task in tasks:
            if task["solved"]:
                solved = solved + 1
            if task["confirmed"]:
                confirmed = confirmed + 1
    console(
        f"""Games Stats
===========
Total threads: {total}
Solved: {solved}
Confirmed: {confirmed}"""
    )
