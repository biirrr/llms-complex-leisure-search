# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Analysis-related CLI commands."""

import os
from csv import DictWriter

from rich.progress import track
from typer import Typer

from llm_complex_leisure_search.analysis.basic_stats import data_set_summary_stats, llm_solved_at_rank

group = Typer(name="analysis", help="Commands for data analysis")

DOMAINS = ["books", "games", "movies"]
MODELS = ["gemini", "gpt-4o-mini"]
DATA_SETS = ["extra", "jdoc"]


@group.command()
def summary_stats() -> None:
    """Generate summary statistics."""
    with open(os.path.join("analysis", "summary.csv"), "w") as out_f:
        writer = DictWriter(
            out_f, fieldnames=["domain", "data.set", "threads.total", "human.solved", "human.solved.fraction"]
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating summary stats"):
            for data_set in DATA_SETS:
                row = {"domain": domain, "data.set": data_set}
                row.update(data_set_summary_stats(domain, data_set))
                writer.writerow(row)


@group.command()
def recall_stats() -> None:
    """Generate recall statistics."""
    with open(os.path.join("analysis", "recall.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=["domain", "data.set"]
            + [f"{llm}.recall.{rank + 1}" for llm in MODELS for rank in range(0, 20)]
            + [f"{llm}.recall.{rank + 1}.fraction" for llm in MODELS for rank in range(0, 20)],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating recall stats"):
            for data_set in DATA_SETS:
                row = {"domain": domain, "data.set": data_set}
                for model in MODELS:
                    for rank in range(0, 20):
                        row.update(llm_solved_at_rank(domain, data_set, model, rank))
                writer.writerow(row)


@group.command()
def all_stats() -> None:
    """Generate all statistics."""
    summary_stats()
    recall_stats()
