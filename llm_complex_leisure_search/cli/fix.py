# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Books-related CLI commands."""

import json
import os

from rich import print as console
from rich.progress import track
from typer import Typer

group = Typer(name="fix", help="Commands for data fixes")

CATEGORIES = ["books", "games", "movies"]
MODELS = ["gemini", "gpt-4o-mini"]
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
                    for result_set in solution["results"]:
                        for entry in result_set:
                            if isinstance(entry["title"], dict):
                                if "year" in entry["title"]:
                                    entry["qualifiers"] = entry["title"]["year"]
                                elif "release_year" in entry["title"]:
                                    entry["qualifiers"] = entry["title"]["release_year"]
                                else:
                                    console(f"[red bold] No year information in {entry['title'].keys()}")
                                    return
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
