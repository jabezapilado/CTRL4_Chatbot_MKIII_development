

from transformers import TrainerCallback


class TrainingMetricsCallback(TrainerCallback):
    """Evaluates the training dataset at the end of each epoch so
    training metrics (accuracy, precision, recall, F1, loss) are
    recorded alongside validation metrics in the trainer history.
    """

    def on_epoch_end(self, args, state, control, **kwargs):
        trainer = kwargs.get("trainer")

        if trainer is None:
            return control

        if trainer.train_dataset is None:
            return control

        trainer.evaluate(
            eval_dataset=trainer.train_dataset,
            metric_key_prefix="train",
        )

        return control