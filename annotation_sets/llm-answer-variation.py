"""Basic LLM stat generation."""

import json
import os
from math import ceil, floor

result_counts = {"books": [], "games": [], "movies": []}

for foldername in os.listdir("."):
    if foldername.startswith("gpt-4o-mini") and not foldername.endswith(".zip"):
        category = ""
        if "books" in foldername:
            category = "books"
        elif "games" in foldername:
            category = "games"
        elif "movies" in foldername:
            category = "movies"
        for filename in os.listdir(foldername):
            if filename.endswith(".json"):
                with open(os.path.join(foldername, filename)) as in_f:
                    try:
                        data = json.load(in_f)
                        elements = None
                        if "suggestions" in data:
                            elements = data["suggestions"]
                        elif "recommendations" in data:
                            elements = data["recommendations"]
                        elif "movies" in data:
                            elements = data["movies"]
                        elif " suggestions" in data:
                            elements = data[" suggestions"]
                        elif "ranked_suggestions" in data:
                            elements = data["ranked_suggestions"]
                        elif "rankedSuggestions" in data:
                            elements = data["rankedSuggestions"]
                        result_counts[category].append(len(elements))
                    except:  # noqa:E722, S110
                        pass


def quantile(counts, frac):
    """Quantile calculation."""
    idx = len(counts) * frac
    if ceil(idx) == floor(idx):
        return (counts[floor(idx)] + counts[floor(idx + 1)]) / 2
    else:
        return counts[floor(idx)]


for category in ["books", "games", "movies"]:
    print("category")  # noqa:T201
    result_counts[category].sort()
    print("min", result_counts[category][0])  # noqa:T201
    print("1st", quantile(result_counts[category], 0.25))  # noqa:T201
    print("median", quantile(result_counts[category], 0.5))  # noqa:T201
    print("3rd", quantile(result_counts[category], 0.75))  # noqa:T201
    print("max", result_counts[category][-1])  # noqa:T201
    print()  # noqa:T201
