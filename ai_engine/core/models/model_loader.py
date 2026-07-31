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
    "english": MODELS_DIR / "english" / "latest",
    "filipino": MODELS_DIR / "filipino" / "latest",
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
    
    if language not in MODEL_PATHS:
        raise ValueError(
            f"Unsupported language '{language}'. Supported languages: {', '.join(MODEL_PATHS.keys())}."
        )

    model_path = MODEL_PATHS[language]

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model directory not found: {model_path}. Publish or copy a model into this directory first."
        )
    
    return AutoModelForSequenceClassification.from_pretrained(
        str(model_path)
    )