# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Books-related CLI commands."""

import json
import os
from csv import DictReader

from rich.progress import track
from typer import Typer

from llm_complex_leisure_search.books.data import (
    extract_solved_threads,
)
from llm_complex_leisure_search.gemini import generate_multiple_responses as gemini_generate
from llm_complex_leisure_search.llms.llama import generate_multiple_responses as llama_generate
from llm_complex_leisure_search.settings import settings
from llm_complex_leisure_search.util import extract_all_answers, split_book_title_by_author

group = Typer(name="books", help="Commands for book-related processing")
ANNOTATION_SOURCE_FILES = ["jdoc", "extra"]
LLM_MODELS = [("Gemini", "gemini"), ("GPT 4o Mini", "gpt-4o-mini")]


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
        if os.path.exists(os.path.join("data", "books", f"gemini_{suffix}.json")):
            with open(os.path.join("data", "books", f"gemini_{suffix}.json")) as in_f:
                results = json.load(in_f)
        else:
            results = []
        for task in track(tasks, description=f"Querying Gemini ({suffix})"):
            # Check if the task has already been processed
            exists = False
            for result in results:
                if result["thread_id"] == task["thread_id"] and len(result["results"]) >= settings.llm.retest_target:
                    exists = True
                    break
            if exists:
                continue
            result = {
                "thread_id": task["thread_id"],
                "results": gemini_generate(task["prompt"]),
            }
            for attempt in result["results"]:
                if attempt is not None:
                    for entry in attempt:
                        title, author = split_book_title_by_author(entry["answer"])
                        entry["title"] = title
                        entry["qualifiers"] = [author]
            results.append(result)
        with open(os.path.join("data", "books", f"gemini_{suffix}.json"), "w") as out_f:
            json.dump(results, out_f)


@group.command()
def query_llama() -> None:
    """Process the books with Llama."""
    for suffix in ANNOTATION_SOURCE_FILES:
        with open(os.path.join("data", "books", f"solved_{suffix}.json")) as in_f:
            tasks = json.load(in_f)
        if os.path.exists(os.path.join("data", "books", f"llama_{suffix}.json")):
            with open(os.path.join("data", "books", f"llama_{suffix}.json")) as in_f:
                results = json.load(in_f)
        else:
            results = []
        for task in track(tasks, description=f"Querying Llama ({suffix})"):
            # Check if the task has already been processed
            exists = False
            for result in results:
                if result["thread_id"] == task["thread_id"] and len(result["results"]) >= settings.llm.retest_target:
                    exists = True
                    break
            if exists:
                continue
            result = {
                "thread_id": task["thread_id"],
                "results": llama_generate(task["prompt"]),
            }
            for attempt in result["results"]:
                if attempt is not None:
                    for entry in attempt:
                        if isinstance(entry["answer"], dict) and "title" in entry["answer"]:
                            entry["title"] = entry["answer"]["title"]
                            if "author" in entry["answer"] and entry["answer"]["author"] is not None:
                                entry["qualifiers"] = [entry["answer"]["author"]]
                            else:
                                entry["qualifiers"] = []
                        elif isinstance(entry["answer"], str):
                            title, author = split_book_title_by_author(entry["answer"])
                            entry["title"] = title
                            if author is not None:
                                entry["qualifiers"] = [author]
                            else:
                                entry["qualifiers"] = []
            results.append(result)
            with open(os.path.join("data", "books", f"llama_{suffix}.json"), "w") as out_f:
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
                if author:
                    entry["qualifiers"] = [author]
                else:
                    entry["qualifiers"] = []

    with open(os.path.join("data", "books", f"gpt-4o-mini_{suffix}.json"), "w") as out_f:
        json.dump(results, out_f)


@group.command()
def extract_answers() -> None:
    """Extract all unique answers."""
    answers = set()
    for _, prefix in track(LLM_MODELS, description="Extracting answers"):
        for suffix in ANNOTATION_SOURCE_FILES:
            with open(os.path.join("data", "books", f"{prefix}_{suffix}.json")) as in_f:
                answers.update(extract_all_answers(json.load(in_f)))
    if os.path.exists(os.path.join("data", "books", "unique-answers.json")):
        with open(os.path.join("data", "books", "unique-answers.json")) as in_f:
            data = json.load(in_f)
    else:
        data = []
    result = []
    for answer in track(answers, description="Merging answers"):
        found = False
        for old_answer in data:
            answer_tuple = (old_answer["answer"][0], tuple(old_answer["answer"][1]))
            if answer_tuple == answer:
                result.append(old_answer)
                found = True
        if not found:
            result.append({"answer": answer, "exists": False, "exists_with_qualifier": False, "popularity": 0})
    with open(os.path.join("data", "books", "unique-answers.json"), "w") as out_f:
        json.dump(result, out_f)
