"""Comparison statistics functions."""

import json
import os

from scipy.stats import mannwhitneyu

from llm_complex_leisure_search.constants import DATA_SETS


def compare_artifact_rank_stats(domain: str, llm: str) -> dict:
    """Compare whether the answer is an artifact leads to a different rank distribution."""
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    with open(os.path.join("data", domain, "unique-answers.json")) as in_f:
        answers = json.load(in_f)
    real_ranks = []
    artifact_ranks = []
    for solution in solutions:
        for result_list in solution["results"]:
            for idx, result in enumerate(result_list):
                found = False
                for answer in answers:
                    if answer["answer"][0] == result["title"] and answer["exists"]:
                        found = True
                        break
                if found:
                    real_ranks.append(idx)
                else:
                    artifact_ranks.append(idx)
    mwu = mannwhitneyu(real_ranks, artifact_ranks)
    mwu_less = mannwhitneyu(real_ranks, artifact_ranks, alternative="less")
    mwu_greater = mannwhitneyu(real_ranks, artifact_ranks, alternative="greater")
    return {
        "mwu.two_sided.statistic": mwu.statistic,
        "mwu.two_sided.pvalue": mwu.pvalue,
        "mwu.less.statistic": mwu_less.statistic,
        "mwu.less.pvalue": mwu_less.pvalue,
        "mwu.greater.statistic": mwu_greater.statistic,
        "mwu.greater.pvalue": mwu_greater.pvalue,
    }
