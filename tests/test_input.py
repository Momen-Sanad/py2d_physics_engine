"""Regression tests for Splashline Showdown input mapping."""

from __future__ import annotations

import unittest

import pygame

from game.input import read_input
from game.settings import GameSettings, InputBindings


def setUpModule() -> None:
    pygame.init()


def tearDownModule() -> None:
    pygame.quit()


class FakeKeys(dict):
    """Small stand-in for pygame's key state sequence."""

    def __getitem__(self, key: int) -> bool:
        return bool(self.get(key, False))


class InputTests(unittest.TestCase):
    def test_remapped_move_keys_drive_gameplay_input(self) -> None:
        keys = FakeKeys({pygame.key.key_code("j"): True})

        input_state = read_input(
            [],
            keys,
            (420, 260),
            InputBindings(move_left="j", move_right="l", fire="k"),
        )

        self.assertEqual(input_state.move_axis, -1.0)

    def test_old_default_key_does_not_move_after_remap(self) -> None:
        keys = FakeKeys({pygame.key.key_code("a"): True})

        input_state = read_input(
            [],
            keys,
            (420, 260),
            InputBindings(move_left="j", move_right="l", fire="k"),
        )

        self.assertEqual(input_state.move_axis, 0.0)

    def test_keyboard_fire_binding_triggers_fire_once(self) -> None:
        fire_key = pygame.key.key_code("k")
        event = pygame.event.Event(pygame.KEYDOWN, key=fire_key)

        input_state = read_input(
            [event],
            FakeKeys(),
            (420, 260),
            InputBindings(move_left="j", move_right="l", fire="k"),
        )

        self.assertTrue(input_state.fire_pressed)

    def test_reset_bindings_restores_defaults(self) -> None:
        settings = GameSettings(bindings=InputBindings(move_left="j", move_right="l", fire="k"))

        settings.reset_bindings()

        self.assertEqual(settings.bindings.move_left, "a")
        self.assertEqual(settings.bindings.move_right, "d")
        self.assertEqual(settings.bindings.fire, "f")


if __name__ == "__main__":
    unittest.main()
