"""Regression tests for Splashline Showdown menu flow."""

from __future__ import annotations

import unittest

from game.scene import menu_items_for
from game.screens import MenuAction, ScreenMode


class MenuFlowTests(unittest.TestCase):
    def test_pause_menu_can_return_to_mode_select(self) -> None:
        actions = [item.action for item in menu_items_for(ScreenMode.PAUSED)]

        self.assertIn(MenuAction.MAIN_MENU, actions)


if __name__ == "__main__":
    unittest.main()
