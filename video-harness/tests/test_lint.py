from pathlib import Path

import pytest

from harness.lint import lint_scene


def test_direct_mathtex_rejected(tmp_path):
    bad = tmp_path / "bad_math_scene.py"
    bad.write_text(
        "from manim import *\n"
        "class Bad(Scene):\n"
        "    def construct(self):\n"
        "        eq = MathTex(r'x+y=z')\n",
        encoding="utf-8",
    )
    issues = lint_scene(bad)
    assert any("MathTex" in issue for issue in issues)


def test_direct_text_rejected(tmp_path):
    bad = tmp_path / "bad_text_scene.py"
    bad.write_text(
        "from manim import *\n"
        "class Bad(Scene):\n"
        "    def construct(self):\n"
        "        txt = Text('hello')\n",
        encoding="utf-8",
    )
    issues = lint_scene(bad)
    assert any("Text" in issue for issue in issues)
