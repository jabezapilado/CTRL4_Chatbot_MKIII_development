"""
Tokenizer Loader

Loads the tokenizer for the emotion recognition models.

Author:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from pathlib import Path

from transformers import AutoTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODELS_DIR = PROJECT_ROOT / "ai_engine" / "models"

TOKENIZER_PATHS = {
    "english": MODELS_DIR / "english" / "v1",
    "filipino": MODELS_DIR / "filipino" / "v1",
}


def load_tokenizer(language: str = "english"):
    """
    Load the tokenizer for the specified language.

    Parameters
    ----------
    language : str
        english or filipino

    Returns
    -------
    AutoTokenizer
    """

    return AutoTokenizer.from_pretrained(
        str(TOKENIZER_PATHS[language])
    )