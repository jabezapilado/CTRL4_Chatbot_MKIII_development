import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import precision_recall_fscore_support
from transformers import TrainerCallback


class TrainingMetricsCallback(TrainerCallback):
    """Evaluates the training dataset at the end of each epoch so
    training metrics (accuracy, precision, recall, F1, loss) are
    recorded alongside validation metrics in the trainer history.
    """

    def __init__(self, trainer=None, max_train_eval_samples=4096):
        self.trainer = trainer
        self.max_train_eval_samples = max_train_eval_samples

    def on_epoch_end(self, args, state, control, **kwargs):
        trainer = kwargs.get("trainer") or self.trainer

        if state.epoch is None:
            return control

        completed_epoch = int(round(state.epoch))

        if not hasattr(self, "_logged_epochs"):
            self._logged_epochs = set()

        if completed_epoch in self._logged_epochs:
            return control

        if trainer is None:
            return control

        if trainer.train_dataset is None:
            return control

        if abs(state.epoch - completed_epoch) > 1e-6:
            return control

        self._logged_epochs.add(completed_epoch)

        eval_dataset = trainer.train_dataset
        if self.max_train_eval_samples and len(eval_dataset) > self.max_train_eval_samples:
            eval_dataset = eval_dataset.select(range(self.max_train_eval_samples))

        prediction_output = trainer.predict(
            test_dataset=eval_dataset,
            metric_key_prefix="train",
        )

        logits = prediction_output.predictions
        labels = prediction_output.label_ids

        if logits is None or labels is None:
            return control

        predictions = np.argmax(logits, axis=-1)

        logits_tensor = torch.tensor(logits, dtype=torch.float32)
        labels_tensor = torch.tensor(labels, dtype=torch.long)
        train_loss = float(F.cross_entropy(logits_tensor, labels_tensor).item())

        train_accuracy = float(np.mean(predictions == labels))
        train_precision, train_recall, train_f1, _ = precision_recall_fscore_support(
            labels,
            predictions,
            average="weighted",
            zero_division=0,
        )

        trainer.log(
            {
                "train_accuracy": train_accuracy,
                "train_precision": float(train_precision),
                "train_recall": float(train_recall),
                "train_f1": float(train_f1),
                "train_loss": train_loss,
                "train_eval_samples": len(eval_dataset),
            }
        )

        return control
