"""Regression tests for generated audio helpers."""

from __future__ import annotations

import unittest

from game.audio import AudioManager, _generate_tone_bytes
from game.settings import GameSettings


class AudioTests(unittest.TestCase):
    def test_unloaded_audio_manager_is_safe_to_use(self) -> None:
        manager = AudioManager()

        manager.play("shot")
        manager.step(0.25)
        manager.set_sfx_volume(2.0)
        manager.set_muted(True)

        self.assertEqual(manager.sfx_volume, 1.0)
        self.assertTrue(manager.muted)

    def test_tone_generation_returns_sample_bytes(self) -> None:
        data = _generate_tone_bytes(440.0, 0.02, 0.25)

        self.assertGreater(len(data), 0)


class GameSettingsTests(unittest.TestCase):
    def test_settings_clamp_volume_and_mute(self) -> None:
        settings = GameSettings()

        settings.adjust_sfx_volume(1.0)
        self.assertEqual(settings.sfx_volume, 1.0)

        settings.adjust_sfx_volume(-2.0)
        self.assertEqual(settings.sfx_volume, 0.0)

        settings.toggle_muted()
        self.assertEqual(settings.effective_sfx_volume(), 0.0)


if __name__ == "__main__":
    unittest.main()
