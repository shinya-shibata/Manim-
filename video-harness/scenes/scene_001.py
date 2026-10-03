from manim import FadeIn, Scene, Write

from harness.api import caption, equation


class Scene001(Scene):
    def construct(self):
        eq = equation("eq_001", scene_id="scene_001")
        self.play(Write(eq))

        cap = caption("claim_002", scene_id="scene_001")
        self.play(FadeIn(cap))
