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
def aggregate_gpt(source_folder: str, suffix: str) -> None:
    """Aggregate the GPT 4o Mini files."""
    with open(os.path.join("data", "movies", f"ignored_{suffix}.txt")) as in_f:
        ignored = [thread_id.strip() for thread_id in in_f.readlines() if thread_id.strip()]
    tasks = {}
    for filename in os.listdir(source_folder):
        if filename.endswith(".json"):
            parts = filename.split(".")
            if parts[0] in ignored:
                continue
            if parts[0] not in tasks:
                tasks[parts[0]] = []
            with open(os.path.join(source_folder, filename)) as in_f:
                try:
                    data = json.load(in_f)
                    if "suggestions" in data:
                        tasks[parts[0]].append(data["suggestions"])
                    elif "recommendations" in data:
                        tasks[parts[0]].append(data["recommendations"])
                except json.JSONDecodeError:
                    pass
    results = []
    for key, value in tasks.items():
        results.append({"thread_id": key, "results": value})
        for attempt in value:
            for entry in attempt:
                title, author = split_book_title_by_author(entry["answer"])
                entry["title"] = title
                entry["author"] = author

    with open(os.path.join("data", "books", f"gpt-4o-mini_{suffix}.json"), "w") as out_f:
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
    for label, prefix in [("Gemini", "gemini"), ("GPT 4o Mini", "gpt-4o-mini")]:
        for suffix in ANNOTATION_SOURCE_FILES:
            with open(os.path.join("data", "books", f"solved_{suffix}.json")) as in_f:
                tasks = json.load(in_f)
            with open(os.path.join("data", "books", f"{prefix}_{suffix}.json")) as in_f:
                llm_tasks = json.load(in_f)
                llm_solution = 0
                llm_solved = 0
                llm_solution_ranks = []
                for llm_task in llm_tasks:
                    found = False
                    for task in tasks:
                        if task["thread_id"] == llm_task["thread_id"]:
                            found = True
                            break
                    if found:
                        if len(llm_task["results"]) > 0:
                            llm_solution = llm_solution + 1
                        for result_list in llm_task["results"]:
                            if result_list[0]["title"] == task["title"]:
                                llm_solved = llm_solved + 1
                                break
                        llm_solution_rank = None
                        for result_list in llm_task["results"]:
                            for idx, result in enumerate(result_list):
                                if result["title"] == task["title"]:
                                    if llm_solution_rank is None:
                                        llm_solution_rank = idx
                                    else:
                                        llm_solution_rank = min(llm_solution_rank, idx)
                        if llm_solution_rank is not None:
                            llm_solution_ranks.append(llm_solution_rank)
                console(f"{label} Solution: {suffix}: {llm_solution} ({llm_solution / len(tasks):.2f})")
                console(f"{label} Solved: {suffix}: {llm_solved} ({llm_solved / len(tasks):.2f})")
                console(
                    f"{label} Found: {suffix}: {len(llm_solution_ranks)} ({len(llm_solution_ranks) / len(tasks):.2f})"
                )
                if (len(llm_solution_ranks)) > 0:
                    console(f"{label} Average Rank: {suffix}: {sum(llm_solution_ranks) / len(llm_solution_ranks)}")
