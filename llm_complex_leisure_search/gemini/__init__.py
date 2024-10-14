# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Gemini API functions."""

import json
from time import sleep

import google.generativeai as genai

from llm_complex_leisure_search.settings import settings
from llm_complex_leisure_search.util import extract_json


def generate_multiple_responses(prompt: str) -> list[dict | None]:
    """Generate multiple responses for a prompt using Gemini."""
    results = []
    for _ in range(0, settings.llm.max_attempts):
        result = generate_single_response(prompt)
        if result is not None:
            results.append(result)
        if len(results) >= settings.llm.retest_target:
            break
    return results


def generate_single_response(prompt: str) -> dict | None:
    """Generate single response for the prompt using Gemini."""
    sleep(2)
    genai.configure(api_key=settings.gemini.api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        text = response.text
        if "[" in text and "]" in text:
            try:
                return json.loads(extract_json(text))
            except json.JSONDecodeError:
                with open("invalid_json.txt", "+a") as out_f:
                    out_f.write("----------------------\n")
                    out_f.write("Invalid JSON extracted\n")
                    out_f.write("----------------------\n")
                    out_f.write(extract_json(text))
                return None
            except Exception:
                with open("invalid_json.txt", "+a") as out_f:
                    out_f.write("-----------------------\n")
                    out_f.write("Invalid JSON identified\n")
                    out_f.write("-----------------------\n")
                    out_f.write(text)
                return None
    except ValueError:
        sleep(60)
        return None
    return None
