from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "source" / "paper.md"
REGISTRY_PATH = ROOT / "registry" / "equations.yaml"


def normalize_latex(latex: str) -> str:
    """Return a deterministic form that is safe to compare in the registry."""
    return re.sub(r"\s+", "", latex.strip())


def compute_hash(latex: str) -> str:
    normalized = normalize_latex(latex)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_display_equations(markdown_text: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"\$\$(.+?)\$\$", markdown_text, re.DOTALL)
    ]


def parse_markdown(path: str | Path) -> dict[str, Any]:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")

    headings = [heading.strip() for heading in re.findall(r"^#+\s+(.*)$", text, re.MULTILINE)]
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip() and not paragraph.strip().startswith("#") and "$$" not in paragraph
    ]

    equations = []
    for index, latex in enumerate(extract_display_equations(text), start=1):
        eq_id = f"eq_{index:03d}"
        equations.append(
            {
                "id": eq_id,
                "status": "source",
                "latex": latex,
                "hash": compute_hash(latex),
                "source": {
                    "file": str(source_path.relative_to(ROOT).as_posix()),
                },
            }
        )

    return {
        "headings": headings,
        "paragraphs": paragraphs,
        "equations": equations,
    }


def generate_registry(source_path: str | Path = SOURCE_PATH, output_path: str | Path = REGISTRY_PATH) -> dict[str, Any]:
    source_file = Path(source_path)
    registry_path = Path(output_path)
    data = parse_markdown(source_file)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        yaml.safe_dump({"equations": data["equations"]}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return {"equations": data["equations"]}


if __name__ == "__main__":
    generate_registry()
    print("Generated equation registry.")
