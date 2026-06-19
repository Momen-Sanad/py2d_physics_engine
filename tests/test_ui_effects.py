"""Regression tests for Splashline Showdown UI-layer effects."""

from __future__ import annotations

import os
from random import Random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game import config
from game.effects import WindState
from game.scene import display_to_logical_mouse, logical_viewport
from game.ui import draw_wind_background
from game.ui_effects import UiConfetti, spawn_victory_confetti, step_ui_confetti


def setUpModule() -> None:
    pygame.init()


def tearDownModule() -> None:
    pygame.quit()


class UiEffectsTests(unittest.TestCase):
    def test_confetti_moves_without_gameplay_step(self) -> None:
        confetti = UiConfetti()
        spawn_victory_confetti(confetti, Random(4), count=8)
        before = [(particle.position.x, particle.position.y) for particle in confetti.particles]

        step_ui_confetti(confetti, 0.25)

        after = [(particle.position.x, particle.position.y) for particle in confetti.particles]
        self.assertNotEqual(before, after)
        self.assertEqual(len(confetti.colors), len(confetti.particles))

    def test_fullscreen_mouse_maps_to_logical_canvas(self) -> None:
        viewport = logical_viewport((1920, 1080))

        self.assertEqual(viewport, (0, 0, 1920, 1080))
        self.assertEqual(display_to_logical_mouse((960, 540), viewport), (550, 360))
        self.assertEqual(display_to_logical_mouse((0, 0), viewport), (0, 0))
        self.assertEqual(display_to_logical_mouse((1919, 1079), viewport), (1099, 719))

    def test_wind_background_renders_directional_waves(self) -> None:
        surface = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

        draw_wind_background(surface, WindState(current_force_x=32.0, timer=0.5))
        draw_wind_background(surface, WindState(current_force_x=-32.0, timer=0.5))


if __name__ == "__main__":
    unittest.main()
