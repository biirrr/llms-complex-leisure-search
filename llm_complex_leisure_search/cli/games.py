# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Games-related CLI commands."""

import json
import os
from csv import DictReader
from time import sleep

from rich import print as console
from rich.progress import track
from typer import Typer

from llm_complex_leisure_search.games.data import (
    extract_solved_threads,
)
from llm_complex_leisure_search.games.igdb import SearchMode, search
from llm_complex_leisure_search.gemini import generate_multiple_responses as gemini_generate
from llm_complex_leisure_search.llms.llama import generate_multiple_responses as llama_generate
from llm_complex_leisure_search.settings import settings
from llm_complex_leisure_search.util import split_title_years

group = Typer(name="games", help="Commands for game-related processing")
ANNOTATION_SOURCE_FILES = ["jdoc", "extra"]
LLM_MODELS = [("Gemini", "gemini"), ("GPT 4o Mini", "gpt-4o-mini")]


@group.command()
def extract() -> None:
    """Extract all solved games threads."""
    for suffix in ANNOTATION_SOURCE_FILES:
        first_posts = []
        with open(os.path.join("data", "games", f"first-posts_{suffix}.tsv")) as in_f:
            reader = DictReader(in_f, delimiter="\t")
            for record in reader:
                first_posts.append(record)
        records = []
        with open(os.path.join("data", "games", f"posts_{suffix}.csv")) as in_f:
            reader = DictReader(in_f)
            for record in reader:
                records.append(record)
        with open(os.path.join("data", "games", f"ignored_{suffix}.txt")) as in_f:
            ignored = [thread_id.strip() for thread_id in in_f.readlines() if thread_id.strip()]
        solved = extract_solved_threads(first_posts, records, ignored)
        with open(os.path.join("data", "games", f"solved_{suffix}.json"), "w") as out_f:
            json.dump(solved, out_f)


@group.command()
def query_gemini() -> None:
    """Process the books with Gemini."""
    for suffix in ANNOTATION_SOURCE_FILES:
        with open(os.path.join("data", "games", f"solved_{suffix}.json")) as in_f:
            tasks = json.load(in_f)
        if os.path.exists(os.path.join("data", "games", f"gemini_{suffix}.json")):
            with open(os.path.join("data", "games", f"gemini_{suffix}.json")) as in_f:
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
            try:
                result = {
                    "thread_id": task["thread_id"],
                    "results": gemini_generate(task["prompt"]),
                }
                for attempt in result["results"]:
                    if attempt is not None:
                        for entry in attempt:
                            title, years = split_title_years(entry["answer"])
                            entry["title"] = title
                            entry["qualifiers"] = years
                results.append(result)
            except Exception as e:
                console(e)
        with open(os.path.join("data", "games", f"gemini_{suffix}.json"), "w") as out_f:
            json.dump(results, out_f)


@group.command()
def query_llama() -> None:
    """Process the games with Llama."""
    for suffix in ANNOTATION_SOURCE_FILES:
        with open(os.path.join("data", "games", f"solved_{suffix}.json")) as in_f:
            tasks = json.load(in_f)
        if os.path.exists(os.path.join("data", "games", f"llama-3-2_{suffix}.json")):
            with open(os.path.join("data", "games", f"llama-3-2_{suffix}.json")) as in_f:
                results = json.load(in_f)
        else:
            results = []
        for task in track(tasks, description=f"Querying Llama 3.2 ({suffix})"):
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
                            title, years = split_title_years(entry["answer"])
                            entry["title"] = title
                            if years is not None:
                                entry["qualifiers"] = years
                            else:
                                entry["qualifiers"] = []
            results.append(result)
            with open(os.path.join("data", "games", f"llama-3-2_{suffix}.json"), "w") as out_f:
                json.dump(results, out_f)


@group.command()
def aggregate_gpt(source_folder: str, model: str, data_set: str) -> None:
    """Aggregate the GPT files."""
    with open(os.path.join("data", "movies", f"ignored_{data_set}.txt")) as in_f:
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
                title, years = split_title_years(entry["answer"])
                entry["title"] = title
                entry["qualifiers"] = years

    with open(os.path.join("data", "games", f"{model}_{data_set}.json"), "w") as out_f:
        json.dump(results, out_f)


@group.command()
def lookup_answers() -> None:
    """Lookup the answers in the IGDB."""
    with open(os.path.join("data", "games", "unique-answers.json")) as in_f:
        answers = json.load(in_f)
    for idx, answer in enumerate(track(answers, description="Looking up answers")):
        if not answer["exists"]:
            try:
                games = search(answer["answer"][0], SearchMode.EXACT)
                if len(games) > 0:
                    answer["exists"] = True
                    answer["popularity"] = sum([g["rating_count"] for g in games if "rating_count" in g]) / len(games)
                for qualifier in answer["answer"][1]:
                    for game in games:
                        if qualifier in [str(v) for v in game["release_years"]]:
                            answer["exists_with_qualifier"] = True
                            answer["popularity"] = game["rating_count"] if "rating_count" in game else 0
                sleep(0.3)
                if idx % 100 == 0:
                    with open(os.path.join("data", "games", "unique-answers.json"), "w") as out_f:
                        json.dump(answers, out_f)
            except Exception as e:
                console(e)
    with open(os.path.join("data", "games", "unique-answers.json"), "w") as out_f:
        json.dump(answers, out_f)
