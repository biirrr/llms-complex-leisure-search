"""Extract threads that haven't been processed previously."""

import os
from csv import DictReader, DictWriter

ids1 = set()
ids2 = set()

for filename in os.listdir("games"):
    if not filename.endswith(".tsv"):
        continue
    with open(f"games/{filename}") as in_f:
        reader = DictReader(in_f, delimiter="\t")
        for line in reader:
            ids1.add(line["thread_id"])

with open("test-set-human-llm-solved.tsv") as in_f:
    reader = DictReader(in_f, delimiter="\t")
    with open("test-set-additional3.tsv", "w") as out_f:
        writer = DictWriter(out_f, fieldnames=reader.fieldnames, delimiter="\t")
        writer.writeheader()
        for line in reader:
            ids2.add(line["thread_id"])
            if line["thread_id"] not in ids1:
                writer.writerow(line)

print(len(ids2 - ids1))  # noqa: T201
