from pathlib import Path

from harness.verify import validate_scene_spec, verify_scene


def test_scene_spec_validation():
    spec = {
        "scene": {
            "id": "scene_001",
            "objective": {"text": "Understand the structural equation."},
            "content": [
                {"type": "equation", "id": "eq_001"},
                {"type": "caption", "id": "claim_002"},
            ],
            "actions": [{"show": "eq_001"}, {"explain": "claim_002"}],
        }
    }
    assert validate_scene_spec(spec) is True


def test_verify_scene_passes():
    root = Path(__file__).resolve().parents[1]
    assert verify_scene(root / "lesson" / "scene_001.yaml") is True
