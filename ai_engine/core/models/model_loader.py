"""
Model Loader

Loads the emotion recognition models.

Author:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from pathlib import Path

from transformers import AutoModelForSequenceClassification


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODELS_DIR = PROJECT_ROOT / "ai_engine" / "models"

MODEL_PATHS = {
    "english": MODELS_DIR / "english" / "v1",
    "filipino": MODELS_DIR / "filipino" / "v1",
}


def load_model(language: str = "english"):
    """
    Load an emotion recognition model.

    Parameters
    ----------
    language : str
        english or filipino

    Returns
    -------
    AutoModelForSequenceClassification
    """
    
    return AutoModelForSequenceClassification.from_pretrained(
        str(MODEL_PATHS[language])
    )