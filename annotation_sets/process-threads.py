"""Process threads to generate data for the human annotation."""

import json
import os
from csv import DictReader, DictWriter
from random import shuffle

# TSV_FN = "books-threads.tsv"
# LLM_BASE_DIR = "gpt-4o-mini.books.extra.reddit-spring2025"
# TSV_FN = "movies-threads.tsv"
# LLM_BASE_DIR = "gpt-4o-mini.movies.extra.reddit-spring2025"
TSV_FN = "games-threads.tsv"
LLM_BASE_DIR = "gpt-4o-mini.games.extra.reddit-spring2025"

GENERATE_EXTRAS = False
ADD_TITLES = False

UNSOVLED_MAX = 50
HUMAN_SOLVED_MAX = 50
LLM_SOLVED_MAX = 50
skip_thread_ids = []

# Load extra book titles
titles = {}
if ADD_TITLES:
    with open("first-posts-solved.extra.books.reddit-spring2025.tsv") as in_f:
        reader = DictReader(in_f, delimiter="\t")
        for line in reader:
            if line["thread_id"] not in titles:
                titles[line["thread_id"]] = line["title"]
    with open("first-posts-solved.extra.books.reddit-summer2025.tsv") as in_f:
        reader = DictReader(in_f, delimiter="\t")
        for line in reader:
            if line["thread_id"] not in titles:
                titles[line["thread_id"]] = line["title"]

if GENERATE_EXTRAS:
    with open("test-set-initial.tsv") as in_f:
        reader = DictReader(in_f, delimiter="\t")
        for line in reader:
            skip_thread_ids.append(line["thread_id"])

result = []
with open(TSV_FN) as in_f:
    reader = DictReader(in_f, delimiter="\t")
    reader_lines = []
    for line in reader:
        reader_lines.append(line)
    reader_lines.sort(key=lambda line: (line["thread_id"], int(line["comment_id"])))
    thread_id = None
    first_post = None
    solved = False
    confirmed = False
    unusable = False
    for line in reader_lines:
        if thread_id != line["thread_id"]:
            if first_post is not None and not unusable:
                if solved and confirmed:
                    first_post["category"] = "solved"
                if first_post["thread_id"] not in skip_thread_ids:
                    result.append(first_post)
            first_post = line
            first_post["category"] = "unsolved"
            first_post["uploaded"] = False
            solved = False
            confirmed = False
            unusable = False
            thread_id = line["thread_id"]
            if ADD_TITLES:
                first_post["comment"] = f"{titles[first_post['thread_id']]}. {first_post['comment']}"
        if line["solved"].strip() in ("solved", "solves"):
            solved = True
            if line["answer"].strip():
                first_post["answer"] = line["answer"].strip()
        elif line["solved"].strip() == "confirmed":
            confirmed = True
            if line["answer"].strip():
                solved = True
                first_post["answer"] = line["answer"].strip()
        elif line["solved"].strip() in ("solved / confirmed", "solved / confirmes"):
            solved = True
            confirmed = True
            if line["answer"].strip():
                first_post["answer"] = line["answer"].strip()
        elif line["solved"].strip() in ("unusable", "unsolved / unuasable", "unsolved / unusable"):
            unusable = True
        elif line["solved"].strip() == "unsolved":
            pass
        elif line["solved"].strip() in ("confirmed?", "thanks?", "solved?", "bot"):
            first_post["category"] = "maybe-solved"
        elif line["solved"] != "":
            print(line["solved"])  # noqa: T201
    if first_post is not None and first_post["thread_id"] not in skip_thread_ids:
        result.append(first_post)

solved = 0
llm_solved_count = 0
for row in result:
    if row["category"] == "solved":
        solved = solved + 1
        llm_solved = False
        with open(f"{LLM_BASE_DIR}/{row['thread_id']}.gpt-4o-mini.v1.json") as in_f:
            try:
                data = json.load(in_f)
                elements = []
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
                else:
                    print(data.keys())  # noqa: T201
                if "(" in row["answer"]:
                    row["answer"] = row["answer"][: row["answer"].find("(")].strip()
                if row["category"] == "solved" and row["answer"].strip() == "":
                    print("arg")  # noqa: T201
                for item in elements:
                    answer = item["answer"]
                    if "(" in answer:
                        answer = answer[: answer.find("(")].strip()
                    elif " by " in answer:
                        answer = answer[: answer.find(" by ")].strip()
                    if answer.strip() == row["answer"].strip():
                        row["category"] = "llm-solved"
                        llm_solved_count = llm_solved_count + 1
                        break
            except json.decoder.JSONDecodeError:
                pass

shuffle(result)
unsolved = [
    {"thread_id": row["thread_id"], "comment": row["comment"], "category": "unsolved"}
    for row in result
    if row["category"] == "unsolved"
]
human_solved = [
    {"thread_id": row["thread_id"], "comment": row["comment"], "category": "solved"}
    for row in result
    if row["category"] == "solved"
]
human_llm_solved = [
    {"thread_id": row["thread_id"], "comment": row["comment"], "category": "llm-solved"}
    for row in result
    if row["category"] == "llm-solved"
]

with open("test-set-unsolved.tsv", "w") as out_f:
    writer = DictWriter(out_f, fieldnames=["thread_id", "comment", "category"], delimiter="\t", extrasaction="ignore")
    writer.writeheader()
    for line in unsolved:
        writer.writerow(line)
with open("test-set-human-solved.tsv", "w") as out_f:
    writer = DictWriter(out_f, fieldnames=["thread_id", "comment", "category"], delimiter="\t", extrasaction="ignore")
    writer.writeheader()
    for line in human_solved:
        writer.writerow(line)
with open("test-set-human-llm-solved.tsv", "w") as out_f:
    writer = DictWriter(out_f, fieldnames=["thread_id", "comment", "category"], delimiter="\t", extrasaction="ignore")
    writer.writeheader()
    for line in human_llm_solved:
        writer.writerow(line)

unsolved_count = 0
human_solved_count = 0
human_llm_solved_count = 0
output_filename = "test-set-additional.tsv" if GENERATE_EXTRAS else "test-set-initial.tsv"
with open(os.path.join(output_filename), "w") as out_f:
    writer = DictWriter(out_f, fieldnames=["thread_id", "comment", "category"], delimiter="\t", extrasaction="ignore")
    writer.writeheader()
    for row in result:
        if row["category"] == "unsolved" and unsolved_count < UNSOVLED_MAX:
            writer.writerow(row)
            unsolved_count = unsolved_count + 1
        elif row["category"] == "solved" and human_solved_count < HUMAN_SOLVED_MAX:
            writer.writerow(row)
            human_solved_count = human_solved_count + 1
        elif row["category"] == "llm-solved" and human_llm_solved_count < LLM_SOLVED_MAX:
            writer.writerow(row)
            human_llm_solved_count = human_llm_solved_count + 1

print(f"Unsolved: {unsolved_count}")  # noqa: T201
print(f"Human solved: {human_solved_count}")  # noqa: T201
print(f"LLM Solved: {human_llm_solved_count}")  # noqa: T201
