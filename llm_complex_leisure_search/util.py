# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Utility functionality."""


class JSONExtractionError(Exception):
    """Error indicating that no valid JSON could be extracted."""


def extract_json(text: str) -> str:
    """Extract JSON data from a text."""
    text = text[text.find("[") :]
    buffer = []
    square_brackets = 0
    escape_next = False
    in_string = False
    for char in text:
        if char == "[" and not in_string and not escape_next:
            square_brackets = square_brackets + 1
        elif char == "]" and not in_string and not escape_next:
            square_brackets = square_brackets - 1
        elif char == '"' and not escape_next:
            in_string = not in_string
        elif char == "\\" and not escape_next:
            escape_next = True
        else:
            escape_next = False
        buffer.append(char)
        if square_brackets == 0:
            break
    if square_brackets > 0:
        msg = f"Unbalanced brackets {square_brackets}"
        raise JSONExtractionError(msg)
    return "".join(buffer)


def split_book_title_by_author(answer: str) -> tuple[str, str]:
    """Split an answer containing the text `title by author` into a `(title, author)` tuple."""
    if " by " in answer:
        return (
            answer[: answer.find(" by ")].strip(),
            answer[answer.find(" by ") + 4 :].strip(),
        )
    else:
        return (answer.strip(), None)
