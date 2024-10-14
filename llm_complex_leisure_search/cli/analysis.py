# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Analysis-related CLI commands."""

import os
from csv import DictWriter

from rich import print as console
from rich.progress import track
from typer import Typer

from llm_complex_leisure_search.analysis.basic_stats import (
    artifact_counts,
    data_set_summary_stats,
    llm_solved_at_rank,
    llm_summary_stats,
)
from llm_complex_leisure_search.constants import DATA_SETS, DOMAINS, LLMS

group = Typer(name="analysis", help="Commands for data analysis")


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
def llm_stats() -> None:
    """Generate llm summary statistics."""
    with open(os.path.join("analysis", "llm-summary.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "data.set",
                "llm",
                "threads.answered",
                "threads.answered.fraction",
                "results.length.min",
                "results.length.q1",
                "results.length.median",
                "results.length.q3",
                "results.length.max",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating summary stats"):
            for data_set in DATA_SETS:
                for llm in LLMS:
                    try:
                        row = {"domain": domain, "data.set": data_set, "llm": llm}
                        row.update(llm_summary_stats(domain, data_set, llm))
                        writer.writerow(row)
                    except FileNotFoundError as e:
                        console(e)


@group.command()
def recall_stats() -> None:
    """Generate recall statistics."""
    with open(os.path.join("analysis", "recall.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=["domain", "data.set", "llm"]
            + [f"recall.{rank + 1}" for rank in range(0, 20)]
            + [f"recall.{rank + 1}.fraction" for rank in range(0, 20)],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating recall stats"):
            for data_set in DATA_SETS:
                for llm in LLMS:
                    try:
                        row = {"domain": domain, "data.set": data_set, "llm": llm}
                        for rank in range(0, 20):
                            row.update(llm_solved_at_rank(domain, data_set, llm, rank))
                        writer.writerow(row)
                    except KeyError as e:
                        console(f"{e} not found")
                    except FileNotFoundError as e:
                        console(e)


@group.command()
def artifact_stats() -> None:
    """Generate artifact statistics."""
    with open(os.path.join("analysis", "artifacts.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "data.set",
                "llm",
                "generated.total",
                "generated.existing",
                "generated.existing.fraction",
                "generated.existing.exact",
                "generated.existing.exact.fraction",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating artifact stats"):
            if domain == "books":
                continue
            for data_set in DATA_SETS:
                for llm in LLMS:
                    try:
                        row = {"domain": domain, "data.set": data_set, "llm": llm}
                        row.update(artifact_counts(domain, data_set, llm))
                        writer.writerow(row)
                    except KeyError as e:
                        console(f"{e} not found")
                    except FileNotFoundError as e:
                        console(e)


@group.command()
def all_stats() -> None:
    """Generate all statistics."""
    summary_stats()
    llm_stats()
    recall_stats()
    artifact_stats()
