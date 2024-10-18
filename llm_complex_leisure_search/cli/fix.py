# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Data fix-related CLI commands."""

import json
import os

from rich import print as console
from rich.progress import track
from typer import Typer

from llm_complex_leisure_search.constants import DATA_SETS, DOMAINS, LLMS
from llm_complex_leisure_search.util import split_book_title_by_author

group = Typer(name="fix", help="Commands for data fixes")


@group.command()
def ensure_result_format() -> None:
    """Ensure all result files are in the correct format."""
    for domain in track(DOMAINS, description="Applying fixes"):
        for llm in LLMS:
            for data_set in DATA_SETS:
                if not os.path.exists(os.path.join("data", domain, f"{llm}_{data_set}.json")):
                    continue
                with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
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
                                elif "answer" in entry["answer"]:
                                    entry["title"] = entry["answer"]["answer"]
                                elif "name" in entry["answer"]:
                                    entry["title"] = entry["answer"]["name"]
                                elif "text" in entry["answer"]:
                                    entry["title"] = entry["answer"]["text"]
                                elif "game" in entry["answer"]:
                                    entry["title"] = entry["answer"]["game"]
                                elif "suggestion" in entry["answer"]:
                                    entry["title"] = entry["answer"]["suggestion"]
                                elif "question" in entry["answer"]:
                                    entry["title"] = entry["answer"]["question"]
                                elif isinstance(entry["answer"], dict):
                                    entry["title"] = next(iter(entry["answer"].keys()))
                                if "Author" in entry["answer"]:
                                    entry["qualifiers"] = entry["answer"]["Author"]
                                elif "author" in entry["answer"]:
                                    entry["qualifiers"] = [entry["answer"]["author"]]
                                elif "year" in entry["answer"]:
                                    entry["qualifiers"] = [entry["answer"]["year"]]
                                elif "release_year" in entry["answer"]:
                                    entry["qualifiers"] = [entry["answer"]["release_year"]]
                                elif "releaseYear" in entry["answer"]:
                                    entry["qualifiers"] = [entry["answer"]["releaseYear"]]
                                elif "release year" in entry["answer"]:
                                    entry["qualifiers"] = [entry["answer"]["release year"]]
                                elif isinstance(entry["answer"], dict):
                                    entry["qualifiers"] = next(iter(entry["answer"].values()))
                            #     else:
                            #         print(entry)
                            #         entry["qualifiers"] = []
                            # if "title" not in entry:
                            #     print(entry)
                            #     return
                            # if "qualifiers" not in entry:
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
                                if " by " in entry["title"]:
                                    title, author = split_book_title_by_author(entry["title"])
                                    entry["title"] = title
                                    entry["qualifiers"] = [author]
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

                with open(os.path.join("data", domain, f"{llm}_{data_set}.json"), "w") as out_f:
                    json.dump(solutions, out_f)


@group.command()
def ensure_only_valid_threads() -> None:
    """Ensure no duplicate threads or ignored threads are included."""
    for domain in track(DOMAINS, description="Applying fixes"):
        for llm in LLMS:
            for data_set in DATA_SETS:
                if not os.path.exists(os.path.join("data", domain, f"{llm}_{data_set}.json")):
                    continue
                with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
                    solutions = json.load(in_f)
                with open(os.path.join("data", domain, f"ignored_{data_set}.txt")) as in_f:
                    ignored = {line.strip() for line in in_f.readlines()}
                with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
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

                with open(os.path.join("data", domain, f"{llm}_{data_set}.json"), "w") as out_f:
                    json.dump(solutions, out_f)


@group.command()
def everything() -> None:
    """Apply all fixes."""
    ensure_only_valid_threads()
    ensure_result_format()
