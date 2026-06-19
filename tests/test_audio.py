"""Regression tests for generated audio helpers."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from game.audio import SOUND_SPECS, AudioManager, _generate_tone_bytes
from game.settings import GameSettings, InputBindings, load_settings, save_settings


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

    def test_victory_sound_is_registered(self) -> None:
        self.assertIn("victory", SOUND_SPECS)


class GameSettingsTests(unittest.TestCase):
    def test_settings_clamp_volume_and_mute(self) -> None:
        settings = GameSettings()

        settings.adjust_sfx_volume(1.0)
        self.assertEqual(settings.sfx_volume, 1.0)

        settings.adjust_sfx_volume(-2.0)
        self.assertEqual(settings.sfx_volume, 0.0)

        settings.toggle_muted()
        self.assertEqual(settings.effective_sfx_volume(), 0.0)

    def test_settings_round_trip_to_json(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "settings.json"
            settings = GameSettings(
                sfx_volume=0.35,
                muted=True,
                bindings=InputBindings(move_left="j", move_right="l", fire="k"),
                tutorial_seen=True,
            )

            self.assertTrue(save_settings(settings, path))
            loaded = load_settings(path)

            self.assertEqual(loaded.sfx_volume, 0.35)
            self.assertTrue(loaded.muted)
            self.assertEqual(loaded.bindings.move_left, "j")
            self.assertEqual(loaded.bindings.move_right, "l")
            self.assertEqual(loaded.bindings.fire, "k")
            self.assertTrue(loaded.tutorial_seen)

    def test_settings_load_defaults_for_missing_or_corrupt_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.json"
            corrupt_path = Path(temp_dir) / "corrupt.json"
            corrupt_path.write_text("{not valid json", encoding="utf-8")

            self.assertEqual(load_settings(missing_path).sfx_volume, 0.8)
            self.assertEqual(load_settings(corrupt_path).bindings.move_left, "a")


if __name__ == "__main__":
    unittest.main()
