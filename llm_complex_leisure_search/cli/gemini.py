# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Gemini-related CLI commands."""

import json
from typing import Annotated

from typer import Argument, FileText, FileTextWrite, Typer

from llm_complex_leisure_search.gemini import generate_multiple_responses

group = Typer(name="gemini", help="Commands for Gemini-related processing")


@group.command()
def process_requests(
    requests: Annotated[FileText, Argument()],
    responses: Annotated[FileTextWrite, Argument()],
) -> None:
    """Generate JSON using Gemini."""
    result = []
    for entry in json.load(requests):
        entry["gemini"] = generate_multiple_responses(entry["templated_request"])
        result.append(entry)
    json.dump(result, responses)
