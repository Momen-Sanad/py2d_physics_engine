"""Small debug overlay helpers shared by the demo scenes."""

from __future__ import annotations


class PerformanceOverlay:
    """Draw a lightweight top-left performance overlay."""

    def __init__(self, font_size: int = 22, update_interval: float = 0.5) -> None:
        import pygame

        self._font = pygame.font.Font(None, font_size)
        self._text_color = (245, 245, 245)
        self._shadow_color = (20, 20, 20)
        self._panel_color = (0, 0, 0, 110)
        self._update_interval = update_interval
        self._elapsed = 0.0
        self._frame_count = 0
        self._display_fps: float | None = None

    def draw(
        self,
        surface,
        frame_time: float,
        fixed_dt: float,
        extra_lines: list[str] | None = None,
    ) -> None:
        import pygame

        if frame_time > 0.0:
            self._elapsed += frame_time
            self._frame_count += 1

        if self._elapsed >= self._update_interval:
            self._display_fps = self._frame_count / self._elapsed
            self._elapsed = 0.0
            self._frame_count = 0

        fps_text = "--.-" if self._display_fps is None else f"{self._display_fps:6.1f}"
        lines = [
            f"FPS (0.5s): {fps_text}",
            f"Physics: {1.0 / fixed_dt:6.1f} Hz",
        ]
        if extra_lines:
            lines.extend(extra_lines)

        rendered_lines = [
            (
                self._font.render(line, True, self._shadow_color),
                self._font.render(line, True, self._text_color),
            )
            for line in lines
        ]
        width = max(text.get_width() for _, text in rendered_lines) + 12
        height = sum(text.get_height() for _, text in rendered_lines) + 10

        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill(self._panel_color)
        surface.blit(panel, (8, 8))

        y = 13
        for shadow, text in rendered_lines:
            surface.blit(shadow, (13, y + 1))
            surface.blit(text, (12, y))
            y += text.get_height()
