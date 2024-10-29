"""Correlation analysis."""

import json
import os

import numpy
from scipy.stats import kendalltau, pearsonr, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score

from llm_complex_leisure_search.constants import DATA_SETS


class BinaryEqualSplitter:
    """A splitter generating equally weighted splits for binary classification data."""

    def __init__(self, n_splits=2, test="all"):
        """Initialise the new splitter."""
        self.n_splits = n_splits
        self.test = test

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
            expanded_train = train[expanded_train_idx]
            if self.test == "positive":
                test_subset = test[numpy.where(classes[test] == 1)[0]]
                yield expanded_train, test_subset
            elif self.test == "negative":
                test_subset = test[numpy.where(classes[test] == 0)[0]]
                yield expanded_train, test_subset
            else:
                yield expanded_train, test

    def get_n_splits(self, data, classes, groups=None):  # noqa: ARG002
        """Return the number of splits."""
        return self.n_splits


def correlate_correct(domain: str, llm: str) -> dict:
    """Calculate logistics regressions for confidence and rank to success."""
    solved = []
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"solved_{data_set}.json")) as in_f:
            solved = solved + json.load(in_f)
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    confidence = [[], []]
    rank = [[], []]
    combined = [[], []]
    for task in solved:
        for solution in solutions:
            if task["thread_id"] == solution["thread_id"]:
                for result_list in solution["results"]:
                    for idx, entry in enumerate(result_list):
                        if "normalised_confidence" in entry:
                            confidence[0].append([entry["normalised_confidence"]])
                            rank[0].append([idx])
                            combined[0].append([entry["normalised_confidence"], idx])
                            if task["title"] == entry["title"]:
                                confidence[1].append(True)
                                rank[1].append(True)
                                combined[1].append(True)
                            else:
                                confidence[1].append(False)
                                rank[1].append(False)
                                combined[1].append(False)

    splitter = BinaryEqualSplitter(n_splits=20)
    splitter_positive = BinaryEqualSplitter(n_splits=20, test="positive")
    splitter_negative = BinaryEqualSplitter(n_splits=20, test="negative")
    lr = LogisticRegression()
    result = {}

    data = numpy.array(confidence[0])
    classes = numpy.array(confidence[1])
    scores = cross_val_score(lr, data, classes, cv=splitter)
    result["lr.confidence.avg"] = numpy.average(scores)
    result["lr.confidence.stdev"] = numpy.std(scores)
    scores = cross_val_score(lr, data, classes, cv=splitter_positive)
    result["lr.confidence.pos.avg"] = numpy.average(scores)
    result["lr.confidence.pos.stdev"] = numpy.std(scores)
    scores = cross_val_score(lr, data, classes, cv=splitter_negative)
    result["lr.confidence.neg.avg"] = numpy.average(scores)
    result["lr.confidence.neg.stdev"] = numpy.std(scores)

    data = numpy.array(rank[0])
    classes = numpy.array(rank[1])
    scores = cross_val_score(lr, data, classes, cv=splitter)
    result["lr.rank.avg"] = numpy.average(scores)
    result["lr.rank.stdev"] = numpy.std(scores)
    scores = cross_val_score(lr, data, classes, cv=splitter_positive)
    result["lr.rank.pos.avg"] = numpy.average(scores)
    result["lr.rank.pos.stdev"] = numpy.std(scores)
    scores = cross_val_score(lr, data, classes, cv=splitter_negative)
    result["lr.rank.neg.avg"] = numpy.average(scores)
    result["lr.rank.neg.stdev"] = numpy.std(scores)

    data = numpy.array(combined[0])
    classes = numpy.array(combined[1])
    scores = cross_val_score(lr, data, classes, cv=splitter)
    result["lr.combined.avg"] = numpy.average(scores)
    result["lr.combined.stdev"] = numpy.std(scores)
    scores = cross_val_score(lr, data, classes, cv=splitter_positive)
    result["lr.combined.pos.avg"] = numpy.average(scores)
    result["lr.combined.pos.stdev"] = numpy.std(scores)
    scores = cross_val_score(lr, data, classes, cv=splitter_negative)
    result["lr.combined.neg.avg"] = numpy.average(scores)
    result["lr.combined.neg.stdev"] = numpy.std(scores)

    return result


def correlate_confidence_rank(domain: str, llm: str) -> dict:
    """Calculate correlation between confidence and rank."""
    solutions = []
    for data_set in DATA_SETS:
        with open(os.path.join("data", domain, f"{llm}_{data_set}.json")) as in_f:
            solutions = solutions + json.load(in_f)
    confidences = []
    ranks = []
    for solution in solutions:
        for result_list in solution["results"]:
            for idx, result in enumerate(result_list):
                if "normalised_confidence" in result:
                    confidences.append(result["normalised_confidence"])
                    ranks.append(idx)
    pearson_corr = pearsonr(confidences, ranks)
    spearman_corr = spearmanr(confidences, ranks)
    kendall_corr = kendalltau(confidences, ranks)
    return {
        "pearsonr.statistic": pearson_corr.statistic,
        "pearsonr.pvalue": pearson_corr.pvalue,
        "spearmanr.statistic": spearman_corr.statistic,
        "spearmanr.pvalue": spearman_corr.pvalue,
        "kendalltau.statistic": kendall_corr.statistic,
        "kendalltau.pvalue": kendall_corr.pvalue,
    }
