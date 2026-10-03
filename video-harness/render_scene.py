import os
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
env = os.environ.copy()
env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
subprocess.run([
    r"C:\Users\user\AppData\Local\Programs\Python\Python314\Scripts\manim.exe",
    str(root / "scenes" / "scene_001.py"),
    "Scene001",
    "-q",
    "l",
    "--format=mp4",
], cwd=str(root), env=env, check=True)
source_dir = root / "media" / "videos" / "scene_001" / "480p15" / "partial_movie_files" / "Scene001"
out_dir = root / "output" / "videos"
out_dir.mkdir(parents=True, exist_ok=True)
mp4_candidates = sorted(source_dir.glob("*.mp4"))
if not mp4_candidates:
    raise FileNotFoundError(f"No MP4 created in {source_dir}")
final_target = out_dir / "scene_001.mp4"
shutil.copy2(mp4_candidates[-1], final_target)
print(f"Rendered scene to {final_target}")
