from transformers import Trainer


class EmotionTrainer(Trainer):
    """Custom Trainer reserved for future extensions.

    Currently this behaves exactly like Hugging Face's Trainer.
    Training-set metric collection is handled outside of this class.
    """

    pass