# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Books-related CLI commands."""

import json
import os
from csv import DictReader

from rich import print as console
from rich.progress import track
from typer import Typer

from llm_complex_leisure_search.books.data import (
    extract_solved_threads,
)
from llm_complex_leisure_search.gemini import generate_multiple_responses
from llm_complex_leisure_search.util import split_book_title_by_author

group = Typer(name="books", help="Commands for book-related processing")
ANNOTATION_SOURCE_FILES = ["posts_jdoc.csv", "posts_extra.csv"]


@group.command()
def extract() -> None:
    """Extract all solved book threads."""
    records = []
    for filename in ANNOTATION_SOURCE_FILES:
        with open(os.path.join("data", "books", filename)) as in_f:
            reader = DictReader(in_f)
            for record in reader:
                records.append(record)
    solved = extract_solved_threads(records)
    with open(os.path.join("data", "books", "solved.json"), "w") as out_f:
        json.dump(solved, out_f)


@group.command()
def query_gemini() -> None:
    """Process the books with Gemini."""
    with open(os.path.join("data", "books", "solved.json")) as in_f:
        tasks = json.load(in_f)
    results = []
    for task in track(tasks, description="Querying Gemini"):
        result = {
            "thread_id": task["thread_id"],
            "results": generate_multiple_responses(task["prompt"]),
        }
        for attempt in result["results"]:
            if attempt is not None:
                for entry in attempt:
                    title, author = split_book_title_by_author(entry["answer"])
                    entry["title"] = title
                    entry["author"] = author
        results.append(result)
    with open(os.path.join("data", "books", "gemini.json"), "w") as out_f:
        json.dump(results, out_f)


@group.command()
def stats() -> None:
    """Summary statistics for the books data-set."""
    thread_ids = set()
    for filename in ANNOTATION_SOURCE_FILES:
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
    with open(os.path.join("data", "books", "gemini.json")) as in_f:
        gemini_tasks = json.load(in_f)
        gemini_solution = 0
        gemini_solved = 0
        gemini_solution_ranks = []
        for gemini_task in gemini_tasks:
            found = False
            for task in tasks:
                if task["thread_id"] == gemini_task["thread_id"]:
                    found = True
                    break
            if found:
                if len(gemini_task["results"]) > 0:
                    gemini_solution = gemini_solution + 1
                for result_list in gemini_task["results"]:
                    if result_list[0]["title"] == task["title"]:
                        gemini_solved = gemini_solved + 1
                        break
                gemini_solution_rank = None
                for result_list in gemini_task["results"]:
                    for idx, result in enumerate(result_list):
                        if result["title"] == task["title"]:
                            if gemini_solution_rank is None:
                                gemini_solution_rank = idx
                            else:
                                gemini_solution_rank = min(gemini_solution_rank, idx)
                if gemini_solution_rank is not None:
                    gemini_solution_ranks.append(gemini_solution_rank)

    console(
        f"""Book Stats
==========
Total threads: {total}
Solved: {solved} ({solved/total:.2f})
Confirmed: {confirmed} ({confirmed/total:.2f})
Gemini Solution: {gemini_solution} ({gemini_solution/total:.2f})
Gemini Solved: {gemini_solved} ({gemini_solved/total:.2f})
Gemini Found: {len(gemini_solution_ranks)} ({len(gemini_solution_ranks)/total:.2f})
Gemini Avg Rank: {sum(gemini_solution_ranks) / len(gemini_solution_ranks)}
"""
    )
