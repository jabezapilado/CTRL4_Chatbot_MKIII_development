"""
Configuration Loader

Loads JSON configuration files.

Author: CTRL4 Chatbot MK2
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_DIR = PROJECT_ROOT / "configs"


def load_config(filename: str):

    filepath = CONFIG_DIR / filename

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)