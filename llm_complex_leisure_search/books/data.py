# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Data extraction functionality for books."""

from rich.progress import track

PROMPT_TEMPLATE = """Identify the book the user is looking for as described in the request below:

Request: "{request}"

Please provide a ranked list of your 20 best guesses for the correct answer. Please answer in a JSON object that contains a ranked list of suggestions. Each suggestion should contain a field called 'answer' containing the suggestion (title and author), a field 'explanation' containing an explanation of why these books could be the correct answer, and a 'confidence' score that represents how confident you are of your suggestion."""  # noqa: E501


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
            "author": None,
        }
        for post in posts:
            if post["thread_id"] != first_post["thread_id"]:
                continue
            if (
                post["solved"] == "solved"  # If the post is solved
                and ":" in post["answer"]  # and there is a semi-colon (author - title)
            ):
                solution["author"] = post["answer"][: post["answer"].find(":")].strip()
                solution["title"] = post["answer"][post["answer"].find(":") + 1 :].strip()
            elif (
                post["solved"] == "solved / confirmed"  # If the post is solved
                and ":" in post["answer"]  # and there is a semi-colon (author - title)
            ):
                solution["author"] = post["answer"][: post["answer"].find(":")].strip()
                solution["title"] = post["answer"][post["answer"].find(":") + 1 :].strip()

        solved.append(solution)
    return solved
