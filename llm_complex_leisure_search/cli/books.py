# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Books-related CLI commands."""

import json
import os
from csv import DictReader

from rich import print as console
from typer import Typer

from llm_complex_leisure_search.books.data import (
    extract_solved_threads,
)

group = Typer(name="books", help="Commands for book-related processing")


@group.command()
def extract() -> None:
    """Extract all solved book threads."""
    records = []
    for filename in ["posts01.csv", "posts02.csv"]:
        with open(os.path.join("data", "books", filename)) as in_f:
            reader = DictReader(in_f)
            for record in reader:
                records.append(record)
    solved = extract_solved_threads(records)
    with open(os.path.join("data", "books", "solved.json"), "w") as out_f:
        json.dump(solved, out_f)


@group.command()
def stats() -> None:
    """Summary statistics for the books data-set."""
    thread_ids = set()
    for filename in ["posts01.csv", "posts02.csv"]:
        with open(os.path.join("data", "books", filename)) as in_f:
            reader = DictReader(in_f)
            for record in reader:
                thread_ids.add(record["thread_id"])
    total = len(thread_ids)
    solved = 0
    confirmed = 0
    with open(os.path.join("data", "books", "solved.json")) as in_f:
        tasks = json.load(in_f)
        for task in tasks:
            if task["solved"]:
                solved = solved + 1
            if task["confirmed"]:
                confirmed = confirmed + 1
    console(
        f"""Book Stats
==========
Total threads: {total}
Solved: {solved}
Confirmed: {confirmed}"""
    )
