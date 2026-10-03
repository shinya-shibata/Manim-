from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, model_validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "equations.yaml"
CLAIMS_PATH = ROOT / "registry" / "claims.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload or {}


def _equation_ids() -> set[str]:
    payload = _load_yaml(REGISTRY_PATH)
    return {entry["id"] for entry in payload.get("equations", [])}


def _claim_ids() -> set[str]:
    payload = _load_yaml(CLAIMS_PATH)
    return {entry["id"] for entry in payload.get("claims", [])}


class Objective(BaseModel):
    text: str


class SceneContent(BaseModel):
    type: Literal["equation", "caption", "definition"]
    id: str

    @model_validator(mode="after")
    def validate_registry_id(self) -> "SceneContent":
        if self.type == "equation":
            if self.id not in _equation_ids():
                raise ValueError(f"Unknown equation ID '{self.id}'")
            payload = _load_yaml(REGISTRY_PATH)
            for entry in payload.get("equations", []):
                if entry.get("id") == self.id and entry.get("status") == "proposed":
                    raise ValueError(f"Equation '{self.id}' is proposed and cannot be rendered.")
        else:
            if self.id not in _claim_ids():
                raise ValueError(f"Unknown claim ID '{self.id}'")
        return self


class SceneAction(BaseModel):
    show: str | None = None
    explain: str | None = None

    @model_validator(mode="after")
    def validate_target_ids(self) -> "SceneAction":
        if self.show is not None and self.show not in _equation_ids():
            raise ValueError(f"Unknown equation ID '{self.show}' in scene action.")
        if self.explain is not None and self.explain not in _claim_ids():
            raise ValueError(f"Unknown claim ID '{self.explain}' in scene action.")
        return self


class SceneSpec(BaseModel):
    id: str
    objective: Objective
    content: list[SceneContent]
    actions: list[SceneAction]


class SceneDocument(BaseModel):
    scene: SceneSpec


def validate_scene_spec(spec: dict[str, Any] | str | Path) -> bool:
    if isinstance(spec, (str, Path)):
        spec_path = Path(spec)
        raw_data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    else:
        raw_data = spec

    SceneDocument.model_validate(raw_data)
    return True
