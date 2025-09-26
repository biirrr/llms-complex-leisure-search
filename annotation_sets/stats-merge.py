"""Merge stats from Toine's data."""

import json
from csv import DictReader

ANNOTATED_FILE = "../../why-ki-requests-are-hard/data/annotated/games.json"
STATS_FILE = "/home/mhall/Downloads/statistics.games.reddit-spring2025.tsv"

with open(ANNOTATED_FILE) as in_f:
    annotated = json.load(in_f)

with open(STATS_FILE) as in_f:
    reader = DictReader(in_f, delimiter="\t")
    for line in reader:
        for entry in annotated:
            if entry["data"]["thread_id"] == line["thread_id"]:
                entry["stats"] = {}
                for key in [
                    "title_length_chars",
                    "text_length_chars",
                    "full_post_length_chars",
                    "title_length_words",
                    "text_length_words",
                    "full_post_length_words",
                    "title_readability",
                    "text_readability",
                    "full_post_readability",
                    "reply_counter",
                    "replies_until_solved",
                    "replies_until_confirmed",
                    "OP_reply_count",
                    "OP_reply_count_before_confirmed",
                    "solved_by_OP",
                    "unique_user_replies",
                ]:
                    try:
                        entry["stats"][key] = float(line[key])
                    except ValueError:
                        if key in entry["stats"]:
                            del entry["stats"][key]
                        pass

with open(ANNOTATED_FILE, "w") as out_f:
    json.dump(annotated, out_f)
