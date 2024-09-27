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
ANNOTATION_SOURCE_FILES = ["jdoc", "extra"]


@group.command()
def extract() -> None:
    """Extract all solved book threads."""
    for suffix in ANNOTATION_SOURCE_FILES:
        first_posts = []
        with open(os.path.join("data", "books", f"first-posts_{suffix}.tsv")) as in_f:
            reader = DictReader(in_f, delimiter="\t")
            for record in reader:
                first_posts.append(record)
        records = []
        with open(os.path.join("data", "books", f"posts_{suffix}.csv")) as in_f:
            reader = DictReader(in_f)
            for record in reader:
                records.append(record)
        with open(os.path.join("data", "books", f"ignored_{suffix}.txt")) as in_f:
            ignored = [thread_id.strip() for thread_id in in_f.readlines() if thread_id.strip()]
        solved = extract_solved_threads(first_posts, records, ignored)
        with open(os.path.join("data", "books", f"solved_{suffix}.json"), "w") as out_f:
            json.dump(solved, out_f)


@group.command()
def query_gemini() -> None:
    """Process the books with Gemini."""
    for suffix in ANNOTATION_SOURCE_FILES:
        with open(os.path.join("data", "books", f"solved_{suffix}.json")) as in_f:
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
        with open(os.path.join("data", "books", f"gemini_{suffix}.json"), "w") as out_f:
            json.dump(results, out_f)


@group.command()
def stats() -> None:
    """Summary statistics for the books data-set."""
    console("Book stats\n##########")
    for suffix in ANNOTATION_SOURCE_FILES:
        thread_ids = set()
        with open(os.path.join("data", "books", f"posts_{suffix}.csv")) as in_f:
            reader = DictReader(in_f)
            for record in reader:
                thread_ids.add(record["thread_id"])
        console(f"Total threads: {suffix}: {len(thread_ids)}")
    for suffix in ANNOTATION_SOURCE_FILES:
        with open(os.path.join("data", "books", f"solved_{suffix}.json")) as in_f:
            tasks = json.load(in_f)
        console(f"Solved: {suffix}: {len(tasks)}")
    for suffix in ANNOTATION_SOURCE_FILES:
        with open(os.path.join("data", "books", f"solved_{suffix}.json")) as in_f:
            tasks = json.load(in_f)
        with open(os.path.join("data", "books", f"gemini_{suffix}.json")) as in_f:
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
            console(f"Gemini Solution: {suffix}: {gemini_solution} ({gemini_solution / len(tasks):.2f})")
            console(f"Gemini Solved: {suffix}: {gemini_solved} ({gemini_solved / len(tasks):.2f})")
            console(
                f"Gemini Found: {suffix}: {len(gemini_solution_ranks)} ({len(gemini_solution_ranks) / len(tasks):.2f})"
            )
            if (len(gemini_solution_ranks)) > 0:
                console(f"Gemini Average Rank: {suffix}: {sum(gemini_solution_ranks) / len(gemini_solution_ranks)}")
