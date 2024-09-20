# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The CLI application."""

from typer import Typer

from llm_complex_leisure_search.cli.books import group as books_group
from llm_complex_leisure_search.cli.games import group as games_group
from llm_complex_leisure_search.cli.gemini import group as gemini_group
from llm_complex_leisure_search.cli.movies import group as movies_group

app = Typer()
app.add_typer(books_group)
app.add_typer(games_group)
app.add_typer(gemini_group)
app.add_typer(movies_group)
