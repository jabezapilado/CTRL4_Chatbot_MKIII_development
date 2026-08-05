#!/usr/bin/env python3
"""Verify the protected runtime artifact for the English emotion model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "ai_engine" / "models" / "english" / "latest"
MANIFEST_NAME = "runtime_artifact_manifest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_model_directory(model_dir: Path) -> list[str]:
    """Return safe validation errors for one provisioned model directory."""
    manifest_path = model_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        return [f"Missing artifact manifest: {manifest_path}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        required_files = manifest["required_files"]
    except (OSError, ValueError, KeyError, TypeError):
        return [f"Invalid artifact manifest: {manifest_path}"]

    errors: list[str] = []
    for filename, expected in required_files.items():
        path = model_dir / filename
        if not path.is_file():
            errors.append(f"Missing required model file: {filename}")
            continue

        expected_size = expected.get("size_bytes")
        if expected_size is not None and path.stat().st_size != expected_size:
            errors.append(f"Unexpected size for model file: {filename}")
            continue

        expected_hash = expected.get("sha256")
        if expected_hash and _sha256(path) != expected_hash:
            errors.append(f"Checksum mismatch for model file: {filename}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify CTRL4's provisioned English emotion model artifact."
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help="Directory containing runtime_artifact_manifest.json and model files.",
    )
    arguments = parser.parse_args()
    errors = verify_model_directory(arguments.model_dir)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("English emotion model artifact verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
