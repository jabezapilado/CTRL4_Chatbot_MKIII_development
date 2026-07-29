"""
Evaluation Metrics

Computes evaluation metrics during model training.

Author: CTRL4 Chatbot MK2
"""

import evaluate
import numpy as np


accuracy = evaluate.load("accuracy")
precision = evaluate.load("precision")
recall = evaluate.load("recall")
f1 = evaluate.load("f1")


def compute_metrics(eval_pred):

    logits, labels = eval_pred

    predictions = np.argmax(
        logits,
        axis=-1
    )

    return {

        "accuracy": accuracy.compute(
            predictions=predictions,
            references=labels
        )["accuracy"],

        "precision": precision.compute(
            predictions=predictions,
            references=labels,
            average="weighted"
        )["precision"],

        "recall": recall.compute(
            predictions=predictions,
            references=labels,
            average="weighted"
        )["recall"],

        "f1": f1.compute(
            predictions=predictions,
            references=labels,
            average="weighted"
        )["f1"]

    }