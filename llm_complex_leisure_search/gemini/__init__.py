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


def generate_multiple_responses(prompt: str) -> list[dict | None]:
    """Generate multiple responses for a prompt using Gemini."""
    responses = []
    for _ in range(0, 3):
        responses.append(generate_single_response(prompt))
    return responses


def generate_single_response(prompt: str) -> dict | None:
    """Generate single response for the prompt using Gemini."""
    genai.configure(api_key=settings.gemini.api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    text = response.text
    if "[" in text and "]" in text:
        return json.loads(text[text.find("[") : text.rfind("]") + 1])
    return None
