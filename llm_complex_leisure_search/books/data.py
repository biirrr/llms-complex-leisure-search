# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Data extraction functionality for books."""

from rich.progress import track

PROMPT_TEMPLATE = """Identify the book the user is looking for as described in the request below:

Request: "{request}"

Please provide a ranked list of your 20 best guesses for the correct answer. Please answer in a JSON object that contains a ranked list of suggestions. Each suggestion should contain a field called 'answer' containing the suggestion (title and author), a field 'explanation' containing an explanation of why these books could be the correct answer, and a 'confidence' score that represents how confident you are of your suggestion."""  # noqa: E501


def extract_solved_threads(posts: list[dict]) -> list[dict]:
    """Extract all solved threads from a list of posts."""
    solved = []
    thread_id = None
    solution = {
        "confirmed": False,
        "prompt": None,
        "request": None,
        "solved": False,
        "thread_id": None,
        "title": None,
        "author": None,
    }
    for post in track(posts, description="Extracting solved threads"):
        if thread_id != post["thread_id"]:
            if solution["solved"]:
                solved.append(solution)
            thread_id = post["thread_id"]
            solution = {
                "confirmed": False,
                "prompt": None,
                "request": None,
                "solved": False,
                "thread_id": None,
                "title": None,
                "author": None,
            }
        if solution["thread_id"] is None:
            solution["thread_id"] = post["thread_id"]
            solution["request"] = post["comment_text"]
            solution["prompt"] = PROMPT_TEMPLATE.format(request=solution["request"])
        if (
            post["solved"] == "solved"  # If the post is solved
            and ":" in post["answer"]  # and there is a semi-colon (author - title)
            and not solution["solved"]  # and it has not already been marked as solved
        ):
            solution["solved"] = True
            solution["title"] = post["answer"][: post["answer"].find(":")]
            solution["author"] = post["answer"][post["answer"].find(":") + 1 :]
        elif (
            post["solved"] == "solved and confirmed"  # If the post is solved
            and ":" in post["answer"]  # and there is a semi-colon (author - title)
            and not solution["solved"]  # and it has not already been marked as solved
        ):
            solution["solved"] = True
            solution["title"] = post["answer"]
            solution["author"] = post["answer"][post["answer"].find(":") + 1 :]
            solution["confirmed"] = True
        elif post["solved"] == "confirmed":
            solution["confirmed"] = True
    if solution["solved"]:
        solved.append(solution)
    return solved
