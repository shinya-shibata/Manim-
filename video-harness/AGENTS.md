# AGENTS.md

## Core rules

1. Do not change the original source equation.
2. Do not ask an LLM to regenerate the equation text.
3. Do not call MathTex, Tex, Text, MarkupText, or Paragraph directly from a scene.
4. Use registry IDs instead of hard-coded math text.
5. Record runtime audit entries every time a registry object is rendered.
6. Do not render proposed equations.
7. Run pytest after every code change.
8. Run lint and schema validation before render.
9. Keep mathematical content separate from pedagogical explanation.
10. Do not hide errors.

## Minimal workflow

- Parse source markdown into registry data.
- Validate the lesson specification.
- Lint the scene.
- Render a low-quality Manim preview.
- Verify the runtime log and registry values.
