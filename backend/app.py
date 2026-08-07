from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the project root importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import create_app


app = create_app()


if __name__ == "__main__":
    # Set CTRL4_HOST=0.0.0.0 only for Tailscale or local-network testing.
    host = os.getenv("CTRL4_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = int(os.getenv("CTRL4_PORT", str(app.config.get("PORT", 5001))))

    app.run(
        host=host,
        port=port,
        debug=app.config.get("DEBUG", True),
        use_reloader=False,
    )
