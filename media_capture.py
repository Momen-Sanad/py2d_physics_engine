# <file>
# <summary>
# Provides screenshot and GIF capture helpers for pygame demo scenes.
# </summary>
# </file>
"""Standalone media capture helpers for demo scenes.

This module intentionally lives outside ``engine/`` because it is a tooling/UI
utility rather than simulation logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# <summary>
# Runtime screenshot and GIF capture controller for pygame scenes.
# </summary>
@dataclass(slots=True)
class CaptureController:
    """Runtime screenshot and GIF capture controller for pygame scenes."""

    demo_name: str
    output_dir: str | Path = "captures"
    gif_fps: int = 20
    message_duration: float = 2.5
    output_path: Path = field(init=False)

    recording: bool = False
    frame_count: int = 0
    _frames: list = field(default_factory=list)
    _capture_accumulator: float = 0.0
    _message: str = ""
    _message_timer: float = 0.0

    # <summary>
    # Finalize dataclass-derived state after initialization.
    # </summary>
    def __post_init__(self) -> None:
        self.output_path = Path(self.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)

    # <summary>
    # Handle capture hotkeys. Returns True when consumed.
    # </summary>
    # <param name="event">pygame event being handled.</param>
    # <param name="surface">pygame surface used for drawing or capture.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def handle_keydown(self, event, surface) -> bool:
        """Handle capture hotkeys. Returns True when consumed."""

        import pygame

        if event.key == pygame.K_TAB:
            self.save_screenshot(surface)
            return True
        if event.key == pygame.K_BACKQUOTE:
            self.toggle_gif_recording(surface)
            return True
        return False

    # <summary>
    # Save a PNG screenshot of the provided surface.
    # </summary>
    # <param name="surface">pygame surface used for drawing or capture.</param>
    def save_screenshot(self, surface) -> None:
        """Save a PNG screenshot of the provided surface."""

        import pygame

        path = self._new_file_path("png")
        pygame.image.save(surface, path)
        self._set_message(f"Screenshot: {path.name}")

    # <summary>
    # Start/stop GIF recording on repeated key presses.
    # </summary>
    # <param name="surface">pygame surface used for drawing or capture.</param>
    def toggle_gif_recording(self, surface) -> None:
        """Start/stop GIF recording on repeated key presses."""

        if not self.recording:
            self.recording = True
            self.frame_count = 0
            self._frames.clear()
            self._capture_accumulator = 0.0
            self._set_message("GIF recording started")
            self._record_frame(surface)
            return

        self.recording = False
        self._set_message(self._save_gif())

    # <summary>
    # Advance capture state and collect frames when recording.
    # </summary>
    # <param name="surface">pygame surface used for drawing or capture.</param>
    # <param name="frame_time">Elapsed frame time in seconds.</param>
    def update(self, surface, frame_time: float) -> None:
        """Advance capture state and collect frames when recording."""

        if self._message_timer > 0.0:
            self._message_timer = max(0.0, self._message_timer - frame_time)
            if self._message_timer == 0.0:
                self._message = ""

        if not self.recording:
            return

        interval = 1.0 / max(1, self.gif_fps)
        self._capture_accumulator += frame_time
        while self._capture_accumulator >= interval:
            self._capture_accumulator -= interval
            self._record_frame(surface)

    # <summary>
    # Return lightweight capture status lines for debug overlays.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def overlay_lines(self) -> list[str]:
        """Return lightweight capture status lines for debug overlays."""

        lines: list[str] = []
        if self.recording:
            lines.append(f"Capture: GIF REC ({self.frame_count} frames) [` stop]")
        if self._message:
            lines.append(self._message)
        if not lines:
            lines.append("Capture: TAB screenshot, ` GIF start/stop")
        return lines

    # <summary>
    # Capture the current surface as a Pillow frame for GIF output.
    # </summary>
    # <param name="surface">pygame surface used for drawing or capture.</param>
    def _record_frame(self, surface) -> None:
        image_module = self._load_pillow_image_module()
        if image_module is None:
            self.recording = False
            self._frames.clear()
            self._set_message("GIF disabled: install Pillow")
            return

        raw_bytes = self._surface_rgb_bytes(surface)
        size = surface.get_size()
        frame = image_module.frombytes("RGB", size, raw_bytes)
        self._frames.append(frame)
        self.frame_count += 1

    # <summary>
    # Encode captured frames into a GIF and reset recording state.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def _save_gif(self) -> str:
        if not self._frames:
            return "GIF canceled: no frames captured"

        image_module = self._load_pillow_image_module()
        if image_module is None:
            self._frames.clear()
            return "GIF save failed: install Pillow"

        path = self._new_file_path("gif")
        duration_ms = int(1000 / max(1, self.gif_fps))

        first_frame = self._frames[0]
        extra_frames = self._frames[1:]
        first_frame.save(
            path,
            save_all=True,
            append_images=extra_frames,
            duration=duration_ms,
            loop=0,
        )

        frame_total = len(self._frames)
        self._frames.clear()
        self.frame_count = 0
        return f"GIF saved: {path.name} ({frame_total} frames)"

    # <summary>
    # Convert a pygame surface into raw RGB bytes.
    # </summary>
    # <param name="surface">pygame surface used for drawing or capture.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    @staticmethod
    def _surface_rgb_bytes(surface) -> bytes:
        import pygame

        return pygame.image.tostring(surface, "RGB")

    # <summary>
    # Import Pillow lazily so screenshots still work without GIF support.
    # </summary>
    @staticmethod
    def _load_pillow_image_module():
        try:
            from PIL import Image
        except ImportError:
            return None
        return Image

    # <summary>
    # Build a timestamped capture path for the current demo.
    # </summary>
    # <param name="extension">File extension used when building a capture path.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def _new_file_path(self, extension: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return self.output_path / f"{self.demo_name}_{timestamp}.{extension}"

    # <summary>
    # Store a temporary capture status message for the overlay.
    # </summary>
    # <param name="message">Status message to display in the overlay.</param>
    def _set_message(self, message: str) -> None:
        self._message = message
        self._message_timer = self.message_duration


