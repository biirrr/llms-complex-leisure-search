"""Correlation analysis."""

import json
import os

import numpy
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score

from llm_complex_leisure_search.constants import DATA_SETS


class BinaryEqualSplitter:
    """A splitter generating equally weighted splits for binary classification data."""

    def __init__(self, n_splits=2):
        """Initialise the new splitter."""
        self.n_splits = n_splits

    def split(self, data, classes, groups=None):  # noqa: ARG002
        """Generate splits."""
        sksplitter = StratifiedKFold(n_splits=self.n_splits)
        for train, test in sksplitter.split(data, classes):
            negative_idx = numpy.where(classes[train] == 0)[0]
            positive_idx = numpy.where(classes[train] == 1)[0]
            if negative_idx.shape[0] > positive_idx.shape[0]:
                expand_idx = numpy.random.choice(positive_idx, size=negative_idx.shape[0], replace=True)
                expanded_train_idx = numpy.append(expand_idx, negative_idx)
            elif negative_idx.shape[0] < positive_idx.shape[0]:
                expand_idx = numpy.random.choice(negative_idx, size=positive_idx.shape[0], replace=True)
                expanded_train_idx = numpy.append(expand_idx, positive_idx)
            train_subset = train[expanded_train_idx]
            yield train_subset, test

    def get_n_splits(self, data, classes, groups=None):  # noqa: ARG002
        """Return the number of splits."""
        return self.n_splits


def correlate_correct(domain: str, llm: str) -> dict:
    """Calculate logistics regressions."""
    solved = []
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + json.load(in_f)
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    confidence = [[], []]
    rank = [[], []]
    for task in solved:
        for solution in solutions:
            if task["thread_id"] == solution["thread_id"]:
                for result_list in solution["results"]:
                    for idx, entry in enumerate(result_list):
                        if "normalised_confidence" in entry:
                            confidence[0].append([entry["normalised_confidence"]])
                            rank[0].append([idx])
                            if task["title"] == entry["title"]:
                                confidence[1].append(True)
                                rank[1].append(True)
                            else:
                                confidence[1].append(False)
                                rank[1].append(False)

    splitter = BinaryEqualSplitter(n_splits=20)
    lr = LogisticRegression()
    result = {}

    scores = numpy.array(confidence[0])
    classes = numpy.array(confidence[1])
    scores = cross_val_score(lr, scores, classes, cv=splitter)
    result["lr.confidence.avg"] = numpy.average(scores)
    result["lr.confidence.stdev"] = numpy.std(scores)

    scores = numpy.array(rank[0])
    classes = numpy.array(rank[1])
    scores = cross_val_score(lr, scores, classes, cv=splitter)
    result["lr.rank.avg"] = numpy.average(scores)
    result["lr.rank.stdev"] = numpy.std(scores)
    return result
