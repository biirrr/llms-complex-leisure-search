# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Data fix-related CLI commands."""

import json
import os

from rich import print as console
from rich.progress import track
from typer import Typer

group = Typer(name="fix", help="Commands for data fixes")

CATEGORIES = ["books", "games", "movies"]
MODELS = ["gemini", "gpt-3_5", "gpt-4o-mini", "llama"]
DATA_SETS = ["extra", "jdoc"]


@group.command()
def ensure_result_format() -> None:
    """Ensure all result files are in the correct format."""
    for category in track(CATEGORIES, description="Applying fixes"):
        for model in MODELS:
            for data_set in DATA_SETS:
                with open(os.path.join("data", category, f"{model}_{data_set}.json")) as in_f:
                    solutions = json.load(in_f)

                for solution in solutions:
                    results = []
                    for result_set in solution["results"]:
                        results.append([entry for entry in result_set if entry["answer"]])
                    solution["results"] = results
                    for result_set in solution["results"]:
                        for entry in result_set:
                            if "title" not in entry and isinstance(entry["answer"], list):
                                entry["title"] = entry["answer"][0]
                                entry["qualifiers"] = entry["answer"][1:]
                            elif "title" not in entry and isinstance(entry["answer"], dict):
                                if "Title" in entry["answer"]:
                                    entry["title"] = entry["answer"]["Title"]
                                elif "bookTitle" in entry["answer"]:
                                    entry["title"] = entry["answer"]["bookTitle"]
                                if "Author" in entry["answer"]:
                                    entry["qualifiers"] = entry["answer"]["Author"]
                                elif "author" in entry["answer"]:
                                    entry["qualifiers"] = [entry["answer"]["author"]]
                                if len(entry["answer"]) == 1:
                                    if list(entry["answer"].values())[0].startswith("by "):  # noqa: RUF015
                                        entry["title"] = list(entry["answer"].keys())[0]  # noqa: RUF015
                                        entry["qualifiers"] = [list(entry["answer"].values())[0][3:]]  # noqa: RUF015
                                    else:
                                        entry["title"] = list(entry["answer"].keys())[0]  # noqa: RUF015
                                        entry["qualifiers"] = [list(entry["answer"].values())[0]]  # noqa: RUF015
                            # if "title" not in entry:
                            #     print(entry)
                            #     return
                            if isinstance(entry["title"], dict):
                                if "year" in entry["title"]:
                                    entry["qualifiers"] = entry["title"]["year"]
                                elif "release_year" in entry["title"]:
                                    entry["qualifiers"] = entry["title"]["release_year"]
                                else:
                                    console(f"[red bold] No year information in {entry['title'].keys()}")
                                    return
                                if "title" in entry["title"]:
                                    entry["title"] = entry["title"]["title"]
                                else:
                                    console(f"[red bold] No title informatio nin {entry['title'].keys()}")
                            if "qualifiers" not in entry:
                                if "author" in entry:
                                    if entry["author"]:
                                        entry["qualifiers"] = [entry["author"]]
                                    else:
                                        entry["qualifiers"] = []
                                    del entry["author"]
                            if isinstance(entry["qualifiers"], int):
                                entry["qualifiers"] = [str(entry["qualifiers"])]
                            elif isinstance(entry["qualifiers"], str):
                                entry["qualifiers"] = [entry["qualifiers"]]
                            elif isinstance(entry["qualifiers"], list):
                                entry["qualifiers"] = [str(v) for v in entry["qualifiers"]]
                            else:
                                console(
                                    f"[red bold] Unsupported qualifiers type {entry['qualifiers'].__class__.__name__}"
                                )
                                return

                with open(os.path.join("data", category, f"{model}_{data_set}.json"), "w") as out_f:
                    json.dump(solutions, out_f)


@group.command()
def ensure_only_valid_threads() -> None:
    """Ensure no duplicate threads or ignored threads are included."""
    for category in track(CATEGORIES, description="Applying fixes"):
        for model in MODELS:
            for data_set in DATA_SETS:
                with open(os.path.join("data", category, f"{model}_{data_set}.json")) as in_f:
                    solutions = json.load(in_f)
                with open(os.path.join("data", category, f"ignored_{data_set}.txt")) as in_f:
                    ignored = {line.strip() for line in in_f.readlines()}
                with open(os.path.join("data", category, f"solved_{data_set}.json")) as in_f:
                    valid = set()
                    for task in json.load(in_f):
                        valid.add(task["thread_id"])

                tmp = []
                seen_ids = set()
                for solution in solutions:
                    if (
                        solution["thread_id"] not in seen_ids
                        and solution["thread_id"] not in ignored
                        and solution["thread_id"] in valid
                    ):
                        tmp.append(solution)
                        seen_ids.add(solution["thread_id"])
                solutions = tmp

                with open(os.path.join("data", category, f"{model}_{data_set}.json"), "w") as out_f:
                    json.dump(solutions, out_f)
