from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from manim import MathTex, Tex

from harness.parse import normalize_latex

ROOT = Path(__file__).resolve().parents[1]
EQUATIONS_PATH = ROOT / "registry" / "equations.yaml"
CLAIMS_PATH = ROOT / "registry" / "claims.yaml"
RUNTIME_LOG_PATH = ROOT / "audit" / "runtime_log.json"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload or {}


def _hash_latex(latex: str) -> str:
    return hashlib.sha256(normalize_latex(latex).encode("utf-8")).hexdigest()


def _write_runtime_log(entry: dict[str, Any]) -> None:
    RUNTIME_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]]
    if RUNTIME_LOG_PATH.exists():
        try:
            payload = json.loads(RUNTIME_LOG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = []
        if isinstance(payload, dict) and "entries" in payload:
            entries = payload["entries"]
        elif isinstance(payload, list):
            entries = payload
        else:
            entries = []
    else:
        entries = []
    entries.append(entry)
    RUNTIME_LOG_PATH.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _registry_equations() -> list[dict[str, Any]]:
    return _load_yaml(EQUATIONS_PATH).get("equations", [])


def _registry_claims() -> list[dict[str, Any]]:
    return _load_yaml(CLAIMS_PATH).get("claims", [])


def load_equation(eq_id: str) -> dict[str, Any]:
    for item in _registry_equations():
        if item.get("id") == eq_id:
            return item
    raise ValueError(f"Unknown equation: {eq_id}")


def load_claim(claim_id: str) -> dict[str, Any]:
    for item in _registry_claims():
        if item.get("id") == claim_id:
            return item
    raise ValueError(f"Unknown claim: {claim_id}")


def equation(eq_id: str, scene_id: str | None = None):
    record = load_equation(eq_id)
    status = record.get("status")
    if status in {"proposed"}:
        raise ValueError(f"Equation '{eq_id}' is proposed and cannot be rendered.")

    latex = record["latex"]
    normalized = normalize_latex(latex)
    hash_value = _hash_latex(latex)
    object_name = f"obj_{eq_id}"
    result = MathTex(latex)
    _write_runtime_log(
        {
            "scene": scene_id or "unknown",
            "object": object_name,
            "kind": "equation",
            "registry_id": eq_id,
            "latex": latex,
            "normalized": normalized,
            "hash": hash_value,
        }
    )
    return result


def caption(claim_id: str, scene_id: str | None = None):
    record = load_claim(claim_id)
    text = record["text"]
    result = Tex(text)
    _write_runtime_log(
        {
            "scene": scene_id or "unknown",
            "object": f"obj_{claim_id}",
            "kind": "caption",
            "registry_id": claim_id,
            "latex": text,
            "normalized": normalize_latex(text),
            "hash": _hash_latex(text),
        }
    )
    return result


def definition(claim_id: str, scene_id: str | None = None):
    record = load_claim(claim_id)
    text = record["text"]
    result = Tex(text)
    _write_runtime_log(
        {
            "scene": scene_id or "unknown",
            "object": f"obj_{claim_id}",
            "kind": "definition",
            "registry_id": claim_id,
            "latex": text,
            "normalized": normalize_latex(text),
            "hash": _hash_latex(text),
        }
    )
    return result
