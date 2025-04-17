"""Commands for data-sampling."""

import os
from csv import DictReader, DictWriter
from random import choice, shuffle

from numpy import array, average
from rich.progress import track
from scipy.spatial.distance import cosine
from typer import Typer

group = Typer(name="sampler", help="Commands for data sampling")


@group.command()
def jdoc_relevance_first_post_sample() -> None:
    """Create a sample of first posts based on the JDOC relevance assessments."""
    vectors = {}

    with open(os.path.join("data", "jdoc-relevance-assessments.tsv")) as in_f:
        reader = DictReader(in_f, delimiter="\t")
        vector_fields = reader.fieldnames[5:]
        for line in reader:
            vec = []
            for key in vector_fields:
                try:
                    vec.append(int(line[key]))
                except ValueError:
                    vec.append(0)
            vectors[line["id"]] = array(vec, dtype=int)

    final_sample = []
    for domain in track(("books", "games", "movies"), description="Creating samples"):
        entries = []
        for filename in ("extra", "jdoc"):
            with open(os.path.join("data", domain, f"first-posts_{filename}.tsv")) as in_f:
                reader = DictReader(in_f, delimiter="\t")
                for line in reader:
                    if line["thread_id"] in vectors:
                        entries.append(line)

        final_selection = None
        final_similarity = 2
        for _ in range(0, 10):
            selected = [choice(entries)]  # noqa: S311
            while len(selected) < 10:  # noqa: PLR2004
                shuffle(entries)
                min_sim = 2
                new_elem = None
                for entry in entries:
                    # Skip things already in the selected list
                    found = False
                    for previous in selected:
                        if entry["thread_id"] == previous["thread_id"]:
                            found = True
                            break
                    if found:
                        continue
                    # Calculate the similarity with all previously selected elements
                    similarities = []
                    for previous in selected:
                        similarities.append(cosine(vectors[previous["thread_id"]], vectors[entry["thread_id"]]))
                    avg_sim = average(similarities)
                    # Update the selected element if less similar than the previous one
                    if avg_sim < min_sim:
                        new_elem = entry
                        min_sim = avg_sim
                # Add the new element to the list of selected elements
                selected.append(new_elem)

            similarities = []
            for entry_a in selected:
                for entry_b in selected:
                    if entry_a["thread_id"] == entry_b["thread_id"]:
                        continue
                    similarities.append(cosine(vectors[entry_a["thread_id"]], vectors[entry_b["thread_id"]]))
            avg_sim = average(similarities)
            if avg_sim < final_similarity:
                final_selection = selected
                final_similarity = avg_sim
        final_sample.extend(final_selection)

    with open(os.path.join("data", "final-sample.tsv"), "w") as out_f:
        writer = DictWriter(out_f, ["thread_id", "domain", "type", "source", "request"], delimiter="\t")
        writer.writeheader()
        for entry in final_sample:
            writer.writerow(entry)
