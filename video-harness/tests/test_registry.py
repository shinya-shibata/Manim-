from pathlib import Path

import pytest

from harness.api import equation
from harness.verify import verify_runtime_audit


def test_unknown_equation_rejected():
    with pytest.raises(ValueError, match="Unknown equation"):
        equation("eq_unknown", scene_id="scene_001")


def test_proposed_equation_rejected():
    with pytest.raises(ValueError, match="proposed|render"):
        equation("eq_002", scene_id="scene_001")


def test_wrong_latex_rejected():
    runtime = {
        "scene": "scene_001",
        "object": "obj_001",
        "kind": "equation",
        "registry_id": "eq_001",
        "latex": "X = \\theta(\\beta)V",
        "normalized": "X=\\theta(\\beta)V",
        "hash": "deadbeef",
    }
    with pytest.raises(ValueError, match="does not match registry|LaTeX"):
        verify_runtime_audit(runtime)


def test_hash_mismatch_rejected():
    runtime = {
        "scene": "scene_001",
        "object": "obj_001",
        "kind": "equation",
        "registry_id": "eq_001",
        "latex": "X = \\theta(\\beta)U",
        "normalized": "X=\\theta(\\beta)U",
        "hash": "deadbeef",
    }
    with pytest.raises(ValueError, match="hash"):
        verify_runtime_audit(runtime)
