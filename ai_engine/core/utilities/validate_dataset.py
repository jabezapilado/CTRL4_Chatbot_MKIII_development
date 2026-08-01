"""Dataset Validator

Validates processed and/or merged Hugging Face datasets before training.

Usage:
python -m ai_engine.core.utilities.validate_dataset --all
python -m ai_engine.core.utilities.validate_dataset --dataset goemotions
python -m ai_engine.core.utilities.validate_dataset --dataset merged_emotion_dataset --scope merged
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from datasets import load_from_disk


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "configs"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MERGED_DIR = PROJECT_ROOT / "data" / "merged"

REQUIRED_FIELDS = [
    "id",
    "text",
    "original_emotion",
    "emotion",
    "sentiment",
    "is_negative",
    "source",
]


def load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_dataset_paths(scope: str, dataset_name: str | None, include_all: bool) -> list[Path]:
    paths: list[Path] = []

    if scope in {"processed", "both"}:
        if include_all:
            if PROCESSED_DIR.exists():
                paths.extend(sorted([p for p in PROCESSED_DIR.iterdir() if p.is_dir()]))
        elif dataset_name:
            candidate = PROCESSED_DIR / dataset_name
            if candidate.exists():
                paths.append(candidate)

    if scope in {"merged", "both"}:
        if include_all:
            if MERGED_DIR.exists():
                paths.extend(sorted([p for p in MERGED_DIR.iterdir() if p.is_dir()]))
        elif dataset_name:
            candidate = MERGED_DIR / dataset_name
            if candidate.exists():
                paths.append(candidate)

    # De-duplicate while preserving order.
    unique: list[Path] = []
    seen = set()
    for path in paths:
        key = str(path.resolve())
        if key not in seen:
            unique.append(path)
            seen.add(key)
    return unique


def validate_row(
    row: dict[str, Any],
    split_name: str,
    row_index: int,
    allowed_emotions: set[str],
    allowed_sentiments: set[str],
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in row:
            errors.append(f"[{split_name}:{row_index}] missing field: {field}")

    if errors:
        return errors

    text = row.get("text")
    if not isinstance(text, str) or not text.strip():
        errors.append(f"[{split_name}:{row_index}] invalid text (empty or non-string)")

    emotion = row.get("emotion")
    if not isinstance(emotion, str) or emotion not in allowed_emotions:
        errors.append(f"[{split_name}:{row_index}] invalid emotion: {emotion}")

    sentiment = row.get("sentiment")
    if not isinstance(sentiment, str) or sentiment not in allowed_sentiments:
        errors.append(f"[{split_name}:{row_index}] invalid sentiment: {sentiment}")

    is_negative = row.get("is_negative")
    if not isinstance(is_negative, bool):
        errors.append(f"[{split_name}:{row_index}] invalid is_negative type: {type(is_negative).__name__}")

    source = row.get("source")
    if not isinstance(source, str) or not source.strip():
        errors.append(f"[{split_name}:{row_index}] invalid source (empty or non-string)")

    return errors


def validate_dataset(path: Path, allowed_emotions: set[str], allowed_sentiments: set[str]) -> tuple[bool, dict[str, Any]]:
    ds = load_from_disk(path)

    expected_splits = {"train", "validation", "test"}
    actual_splits = set(ds.keys())
    split_errors = sorted(list(expected_splits - actual_splits))

    report: dict[str, Any] = {
        "dataset": path.name,
        "path": str(path),
        "splits": {},
        "errors": [],
        "warnings": [],
    }

    if split_errors:
        report["errors"].append(f"missing splits: {', '.join(split_errors)}")

    # Duplicate text checks:
    # 1) per split
    # 2) cross-split leakage
    split_text_sets: dict[str, set[str]] = {}

    for split_name in sorted(actual_splits):
        split_ds = ds[split_name]
        split_report = {
            "rows": len(split_ds),
            "invalid_rows": 0,
            "duplicate_text_rows": 0,
            "example_errors": [],
        }

        seen_text: set[str] = set()
        normalized_texts: set[str] = set()

        for idx, row in enumerate(split_ds):
            errs = validate_row(row, split_name, idx, allowed_emotions, allowed_sentiments)
            if errs:
                split_report["invalid_rows"] += 1
                if len(split_report["example_errors"]) < 10:
                    split_report["example_errors"].extend(errs[:2])

            text = row.get("text")
            if isinstance(text, str):
                normalized = text.strip().lower()
                if normalized in seen_text:
                    split_report["duplicate_text_rows"] += 1
                else:
                    seen_text.add(normalized)
                normalized_texts.add(normalized)

        split_text_sets[split_name] = normalized_texts
        report["splits"][split_name] = split_report

    # Cross-split leakage warnings.
    if {"train", "validation"}.issubset(split_text_sets):
        overlap = split_text_sets["train"].intersection(split_text_sets["validation"])
        if overlap:
            report["warnings"].append(
                f"train/validation duplicate texts: {len(overlap)}"
            )
    if {"train", "test"}.issubset(split_text_sets):
        overlap = split_text_sets["train"].intersection(split_text_sets["test"])
        if overlap:
            report["warnings"].append(
                f"train/test duplicate texts: {len(overlap)}"
            )
    if {"validation", "test"}.issubset(split_text_sets):
        overlap = split_text_sets["validation"].intersection(split_text_sets["test"])
        if overlap:
            report["warnings"].append(
                f"validation/test duplicate texts: {len(overlap)}"
            )

    has_invalid_rows = any(
        split_info["invalid_rows"] > 0 for split_info in report["splits"].values()
    )
    is_valid = not report["errors"] and not has_invalid_rows
    return is_valid, report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate processed/merged datasets before retraining.")
    parser.add_argument("--dataset", type=str, help="Dataset folder name (e.g. goemotions or merged_emotion_dataset).")
    parser.add_argument("--all", action="store_true", help="Validate all datasets in selected scope.")
    parser.add_argument(
        "--scope",
        choices=["processed", "merged", "both"],
        default="both",
        help="Where to look for datasets.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code if warnings exist.",
    )

    args = parser.parse_args()

    if not args.all and not args.dataset:
        parser.error("Choose either --all or --dataset <name>.")

    label_encoder = load_json(CONFIG_DIR / "label_encoder.json")
    sentiment_mapping = load_json(CONFIG_DIR / "sentiment_mapping.json")

    allowed_emotions = set(label_encoder.keys())
    allowed_sentiments = set(value["sentiment"] for value in sentiment_mapping.values())

    targets = collect_dataset_paths(args.scope, args.dataset, args.all)
    if not targets:
        print("No datasets found for the selected scope/options.")
        raise SystemExit(1)

    any_invalid = False
    any_warnings = False

    print("=" * 72)
    print("DATASET VALIDATION REPORT")
    print("=" * 72)

    for path in targets:
        valid, report = validate_dataset(path, allowed_emotions, allowed_sentiments)

        print(f"\nDataset: {report['dataset']}")
        print(f"Path   : {report['path']}")
        print(f"Status : {'VALID' if valid else 'INVALID'}")

        for split_name in sorted(report["splits"].keys()):
            split_info = report["splits"][split_name]
            print(
                f"  - {split_name:<10} rows={split_info['rows']:,} "
                f"invalid={split_info['invalid_rows']:,} "
                f"dup_text={split_info['duplicate_text_rows']:,}"
            )

            for err in split_info["example_errors"][:5]:
                print(f"      example: {err}")

        for err in report["errors"]:
            print(f"  error   : {err}")

        for warn in report["warnings"]:
            any_warnings = True
            print(f"  warning : {warn}")

        if not valid:
            any_invalid = True

    print("\n" + "=" * 72)
    if any_invalid:
        print("RESULT: INVALID DATASET(S) FOUND")
    elif any_warnings:
        print("RESULT: VALID WITH WARNINGS")
    else:
        print("RESULT: ALL DATASETS VALID")
    print("=" * 72)

    if any_invalid or (args.strict and any_warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
