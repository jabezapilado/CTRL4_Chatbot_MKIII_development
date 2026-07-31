

from transformers import Trainer


class EmotionTrainer(Trainer):
    """Custom Trainer for future training-specific extensions.

    This class currently behaves exactly like Hugging Face's Trainer.
    We introduce it now so training-specific metric collection can be
    added without modifying the rest of the training pipeline.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._train_metrics_logged_epochs = set()

    def evaluate(self, *args, **kwargs):
        metrics = super().evaluate(*args, **kwargs)

        prefix = kwargs.get("metric_key_prefix", "eval")

        if (
            prefix == "eval"
            and self.train_dataset is not None
            and self.state.epoch is not None
        ):
            epoch = int(self.state.epoch)

            if epoch not in self._train_metrics_logged_epochs:
                self._train_metrics_logged_epochs.add(epoch)
                super().evaluate(
                    eval_dataset=self.train_dataset,
                    metric_key_prefix="train",
                )

        return metrics