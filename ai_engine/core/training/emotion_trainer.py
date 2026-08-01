import torch
from torch import nn
from transformers import Trainer


class EmotionTrainer(Trainer):
    """Custom Trainer reserved for future extensions.

    Currently this behaves exactly like Hugging Face's Trainer.
    Training-set metric collection is handled outside of this class.
    """

    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        if self.class_weights is not None:
            loss_fct = nn.CrossEntropyLoss(weight=self.class_weights.to(logits.device))
        else:
            loss_fct = nn.CrossEntropyLoss()

        loss = loss_fct(
            logits.view(-1, model.config.num_labels),
            labels.view(-1),
        )

        if return_outputs:
            return loss, outputs

        return loss