from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_RENDER_CALLS = {"MathTex", "Tex", "Text", "MarkupText", "Paragraph"}


def lint_scene(path: str | Path) -> list[str]:
    source_path = Path(path)
    source_text = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source_text, filename=str(source_path))

    issues: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = getattr(node.func, "id", None)
        if call_name in FORBIDDEN_RENDER_CALLS:
            issues.append(
                f"REJECT\nForbidden direct rendering call:\n{call_name}\nFile:\n{source_path.name}\nLine:\n{node.lineno}"
            )
    return issues


def check_scene_lint(path: str | Path) -> bool:
    issues = lint_scene(path)
    if issues:
        raise ValueError("\n\n".join(issues))
    return True
