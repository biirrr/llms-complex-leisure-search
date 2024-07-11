# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Gemini API functions."""

import json

import google.generativeai as genai

from llm_complex_leisure_search.settings import settings

TEMPLATE = """Identify the {domain} the user is looking for as described in the request below:

Request: "{request}"

Please provide a ranked list of your 20 best guesses for the correct answer. Please answer in a JSON object that contains a ranked list of suggestions. Each suggestion should contain a field called 'answer' containing the suggestion, a field 'explanation' containing an explanation of why these {domain}s could be the correct answer, and a 'confidence' score that represents how confident you are of your suggestion.
"""  # noqa: E501


def generate_json(domain: str) -> dict | None:
    """Generate JSON using Gemini using an example request."""
    genai.configure(api_key=settings.gemini.api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        TEMPLATE.format(
            domain=domain,
            request="""I'm looking for one of those virus movies with a very specific ending. Hi all. Just hoping someone out there can identify a movie from its ending. I've googled all sorts of combinations and done everything I can think of to find out what it is, but I've still come up blank. Ok, so it's another one of those post deadly virus survivor films.  I can't even remember who was in it, but I remember it had a pretty brutal ending. After spending the movie trying to figure out how to survive and by the end it looked like death was inevitable, so to be kind the male protagonist shot everyone he had been travelling with in their car.  As he is about to turn the gun on himself, the army come to the scene and it turns out they had an answer to help survive. I just remember thinking it was a cruel thing that the character would have to then live with. Any help on this would be fabulous because I really can't find the movie this engine belongs to! Thanks in advance.""",  # noqa: E501
        )
    )
    text = response.text
    if "[" in text and "]" in text:
        return json.loads(text[text.find("[") : text.rfind("]") + 1])
    return None
