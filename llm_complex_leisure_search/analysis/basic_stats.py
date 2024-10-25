"""Basic statistics analysis."""

import json
import os
from csv import DictReader

import numpy

from llm_complex_leisure_search.constants import DATA_SETS


def data_set_summary_stats(domain: str) -> dict:
    """Generate basic summary statistics for a data-set."""
    result = {}
    thread_ids = set()
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"posts_{data_set}.csv")) as in_f:
            reader = DictReader(in_f)
            for line in reader:
                thread_ids.add(line["thread_id"])
    result["threads.total"] = len(thread_ids)
    solved = 0
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + len(json.load(in_f))
    result["human.solved"] = solved
    result["human.solved.fraction"] = result["human.solved"] / result["threads.total"]
    return result


def llm_summary_stats(domain: str, llm: str) -> dict:
    """Generate basic summary statistics for a model."""
    solved = []
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + json.load(in_f)
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    result_lengths = []
    for solution in solutions:
        for result_list in solution["results"]:
            result_lengths.append(len(result_list))
    row = {
        "threads.answered": len(solutions),
        "threads.answered.fraction": len(solutions) / len(solved),
        "results.length.min": numpy.min(result_lengths),
        "results.length.q1": numpy.percentile(result_lengths, 25),
        "results.length.median": numpy.percentile(result_lengths, 50),
        "results.length.q3": numpy.percentile(result_lengths, 75),
        "results.length.max": numpy.max(result_lengths),
    }
    return row


def llm_solved_at_rank(domain: str, llm: str, rank: int) -> dict:
    """Calculate how many solved tasks at a given rank in any one of the three result lists."""
    solved = []
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + json.load(in_f)
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    total_found = 0
    for task in solved:
        for solution in solutions:
            if task["thread_id"] == solution["thread_id"]:
                found = False
                for result_list in solution["results"]:
                    for entry in result_list[: rank + 1]:
                        if task["title"] == entry["title"]:
                            found = True
                if found:
                    total_found += 1
    result = {f"solved.{rank + 1}": total_found, f"solved.{rank + 1}.fraction": total_found / len(solved)}
    return result


def llm_solved_at_rank_single(domain: str, llm: str, rank: int) -> dict:
    """Calculate how many solved tasks at a given rank in each of the result lists."""
    solved = []
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + json.load(in_f)
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    total_found = 0
    for task in solved:
        for solution in solutions:
            if task["thread_id"] == solution["thread_id"]:
                for result_list in solution["results"]:
                    for entry in result_list[: rank + 1]:
                        if task["title"] == entry["title"]:
                            total_found += 1
                            break
    result = {f"solved.{rank + 1}": total_found, f"solved.{rank + 1}.fraction": total_found / (len(solved) * 3)}
    return result


def artifact_counts(domain: str, llm: str) -> dict:
    """Count how many entries exist."""
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    with open(os.path.join("data", domain, "unique-answers.json")) as in_f:
        unique_answers = json.load(in_f)
        for answer in unique_answers:
            answer["answer"] = (answer["answer"][0], tuple(answer["answer"][1]))
    titles = 0
    existing_titles = 0
    existing_titles_with_qualifier = 0
    for solution in solutions:
        for result_list in solution["results"]:
            for entry in result_list:
                entry_tuple = (entry["title"], tuple(entry["qualifiers"]))
                titles += 1
                for answer in unique_answers:
                    if entry_tuple == answer["answer"]:
                        if answer["exists"]:
                            existing_titles += 1
                        if answer["exists_with_qualifier"]:
                            existing_titles_with_qualifier += 1
                            break
    return {
        "generated.total": titles,
        "generated.existing": existing_titles,
        "generated.existing.fraction": existing_titles / titles,
        "generated.existing.exact": existing_titles_with_qualifier,
        "generated.existing.exact.fraction": existing_titles_with_qualifier / titles,
    }


def duplicate_counts(domain: str, llm: str) -> dict:
    """Count how many duplicates exist."""
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    thread_duplicates = 0
    duplicates = []
    for solution in solutions:
        for result_list in solution["results"]:
            uniques = {(result["title"], tuple(result["qualifiers"])) for result in result_list}
            if len(result_list) - len(uniques) > 0:
                thread_duplicates += 1
            duplicates.append(len(result_list) - len(uniques))
    return {
        "results.duplicates": thread_duplicates,
        "results.duplicates.fraction": thread_duplicates / (len(solutions) * 3),
        "duplicates.average": sum(duplicates) / len(duplicates),
        "duplicates.min": numpy.min(duplicates),
        "duplicates.q1": numpy.percentile(duplicates, 25),
        "duplicates.median": numpy.percentile(duplicates, 50),
        "duplicates.q3": numpy.percentile(duplicates, 75),
        "duplicates.max": numpy.max(duplicates),
    }
