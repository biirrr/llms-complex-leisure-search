# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Llama 3.2 LLM."""

import json

from httpx import ReadTimeout
from ollama import Client

from llm_complex_leisure_search.settings import settings
from llm_complex_leisure_search.util import extract_json


def generate_multiple_responses(prompt: str) -> list[dict | None]:
    """Generate multiple responses for a prompt using Llama 3.2."""
    results = []
    for _ in range(0, settings.llm.max_attempts):
        result = generate_single_response(prompt)
        if result is not None:
            results.append(result)
        if len(results) >= settings.llm.retest_target:
            break
    return results


def generate_single_response(prompt: str) -> dict | None:
    """Generate single response for the prompt using Llama 3.2."""
    try:
        client = Client("http://localhost:11434", timeout=300)
        response = client.generate("llama3.2", prompt=prompt, format="json")
        text = response["response"]
        if "[" in text and "]" in text:
            try:
                attempt = json.loads(extract_json(text))
                for entry in attempt:
                    if not isinstance(entry, dict):
                        raise ValueError("Not a dict entry")  # noqa: EM101
                return attempt
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
        return None
    except ReadTimeout:
        return None
    return None
