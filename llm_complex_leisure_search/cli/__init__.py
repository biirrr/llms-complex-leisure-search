# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The CLI application."""

from typer import Typer

from llm_complex_leisure_search.cli.games import group as games_group

app = Typer()
app.add_typer(games_group)
