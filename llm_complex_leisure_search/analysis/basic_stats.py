"""Basic statistics analysis."""

import json
import os
from collections import Counter
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
        "results.total": sum(result_lengths),
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


def llm_solved_mmr(domain: str, data: dict, solved_factor: int = 1, field_suffix: str = "") -> dict:
    """Calculate the MMR for the given set of solved data."""
    solved = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + json.load(in_f)
    total = 0
    for rank in range(1, 21):
        total = total + (1 / rank * data[f"solved.{rank}{field_suffix}"])
    return {"mmr": total / (len(solved) * solved_factor)}


def llm_solved_at_rank_avg(domain: str, llm: str, rank: int) -> dict:
    """Calculate how many solved tasks at a given rank as an average of the three runs."""
    solved = []
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + json.load(in_f)
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    totals = numpy.array([0, 0, 0])
    for task in solved:
        for solution in solutions:
            if task["thread_id"] == solution["thread_id"]:
                for idx, result_list in enumerate(solution["results"]):
                    for entry in result_list[: rank + 1]:
                        if task["title"] == entry["title"]:
                            totals[idx] += 1
                            break
    totals_frac = totals / len(solved)
    result = {
        f"solved.{rank + 1}.avg": numpy.average(totals),
        f"solved.{rank + 1}.stdev": numpy.std(totals),
        f"solved.{rank+1}.fraction.avg": numpy.average(totals_frac),
        f"solved.{rank+1}.fraction.stdev": numpy.std(totals_frac),
    }
    return result


def llm_solved_stats(domain: str, llm: str) -> dict:
    """Calculate statistics of how many solved across all result lists."""
    solved = []
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + json.load(in_f)
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    found_counts = []
    for task in solved:
        for solution in solutions:
            if task["thread_id"] == solution["thread_id"]:
                found_count = 0
                for result_list in solution["results"]:
                    found = False
                    for entry in result_list:
                        if task["title"] == entry["title"]:
                            found = True
                            break
                    if found:
                        found_count += 1
                found_counts.append(found_count)
    counts = Counter(found_counts)
    return {
        "solved.0": counts[0],
        "solved.1": counts[1],
        "solved.2": counts[2],
        "solved.3": counts[3],
        "solved.0.fraction": counts[0] / len(solved),
        "solved.1.fraction": counts[1] / len(solved),
        "solved.2.fraction": counts[2] / len(solved),
        "solved.3.fraction": counts[3] / len(solved),
    }


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


def confidence_counts(domain: str, llm: str) -> dict:
    """Analyse the confidence distribution."""
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    confidence = []
    no_confidence = 0
    for solution in solutions:
        for result_list in solution["results"]:
            for result in result_list:
                if "normalised_confidence" in result:
                    confidence.append(result["normalised_confidence"])
                else:
                    no_confidence += 1
    return {
        "confidence.average": numpy.average(confidence),
        "confidence.std": numpy.std(confidence),
        "confidence.min": numpy.min(confidence),
        "confidence.q1": numpy.percentile(confidence, 25),
        "confidence.median": numpy.percentile(confidence, 50),
        "confidence.q3": numpy.percentile(confidence, 75),
        "confidence.max": numpy.max(confidence),
        "confidence.noscore": no_confidence,
    }
