from transformers import TrainerCallback


class TrainingMetricsCallback(TrainerCallback):
    """Evaluates the training dataset at the end of each epoch so
    training metrics (accuracy, precision, recall, F1, loss) are
    recorded alongside validation metrics in the trainer history.
    """

    def on_epoch_end(self, args, state, control, **kwargs):
        trainer = kwargs.get("trainer")

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

        prediction_output = trainer.predict(
            test_dataset=trainer.train_dataset,
            metric_key_prefix="train",
        )

        trainer.log(prediction_output.metrics)

        return control
