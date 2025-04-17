# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The CLI application."""

from typer import Typer

from llm_complex_leisure_search.cli.analysis import group as analysis_group
from llm_complex_leisure_search.cli.books import group as books_group
from llm_complex_leisure_search.cli.data import group as data_group
from llm_complex_leisure_search.cli.fix import group as fix_group
from llm_complex_leisure_search.cli.games import group as games_group
from llm_complex_leisure_search.cli.movies import group as movies_group
from llm_complex_leisure_search.cli.sampler import group as samplers_group

app = Typer(pretty_exceptions_enable=False)
app.add_typer(analysis_group)
app.add_typer(books_group)
app.add_typer(data_group)
app.add_typer(fix_group)
app.add_typer(games_group)
app.add_typer(movies_group)
app.add_typer(samplers_group)
