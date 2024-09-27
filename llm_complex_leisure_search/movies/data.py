# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Data extraction functionality for books."""

from rich.progress import track

from llm_complex_leisure_search.util import split_title_years

PROMPT_TEMPLATE = """Identify the movie the user is looking for as described in the request below:

Request: "{request}"

Please provide a ranked list of your 20 best guesses for the correct answer. Please answer in a JSON object that contains a ranked list of suggestions. Each suggestion should contain a field called 'answer' containing the suggestion (title and release year), a field 'explanation' containing an explanation of why these movies could be the correct answer, and a 'confidence' score that represents how confident you are of your suggestion."""  # noqa: E501


def extract_solved_threads(first_posts: list[dict], posts: list[dict], ignored_ids: list[str]) -> list[dict]:
    """Extract all solved threads from a list of posts."""
    solved = []
    for first_post in track(first_posts, description="Finding solutions"):
        if first_post["thread_id"] in ignored_ids:
            continue
        solution = {
            "thread_id": first_post["thread_id"],
            "request": first_post["request"],
            "prompt": PROMPT_TEMPLATE.format(request=first_post["request"]),
            "title": None,
            "years": [],
            "imdb_id": None,
        }
        for post in posts:
            if post["thread_id"] != first_post["thread_id"]:
                continue
            if post["solved"] == "solved" or post["solved"] == "solved / confirmed":
                title, years = split_title_years(post["answer"])
                solution["title"] = title
                solution["years"] = years
                solution["imdb_id"] = post["IMDB_id"]
        if solution["imdb_id"]:
            solved.append(solution)
    return solved
