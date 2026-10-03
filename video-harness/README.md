# Video Harness PoC

This project is a minimal, local-first pipeline for turning a small mathematics source document into a validated Manim scene without rewriting the original source equation.

## 1. Check the Python environment

Open PowerShell and run:

```powershell
python --version
python -m pip --version
```

The project expects Python 3.10+ and a working Manim Community Edition installation.

## 2. Create a virtual environment

```powershell
cd C:\path\to\video-harness
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## 4. Confirm Manim and TeX tooling

```powershell
manim --version
tex --version
```

This project expects Manim Community Edition 0.21.0 and a working LaTeX toolchain such as MiKTeX.

## 5. Generate the equation registry

```powershell
python -m harness.parse
```

This reads the source markdown and writes the equation registry.

## 6. Validate the lesson

```powershell
python -c "import yaml; from harness.schema import validate_scene_spec; data = yaml.safe_load(open('lesson/scene_001.yaml', encoding='utf-8')); validate_scene_spec(data); print('OK')"
```

## 7. Lint the scene

```powershell
python -c "from harness.lint import lint_scene; issues = lint_scene('scenes/scene_001.py'); print(issues if issues else 'OK')"
```

## 8. Render a low-quality preview

```powershell
python -m manim scenes/scene_001.py Scene001 -q l --format=mp4 -o scene_001.mp4
```

The output video is written to the default Manim output directory, and the project keeps a copy in `output/videos`.

## 9. Verify the audit trail

```powershell
python -c "from harness.verify import verify_scene; print(verify_scene('lesson/scene_001.yaml'))"
```

## 10. Where the MP4 is saved

```powershell
Get-ChildItem .\output\videos
```

## 11. Run the test suite

```powershell
pytest
```

A passing run confirms that the source equation, registry entries, runtime audit, and lint rules all agree.
