# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Data extraction functionality for games."""

from rich.progress import track

from llm_complex_leisure_search.games.igdb import get_game

PROMPT_TEMPLATE = """Identify the game the user is looking for as described in the request below:

Request: "{request}"

Please provide a ranked list of your 20 best guesses for the correct answer. Please answer in a JSON object that contains a ranked list of suggestions. Each suggestion should contain a field called 'answer' containing the suggestion (title and release year), a field 'explanation' containing an explanation of why these games could be the correct answer, and a 'confidence' score that represents how confident you are of your suggestion."""  # noqa: E501


def extract_solved_threads(posts: list[dict]) -> list[dict]:
    """Extract all solved threads from a list of posts."""
    solved = []
    thread_id = None
    solution = {
        "confirmed": False,
        "igdb_id": None,
        "prompt": None,
        "request": None,
        "solved": False,
        "thread_id": None,
        "title": None,
        "years": None,
    }
    for post in track(posts, description="Extracting solved threads"):
        if thread_id != post["thread_id"]:
            if solution["solved"]:
                solved.append(solution)
            thread_id = post["thread_id"]
            solution = {
                "confirmed": False,
                "igdb_id": None,
                "prompt": None,
                "request": None,
                "solved": False,
                "thread_id": None,
                "title": None,
                "year": None,
            }
        if solution["thread_id"] is None:
            solution["thread_id"] = post["thread_id"]
            solution["request"] = post["comment_text"]
            solution["prompt"] = PROMPT_TEMPLATE.format(request=solution["request"])
        if post["solved"] == "solved" and post["answer"].strip() and post["IGDB_id"].strip() and not solution["solved"]:
            solution["solved"] = True
            solution["title"] = post["answer"]
            solution["igdb_id"] = post["IGDB_id"]
        elif (
            post["solved"] == "solved and confirmed"
            and post["answer"].strip()
            and post["IGDB_id"].strip()
            and not solution["solved"]
        ):
            solution["solved"] = True
            solution["title"] = post["answer"]
            solution["igdb_id"] = post["IGDB_id"]
            solution["confirmed"] = True
        elif post["solved"] == "confirmed":
            solution["confirmed"] = True
    if solution["solved"]:
        solved.append(solution)
    for solution in track(solved, description="Add publication years"):
        game = get_game(solution["igdb_id"])
        solution["years"] = game["release_years"]
    return solved
