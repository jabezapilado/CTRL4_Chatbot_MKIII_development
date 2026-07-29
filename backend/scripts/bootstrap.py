from __future__ import annotations

import sys
from pathlib import Path


def setup_paths() -> None:
    """
    Configure Python paths for standalone backend scripts.

    Allows imports such as:

        from server...
        from ai_engine...
    """

    project_root = Path(__file__).resolve().parents[2]
    backend_root = project_root / "backend"

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))