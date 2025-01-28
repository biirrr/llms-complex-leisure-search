# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Analysis-related CLI commands."""

import json
import os

from rich import print as console
from rich.progress import track
from typer import Typer

from llm_complex_leisure_search.constants import DATA_SETS, DOMAINS, LLMS
from llm_complex_leisure_search.util import extract_all_answers

group = Typer(name="data", help="Commands for data processing")


@group.command()
def extract_unique_answers(restrict_domain: str | None = None) -> None:
    """Extract the unique answers."""
    for domain in DOMAINS:
        if restrict_domain is not None and domain != restrict_domain:
            continue
        answers = set()
        for llm in track(LLMS, description=f"Extracting unique {domain} answers"):
            for data_set in DATA_SETS:
                try:
                    with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
                        answers.update(extract_all_answers(json.load(in_f)))
                except KeyError as e:
                    console(f"[red bold]Error[/red bold] {e} not found")
                except FileNotFoundError as e:
                    console(f"[red bold]Error[/red bold] {e}")
        if os.path.exists(os.path.join("data", domain, "unique-answers.json")):
            with open(os.path.join("data", domain, "unique-answers.json")) as in_f:
                data = json.load(in_f)
        else:
            data = []
        result = []
        for answer in track(answers, description=f"Merging unique {domain} answers"):
            found = False
            for old_answer in data:
                answer_tuple = (old_answer["answer"][0], tuple(old_answer["answer"][1]))
                if answer_tuple == answer:
                    result.append(old_answer)
                    found = True
            if not found:
                result.append({"answer": answer, "exists": False, "exists_with_qualifier": False, "popularity": 0})
        with open(os.path.join("data", domain, "unique-answers.json"), "w") as out_f:
            json.dump(result, out_f)
