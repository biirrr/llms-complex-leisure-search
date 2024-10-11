"""Basic statistics analysis."""

import json
import os
from csv import DictReader


def data_set_summary_stats(domain: str, data_set: str) -> dict:
    """Generate basic summary statistics for a data-set."""
    result = {}
    with open(os.path.join("data", domain, f"posts_{data_set}.csv")) as in_f:
        reader = DictReader(in_f)
        thread_ids = set()
        for line in reader:
            thread_ids.add(line["thread_id"])
        result["threads.total"] = len(thread_ids)
    with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
        result["human.solved"] = len(json.load(in_f))
    result["human.solved.fraction"] = result["human.solved"] / result["threads.total"]
    return result


def llm_solved_at_rank(domain: str, data_set: str, llm: str, rank: int) -> dict:
    """Calculate how many solved tasks at a given rank in the results."""
    with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
        solved = json.load(in_f)
    with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
        solutions = json.load(in_f)
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
    result = {f"{llm}.recall.{rank + 1}": total_found, f"{llm}.recall.{rank + 1}.fraction": total_found / len(solved)}
    return result
