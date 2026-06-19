"""Regression tests for Splashline Showdown tutorial overlays."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game import config
from game.scene import TUTORIAL_PAGES, tutorial_menu_items
from game.screens import MenuAction
from game.ui import draw_tutorial_overlay


def setUpModule() -> None:
    pygame.init()


def tearDownModule() -> None:
    pygame.quit()


class TutorialTests(unittest.TestCase):
    def test_tutorial_menu_items_include_navigation_and_practice(self) -> None:
        first_page_actions = [item.action for item in tutorial_menu_items(0)]
        second_page_actions = [item.action for item in tutorial_menu_items(1)]

        self.assertIn(MenuAction.TUTORIAL_NEXT, first_page_actions)
        self.assertNotIn(MenuAction.TUTORIAL_PREVIOUS, first_page_actions)
        self.assertIn(MenuAction.TUTORIAL_PREVIOUS, second_page_actions)
        self.assertIn(MenuAction.START_PRACTICE, first_page_actions)

    def test_tutorial_overlay_renders_each_page(self) -> None:
        surface = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        fonts = {
            "title": pygame.font.Font(None, 48),
            "body": pygame.font.Font(None, 28),
            "small": pygame.font.Font(None, 23),
        }

        for page_index, (title, lines) in enumerate(TUTORIAL_PAGES):
            draw_tutorial_overlay(
                surface,
                fonts,
                title,
                lines,
                page_index,
                len(TUTORIAL_PAGES),
                tutorial_menu_items(page_index),
                0,
            )


if __name__ == "__main__":
    unittest.main()
