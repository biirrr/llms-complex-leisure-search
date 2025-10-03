"""Merge stats from Toine's data."""

import json
from csv import DictReader

for annotated_file, stats_file in [
    (
        "../../why-ki-requests-are-hard/data/annotated/books.json",
        "/home/mhall/Downloads/statistics/statistics.books.reddit-spring+summer2025.tsv",
    ),
    (
        "../../why-ki-requests-are-hard/data/annotated/games.json",
        "/home/mhall/Downloads/statistics/statistics.games.reddit-spring2025.tsv",
    ),
    (
        "../../why-ki-requests-are-hard/data/annotated/movies.json",
        "/home/mhall/Downloads/statistics/statistics.movies.reddit-spring2025.tsv",
    ),
]:
    with open(annotated_file) as in_f:
        annotated = json.load(in_f)

    with open(stats_file) as in_f:
        reader = DictReader(in_f, delimiter="\t")
        for line in reader:
            for entry in annotated:
                if str(entry["data"]["thread_id"]) == str(line["thread_id"]):
                    if "stats" not in entry:
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

    with open(annotated_file, "w") as out_f:
        json.dump(annotated, out_f)
