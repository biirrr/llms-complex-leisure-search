"""A simple script to calculate some annotation stats."""

import collections
import csv
import itertools
import json


def headings_key(heading):
    """Column sorting key calculation."""
    if heading == "id":
        return -1
    elif heading.startswith("start."):
        return 0
    elif heading.startswith("end."):
        return 1
    elif heading.startswith("text."):
        return 2
    elif heading.startswith("label."):
        return 3


with open("annotations-sample.json") as in_f:
    data = json.load(in_f)

DISTANCE_THRESHOLD = 5
divergent_annotations = []
non_divergent_annotations = []
majority_annotations = []
headings = set()

for entry in data:
    shared_annotations = []
    for idx1 in range(0, len(entry["annotations"]) - 1):
        annotator1 = entry["annotations"][idx1]
        for idx2 in range(idx1 + 1, len(entry["annotations"])):
            annotator2 = entry["annotations"][idx2]
            for span1, span2 in itertools.product(annotator1["result"], annotator2["result"]):
                if (
                    abs(span1["value"]["start"] - span2["value"]["start"]) <= DISTANCE_THRESHOLD
                    and abs(span1["value"]["end"] - span2["value"]["end"]) <= DISTANCE_THRESHOLD
                ):
                    existing_ann = None
                    for shared_ann in shared_annotations:
                        if (
                            f"start.{annotator1['completed_by']}" in shared_ann
                            and shared_ann[f"start.{annotator1['completed_by']}"] == span1["value"]["start"]
                            and shared_ann[f"end.{annotator1['completed_by']}"] == span1["value"]["end"]
                        ):
                            existing_ann = shared_ann
                            break
                    if existing_ann is None:
                        shared_annotations.append(
                            {
                                "id": entry["id"],
                                f"start.{annotator1['completed_by']}": span1["value"]["start"],
                                f"start.{annotator2['completed_by']}": span2["value"]["start"],
                                f"end.{annotator1['completed_by']}": span1["value"]["end"],
                                f"end.{annotator2['completed_by']}": span2["value"]["end"],
                                f"text.{annotator1['completed_by']}": span1["value"]["text"],
                                f"text.{annotator2['completed_by']}": span2["value"]["text"],
                                f"label.{annotator1['completed_by']}": span1["value"]["labels"][0],
                                f"label.{annotator2['completed_by']}": span2["value"]["labels"][0],
                            }
                        )
                    else:
                        existing_ann[f"start.{annotator2['completed_by']}"] = span2["value"]["start"]
                        existing_ann[f"end.{annotator2['completed_by']}"] = span2["value"]["end"]
                        existing_ann[f"text.{annotator2['completed_by']}"] = span2["value"]["text"]
                        existing_ann[f"label.{annotator2['completed_by']}"] = span2["value"]["labels"][0]
    for annotation in shared_annotations:
        labels = set()
        annotators = set()
        label_values = []
        for key, value in annotation.items():
            if key.startswith("label."):
                labels.add(value)
                annotators.add(key[6:])
                label_values.append(value)
        if len(labels) > 1:
            headings.update(annotation.keys())
            divergent_annotations.append(annotation)
            if collections.Counter(label_values).most_common(1)[0][1] > len(annotators) / 2:
                majority_annotations.append(annotators)
        else:
            non_divergent_annotations.append(annotation)


headings_list = list(headings)
headings_list.sort(key=headings_key)
with open("annotations-diff.tsv", "w") as out_f:
    writer = csv.DictWriter(out_f, fieldnames=headings_list, delimiter="\t", restval="N/A")
    writer.writeheader()
    for annotation in divergent_annotations:
        writer.writerow(annotation)

print(f"Total: {len(non_divergent_annotations) + len(divergent_annotations)}")  # noqa: T201
print(f"Non-divergent: {len(non_divergent_annotations)}")  # noqa: T201
print(f"Divergent: {len(divergent_annotations)}")  # noqa: T201
print(f"Majority: {len(majority_annotations)}")  # noqa: T201
print(  # noqa: T201
    f"Complete agreement: {(len(non_divergent_annotations)) / (len(divergent_annotations) + len(non_divergent_annotations))}"  # noqa: E501
)
print(  # noqa: T201
    f"Majority agreement: {(len(non_divergent_annotations) + len(majority_annotations)) / (len(divergent_annotations) + len(non_divergent_annotations))}"  # noqa: E501
)
