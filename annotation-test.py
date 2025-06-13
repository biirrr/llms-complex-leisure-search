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
                annotation["final_label"] = collections.Counter(label_values).most_common(1)[0][0]
                majority_annotations.append(annotation)
            else:
                if entry["data"]["domain"] == "book":
                    if f"label.3" in annotation:
                        annotation["final_label"] = annotation[f"label.3"]
                elif entry["data"]["domain"] == "game":
                    if f"label.6" in annotation:
                        annotation["final_label"] = annotation[f"label.6"]
                elif entry["data"]["domain"] == "movie":
                    if f"label.4" in annotation:
                        annotation["final_label"] = annotation[f"label.4"]
        else:
            non_divergent_annotations.append(annotation)


headings_list = list(headings)
headings_list.sort(key=headings_key)
with open("annotations-diff.tsv", "w") as out_f:
    writer = csv.DictWriter(out_f, fieldnames=headings_list, delimiter="\t", restval="N/A", extrasaction="ignore")
    writer.writeheader()
    for annotation in divergent_annotations:
        writer.writerow(annotation)

annotations_map = {}
for annotation in non_divergent_annotations:
    if annotation["id"] not in annotations_map:
        annotations_map[annotation["id"]] = []
    result = {"id": annotation["id"], "start": None, "end": None, "text": None, "label": None}
    for key, value in annotation.items():
        if "text." in key and result["text"] is None:
            result["text"] = value
        elif "start." in key and result["start"] is None:
            result["start"] = value
        elif "end." in key and result["end"] is None:
            result["end"] = value
        elif "label." in key and result["label"] is None:
            result["label"] = value
    annotations_map[annotation["id"]].append(result)
for annotation in divergent_annotations:
    if annotation["id"] not in annotations_map:
        annotations_map[annotation["id"]] = []
    result = {"id": annotation["id"], "start": None, "end": None, "text": None, "label": None}
    for key, value in annotation.items():
        if "text." in key and result["text"] is None:
            result["text"] = value
        elif "start." in key and result["start"] is None:
            result["start"] = value
        elif "end." in key and result["end"] is None:
            result["end"] = value
        elif "final_label" == key and result["label"] is None:
            result["label"] = value
    if result["label"] is not None:
        annotations_map[annotation["id"]].append(result)

for annotations in annotations_map.values():
    annotations.sort(key=lambda a: a["start"])

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

with open("annotations.html", "w") as out_f:
    print("<!DOCTYPE html>", file=out_f)
    print("<html>", file=out_f)
    print("<head>", file=out_f)
    print("  <title>Shared annotations</title>", file=out_f)
    print("""  <script>
    function mouseEnter(ev) {
      for(const span of document.querySelectorAll("#entry-" + ev.target.getAttribute("data-id") + " p span")) {
        const idx = Number.parseInt(span.getAttribute("data-idx"));
        if (idx >= Number.parseInt(ev.target.getAttribute("data-start")) && idx <= Number.parseInt(ev.target.getAttribute("data-end"))) {
          span.classList.add("highlight");
        }
      }
    }

    function mouseLeave(ev) {
      for(const span of document.querySelectorAll("#entry-" + ev.target.getAttribute("data-id") + " span.highlight")) {
        span.classList.remove("highlight");
      }
    }

    document.addEventListener("DOMContentLoaded", () => {
      for (const span of document.querySelectorAll("li span")) {
        span.addEventListener("mouseenter", mouseEnter);
        span.addEventListener("mouseleave", mouseLeave);
      }
    });
  </script>""", file=out_f)
    print("""  <style>
    .highlight {
      background: #ffff00;
    }
  </style>""", file=out_f)
    print("</head>", file=out_f)
    print("<body>", file=out_f)
    print("  <h1>Shared annotations</h1>", file=out_f)
    for entry in data:
        print(f'  <section id="entry-{entry["id"]}">', file=out_f)
        print(f"    <h2>{entry['id']}</h2>", file=out_f)
        out_f.write("    <p>")
        for idx, char in enumerate(entry["data"]["request"]):
            out_f.write(f'<span data-idx="{idx + 1}">{char}</span>')
        print("    </p>", file=out_f)
        if entry["id"] in annotations_map:
            print("    <ol>", file=out_f)
            for annotation in annotations_map[entry["id"]]:
                print(f'    <li><span data-id="{annotation['id']}" data-start="{annotation['start']}" data-end="{annotation['end']}">{annotation["label"]}: {annotation["text"]}</span></li>', file=out_f)
            print("    </ol>", file=out_f)
        print("  </section>", file=out_f)
    print("</body>", file=out_f)
    print("</html>", file=out_f)
