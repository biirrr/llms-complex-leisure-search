# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Gemini-related CLI commands."""

from rich import print as console
from typer import Typer

from llm_complex_leisure_search.gemini import generate_json as api_generate_json

group = Typer(name="gemini", help="Commands for Gemini-related processing")


@group.command()
def generate_json(domain: str) -> None:
    """Generate JSON using Gemini."""
    console(api_generate_json(domain))
