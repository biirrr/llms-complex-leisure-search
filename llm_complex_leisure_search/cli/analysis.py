# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Analysis-related CLI commands."""

import itertools
import os
from csv import DictWriter

from rich import print as console
from rich.progress import track
from typer import Typer

from llm_complex_leisure_search.analysis.basic_stats import (
    artifact_counts,
    confidence_counts,
    data_set_summary_stats,
    duplicate_counts,
    llm_solved_at_rank,
    llm_solved_at_rank_avg,
    llm_solved_at_rank_single,
    llm_solved_mmr,
    llm_solved_stats,
    llm_summary_stats,
)
from llm_complex_leisure_search.analysis.comparison_stats import compare_artifact_rank_stats
from llm_complex_leisure_search.analysis.correlation_stats import (
    correlate_confidence_rank,
    correlate_correct,
    correlate_popularity_confidence,
    correlate_popularity_rank,
)
from llm_complex_leisure_search.constants import DOMAINS, LLMS

group = Typer(name="analysis", help="Commands for data analysis")


@group.command()
def summary_stats() -> None:
    """Generate summary statistics."""
    with open(os.path.join("analysis", "summary.csv"), "w") as out_f:
        writer = DictWriter(out_f, fieldnames=["domain", "threads.total", "human.solved", "human.solved.fraction"])
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating summary stats"):
            row = {"domain": domain}
            row.update(data_set_summary_stats(domain))
            writer.writerow(row)


@group.command()
def llm_stats() -> None:
    """Generate llm summary statistics."""
    with open(os.path.join("analysis", "llm-summary.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "threads.answered",
                "threads.answered.fraction",
                "results.length.min",
                "results.length.q1",
                "results.length.median",
                "results.length.q3",
                "results.length.max",
                "results.total",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating summary stats"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(llm_summary_stats(domain, llm))
                    writer.writerow(row)
                except FileNotFoundError as e:
                    console(e)


@group.command()
def solved_stats() -> None:
    """Generate solved statistics."""
    with open(os.path.join("analysis", "solved-best.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=["domain", "llm", "mmr"]
            + [f"solved.{rank + 1}" for rank in range(0, 20)]
            + [f"solved.{rank + 1}.fraction" for rank in range(0, 20)],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating best solved stats"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    for rank in range(0, 20):
                        row.update(llm_solved_at_rank(domain, llm, rank))
                    row.update(llm_solved_mmr(domain, row))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)
    with open(os.path.join("analysis", "solved.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=["domain", "llm", "mmr"]
            + [f"solved.{rank + 1}" for rank in range(0, 20)]
            + [f"solved.{rank + 1}.fraction" for rank in range(0, 20)],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating solved stats"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    for rank in range(0, 20):
                        row.update(llm_solved_at_rank_single(domain, llm, rank))
                    row.update(llm_solved_mmr(domain, row, solved_factor=3))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)
    with open(os.path.join("analysis", "solved-average.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "mmr",
                *itertools.chain(
                    *[
                        [
                            f"solved.{rank + 1}.avg",
                            f"solved.{rank + 1}.stdev",
                            f"solved.{rank + 1}.fraction.avg",
                            f"solved.{rank + 1}.fraction.stdev",
                        ]
                        for rank in range(0, 20)
                    ]
                ),
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating average solved stats"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    for rank in range(0, 20):
                        row.update(llm_solved_at_rank_avg(domain, llm, rank))
                    row.update(llm_solved_mmr(domain, row, field_suffix=".avg"))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)
    with open(os.path.join("analysis", "solved-stats.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=["domain", "llm"]
            + [f"solved.{rank}" for rank in range(0, 4)]
            + [f"solved.{rank}.fraction" for rank in range(0, 4)],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating solved stats"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(llm_solved_stats(domain, llm))
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
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(artifact_counts(domain, llm))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)


@group.command()
def duplicate_stats() -> None:
    """Generate duplicate statistics."""
    with open(os.path.join("analysis", "duplicates.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "results.duplicates",
                "results.duplicates.fraction",
                "duplicates.average",
                "duplicates.min",
                "duplicates.q1",
                "duplicates.median",
                "duplicates.q3",
                "duplicates.max",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating duplicate stats"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(duplicate_counts(domain, llm))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)


@group.command()
def confidence_stats() -> None:
    """Generate confidence statistics."""
    with open(os.path.join("analysis", "confidence.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "confidence.average",
                "confidence.std",
                "confidence.min",
                "confidence.q1",
                "confidence.median",
                "confidence.q3",
                "confidence.max",
                "confidence.noscore",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Generating duplicate stats"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(confidence_counts(domain, llm))
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
    solved_stats()
    artifact_stats()
    duplicate_stats()


@group.command()
def compare_artifact_ranks() -> None:
    """Generate stats whether the real/artifact answer rank distributions differ."""
    with open(os.path.join("analysis", "compare-artifact-ranks.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "real.rank.min",
                "real.rank.q1",
                "real.rank.median",
                "real.rank.q3",
                "real.rank.max",
                "real.rank.avg",
                "real.rank.std",
                "artifact.rank.min",
                "artifact.rank.q1",
                "artifact.rank.median",
                "artifact.rank.q3",
                "artifact.rank.max",
                "artifact.rank.avg",
                "artifact.rank.std",
                "mwu.two_sided.statistic",
                "mwu.two_sided.pvalue",
                "mwu.greater.statistic",
                "mwu.greater.pvalue",
                "mwu.less.statistic",
                "mwu.less.pvalue",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Calculating distribution stats"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(compare_artifact_rank_stats(domain, llm))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)


@group.command()
def confidence_correct_correlation() -> None:
    """Generate confidence - correctness stats."""
    with open(os.path.join("analysis", "correlate-correct.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "lr.confidence.avg",
                "lr.confidence.stdev",
                "lr.confidence.pos.avg",
                "lr.confidence.pos.stdev",
                "lr.confidence.neg.avg",
                "lr.confidence.neg.stdev",
                "lr.rank.avg",
                "lr.rank.stdev",
                "lr.rank.pos.avg",
                "lr.rank.pos.stdev",
                "lr.rank.neg.avg",
                "lr.rank.neg.stdev",
                "lr.combined.avg",
                "lr.combined.stdev",
                "lr.combined.pos.avg",
                "lr.combined.pos.stdev",
                "lr.combined.neg.avg",
                "lr.combined.neg.stdev",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Calculating correlations"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(correlate_correct(domain, llm))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)


@group.command()
def confidence_rank_correlation() -> None:
    """Generate confidence - rank stats."""
    with open(os.path.join("analysis", "correlate-confidence-rank.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "pearsonr.statistic",
                "pearsonr.pvalue",
                "spearmanr.statistic",
                "spearmanr.pvalue",
                "kendalltau.statistic",
                "kendalltau.pvalue",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Calculating correlations"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(correlate_confidence_rank(domain, llm))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)


@group.command()
def popularity_rank_correlation() -> None:
    """Generate popularity - rank stats."""
    with open(os.path.join("analysis", "correlate-popularity-rank.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "pearsonr.statistic",
                "pearsonr.pvalue",
                "spearmanr.statistic",
                "spearmanr.pvalue",
                "kendalltau.statistic",
                "kendalltau.pvalue",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Calculating correlations"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(correlate_popularity_rank(domain, llm))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)


@group.command()
def popularity_confidence_correlation() -> None:
    """Generate popularity - confidence stats."""
    with open(os.path.join("analysis", "correlate-popularity-confidence.csv"), "w") as out_f:
        writer = DictWriter(
            out_f,
            fieldnames=[
                "domain",
                "llm",
                "pearsonr.statistic",
                "pearsonr.pvalue",
                "spearmanr.statistic",
                "spearmanr.pvalue",
                "kendalltau.statistic",
                "kendalltau.pvalue",
            ],
        )
        writer.writeheader()
        for domain in track(DOMAINS, description="Calculating correlations"):
            for llm in LLMS:
                try:
                    row = {"domain": domain, "llm": llm}
                    row.update(correlate_popularity_confidence(domain, llm))
                    writer.writerow(row)
                except KeyError as e:
                    console(f"{e} not found")
                except FileNotFoundError as e:
                    console(e)
