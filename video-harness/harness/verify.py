from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from PIL import Image

from harness.api import RUNTIME_LOG_PATH, _hash_latex, load_equation
from harness.lint import lint_scene
from harness.parse import normalize_latex
from harness.schema import validate_scene_spec

ROOT = Path(__file__).resolve().parents[1]


def _load_runtime_entries() -> list[dict[str, Any]]:
    if not RUNTIME_LOG_PATH.exists():
        return []
    payload = json.loads(RUNTIME_LOG_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get("entries", [])
    return []


def verify_runtime_audit(runtime_entry: dict[str, Any]) -> bool:
    registry_id = runtime_entry.get("registry_id")
    if not registry_id:
        raise ValueError("Runtime audit record is missing a registry_id.")

    registry_entry = load_equation(registry_id)
    expected_latex = registry_entry["latex"]
    actual_latex = runtime_entry.get("latex")
    if actual_latex != expected_latex:
        raise ValueError(
            f"Runtime log LaTeX does not match registry for {registry_id}: expected {expected_latex!r}, got {actual_latex!r}."
        )

    if runtime_entry.get("normalized") != normalize_latex(actual_latex):
        raise ValueError(f"Runtime log normalized value does not match registry for {registry_id}.")

    expected_hash = _hash_latex(actual_latex)
    if runtime_entry.get("hash") != expected_hash:
        raise ValueError(f"Runtime log hash mismatch for {registry_id}: expected {expected_hash!r}.")

    return True


def validate_scene_yaml(scene_path: str | Path) -> bool:
    path = Path(scene_path)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate_scene_spec(payload)
    return True


def validate_visual_bounds(frame_path: str | Path) -> bool:
    path = Path(frame_path)
    if not path.exists():
        return True
    with Image.open(path) as image:
        width, height = image.size
        if width <= 0 or height <= 0:
            raise ValueError(f"Image {path} is invalid or empty.")
    return True


def verify_scene(scene_path: str | Path) -> bool:
    path = Path(scene_path)
    if path.suffix in {".yaml", ".yml"}:
        validate_scene_yaml(path)
        return True

    issues = lint_scene(path)
    if issues:
        raise ValueError("\n\n".join(issues))
    return True


if __name__ == "__main__":
    print(verify_scene(ROOT / "lesson" / "scene_001.yaml"))
