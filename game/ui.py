"""Drawing helpers for Splashline Showdown."""

from __future__ import annotations

from math import cos, sin, tau

from engine.math2d import Vec2

from . import config
from .effects import DripEmitter, WindState
from .entities import Arena, Ball, Projectile
from .powerups import ActiveEffect, PowerupKind, PowerupPickup
from .screens import MenuAction, MenuItem
from .settings import GameSettings
from .state import MatchPhase, MatchState, PlayerId, PlayerState


SKY_COLOR = (143, 212, 244)
SAND_COLOR = (241, 229, 186)
WATER_COLOR = (57, 143, 205)
NET_COLOR = (246, 248, 252)
LINE_COLOR = (255, 255, 255)
BEACH_BALL_PANELS = (
    (255, 255, 255),
    (255, 104, 84),
    (255, 217, 82),
    (61, 152, 235),
    (255, 255, 255),
    (71, 205, 190),
)


def draw_arena(surface, arena: Arena) -> None:
    """Draw the shared world backdrop and arena lines."""

    import pygame

    surface.fill(SKY_COLOR)
    pygame.draw.rect(
        surface,
        SAND_COLOR,
        (0, int(arena.water_y - 22.0), config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
    )
    pygame.draw.rect(
        surface,
        WATER_COLOR,
        (0, int(arena.water_y), config.WINDOW_WIDTH, config.WINDOW_HEIGHT - int(arena.water_y)),
    )
    pygame.draw.line(
        surface,
        LINE_COLOR,
        (int(arena.left), int(arena.water_y)),
        (int(arena.right), int(arena.water_y)),
        3,
    )
    left, top, right, bottom = arena.net_rect()
    pygame.draw.rect(surface, NET_COLOR, (left, top, right - left, bottom - top))
    pygame.draw.line(
        surface,
        (205, 212, 223),
        (int(arena.net_x), int(top)),
        (int(arena.net_x), int(bottom)),
        2,
    )


def draw_players(
    surface,
    players: tuple[PlayerState, PlayerState],
    active_player: PlayerId,
    aim_world: Vec2,
) -> None:
    """Draw both players and the active aiming guide."""

    import pygame

    for player in players:
        color = (232, 108, 78) if player.player_id is active_player else (73, 98, 118)
        rect = pygame.Rect(
            int(player.position.x - config.PLAYER_WIDTH * 0.5),
            int(player.position.y - config.PLAYER_HEIGHT * 0.5),
            int(config.PLAYER_WIDTH),
            int(config.PLAYER_HEIGHT),
        )
        pygame.draw.rect(surface, color, rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=10)

        gun_origin = (
            int(player.position.x + (config.PLAYER_GUN_OFFSET_X if player.player_id is PlayerId.LEFT else -config.PLAYER_GUN_OFFSET_X)),
            int(player.position.y + config.PLAYER_GUN_OFFSET_Y),
        )
        pygame.draw.circle(surface, (255, 255, 255), gun_origin, 5)
        if player.player_id is active_player:
            pygame.draw.line(surface, (255, 248, 210), gun_origin, aim_world.to_tuple(), 2)


def draw_ball(surface, ball: Ball) -> None:
    """Draw the central ball as a colorful beach ball."""

    import pygame

    center_x = int(round(ball.body.position.x))
    center_y = int(round(ball.body.position.y))
    position = (center_x, center_y)
    radius = int(ball.body.radius)
    rotation = (ball.body.position.x * 0.035 + ball.body.position.y * 0.012) % tau
    panel_step = tau / len(BEACH_BALL_PANELS)

    pygame.draw.circle(surface, (255, 255, 255), position, radius)
    for index, color in enumerate(BEACH_BALL_PANELS):
        start_angle = rotation + index * panel_step
        end_angle = start_angle + panel_step
        points = [position]
        for segment in range(8):
            t = segment / 7.0
            angle = start_angle + (end_angle - start_angle) * t
            points.append(
                (
                    int(round(center_x + cos(angle) * radius)),
                    int(round(center_y + sin(angle) * radius)),
                )
            )
        pygame.draw.polygon(surface, color, points)

    for index in range(len(BEACH_BALL_PANELS)):
        angle = rotation + index * panel_step
        end = (
            int(round(center_x + cos(angle) * radius)),
            int(round(center_y + sin(angle) * radius)),
        )
        pygame.draw.line(surface, (255, 255, 255), position, end, 2)

    center_radius = max(5, int(radius * 0.22))
    pygame.draw.circle(surface, (255, 255, 255), position, center_radius)
    pygame.draw.circle(surface, (218, 231, 238), position, center_radius, 1)
    pygame.draw.circle(surface, (255, 255, 255), position, radius, 3)
    pygame.draw.circle(surface, (54, 78, 104), position, radius, 1)
    highlight = (
        int(round(center_x - radius * 0.32)),
        int(round(center_y - radius * 0.36)),
    )
    pygame.draw.circle(surface, (255, 255, 255), highlight, max(3, int(radius * 0.12)))


def draw_projectiles(surface, projectiles: list[Projectile]) -> None:
    """Draw active player projectiles."""

    import pygame

    for projectile in projectiles:
        color = (255, 161, 75) if projectile.owner is PlayerId.LEFT else (89, 137, 244)
        if projectile.heavy:
            color = (255, 88, 88) if projectile.owner is PlayerId.LEFT else (84, 110, 255)
        pygame.draw.circle(
            surface,
            color,
            projectile.body.position.to_tuple(),
            int(projectile.body.radius),
        )


def draw_particles(surface, emitter: DripEmitter) -> None:
    """Draw drip and splash particles."""

    import pygame

    for particle in emitter.particles:
        color = (209, 240, 255) if particle.velocity.y < 0.0 else (110, 196, 235)
        pygame.draw.circle(
            surface,
            color,
            particle.position.to_tuple(),
            max(1, int(particle.radius)),
        )


def draw_powerups(surface, pickups: list[PowerupPickup]) -> None:
    """Draw active airborne pickups."""

    import pygame

    color_map = {
        PowerupKind.HEAVY_SHOT: (245, 96, 96),
        PowerupKind.DOUBLE_SHOT: (254, 194, 74),
        PowerupKind.NULL_WIND: (94, 223, 188),
    }
    for pickup in pickups:
        color = color_map[pickup.kind]
        pygame.draw.circle(surface, color, pickup.position.to_tuple(), int(pickup.radius))
        pygame.draw.circle(surface, (255, 255, 255), pickup.position.to_tuple(), int(pickup.radius), 2)


def draw_hud(
    surface,
    fonts: dict[str, object],
    match: MatchState,
    wind: WindState,
    active_effects: list[ActiveEffect],
) -> None:
    """Draw score, timer, turn, wind, and effect state."""

    import pygame

    title_font = fonts["title"]
    body_font = fonts["body"]
    small_font = fonts["small"]

    panel = pygame.Surface((config.WINDOW_WIDTH - 32, 92), pygame.SRCALPHA)
    panel.fill((18, 30, 45, 150))
    surface.blit(panel, (16, 16))

    left_score = title_font.render(str(match.left_player.score), True, (255, 255, 255))
    right_score = title_font.render(str(match.right_player.score), True, (255, 255, 255))
    timer_text = f"{int(match.timer_remaining // 60):02d}:{int(match.timer_remaining % 60):02d}"
    if match.sudden_death and match.winner is None:
        timer_text = "SD"
    timer_surface = title_font.render(timer_text, True, (255, 244, 201))

    surface.blit(left_score, (58, 28))
    surface.blit(right_score, (config.WINDOW_WIDTH - 82 - right_score.get_width(), 28))
    surface.blit(timer_surface, (config.WINDOW_WIDTH * 0.5 - timer_surface.get_width() * 0.5, 28))

    control_name = "Left" if match.turn.active_player is PlayerId.LEFT else "Right"
    status = f"Control: {control_name}  Shots: {match.turn.shots_left}  Cooldown: {match.turn.cooldown_remaining:0.2f}s"
    phase = "Sudden Death" if match.sudden_death and match.winner is None else match.phase.value.replace("_", " ").title()
    wind_label = _wind_label(active_effects, wind.current_force_x)

    surface.blit(body_font.render(status, True, (246, 247, 249)), (58, 66))
    phase_surface = body_font.render(phase, True, (245, 231, 145))
    surface.blit(phase_surface, (config.WINDOW_WIDTH * 0.5 - phase_surface.get_width() * 0.5, 66))
    wind_surface = body_font.render(wind_label, True, (221, 246, 255))
    surface.blit(wind_surface, (config.WINDOW_WIDTH - 72 - wind_surface.get_width(), 66))

    active_lines = _effect_lines(match, active_effects)
    y = 116
    for line in active_lines:
        text = small_font.render(line, True, (252, 252, 252))
        surface.blit(text, (26, y))
        y += text.get_height() + 4


def draw_game_over(surface, fonts: dict[str, object], match: MatchState) -> None:
    """Draw the winner overlay."""

    import pygame

    if match.phase is not MatchPhase.GAME_OVER or match.winner is None:
        return

    overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 15, 24, 150))
    surface.blit(overlay, (0, 0))

    winner_name = "Left Player" if match.winner is PlayerId.LEFT else "Right Player"
    lines = [
        fonts["title"].render(f"{winner_name} Wins", True, (255, 246, 204)),
        fonts["body"].render("Press R to restart the match", True, (255, 255, 255)),
    ]
    total_height = sum(line.get_height() for line in lines) + 10
    y = config.WINDOW_HEIGHT * 0.5 - total_height * 0.5
    for line in lines:
        x = config.WINDOW_WIDTH * 0.5 - line.get_width() * 0.5
        surface.blit(line, (x, y))
        y += line.get_height() + 10


def draw_start_overlay(
    surface,
    fonts: dict[str, object],
    items: list[MenuItem],
    selected_index: int,
) -> None:
    """Draw the first player-facing overlay."""

    _draw_menu_overlay(
        surface,
        fonts,
        "Splashline Showdown",
        "Local beach-ball physics duel",
        [
            "Fire projectiles to knock the beach ball over the net.",
            "First to the score cap wins before the tide turns.",
        ],
        items,
        selected_index,
    )


def draw_pause_overlay(
    surface,
    fonts: dict[str, object],
    items: list[MenuItem],
    selected_index: int,
) -> None:
    """Draw the paused-game overlay."""

    _draw_menu_overlay(
        surface,
        fonts,
        "Paused",
        "Gameplay is frozen",
        [],
        items,
        selected_index,
    )


def draw_how_to_play_overlay(
    surface,
    fonts: dict[str, object],
    items: list[MenuItem],
    selected_index: int,
) -> None:
    """Draw concise controls and objective text."""

    _draw_menu_overlay(
        surface,
        fonts,
        "How To Play",
        "Controls",
        [
            "Objective: score when the ball lands in the opponent water.",
            "Move: A/D or Left/Right.",
            "Aim: mouse. Shoot: left click.",
            "Each possession gets 3 shots.",
            "Control changes when the ball crosses the net.",
            "Esc pauses or goes back from menus.",
        ],
        items,
        selected_index,
    )


def draw_powerups_overlay(
    surface,
    fonts: dict[str, object],
    items: list[MenuItem],
    selected_index: int,
) -> None:
    """Draw the powerup reference overlay."""

    _draw_menu_overlay(
        surface,
        fonts,
        "Powerups",
        "Touch pickups with the ball or a projectile",
        [
            f"{PowerupKind.HEAVY_SHOT.label()}: next shot is heavier and faster.",
            f"{PowerupKind.DOUBLE_SHOT.label()}: next shot fires two projectiles.",
            f"{PowerupKind.NULL_WIND.label()}: temporarily cancels wind.",
            "Ball pickups go to the controlling player.",
            "Projectile pickups go to the projectile owner.",
        ],
        items,
        selected_index,
    )


def draw_options_overlay(
    surface,
    fonts: dict[str, object],
    settings: GameSettings,
    items: list[MenuItem],
    selected_index: int,
) -> None:
    """Draw the runtime audio options overlay."""

    display_items: list[MenuItem] = []
    for item in items:
        if item.action is MenuAction.SFX_VOLUME:
            label = f"SFX Volume: {int(round(settings.sfx_volume * 100.0))}%"
        elif item.action is MenuAction.MUTE:
            label = f"Mute: {'On' if settings.muted else 'Off'}"
        else:
            label = item.label
        display_items.append(MenuItem(label, item.action))

    _draw_menu_overlay(
        surface,
        fonts,
        "Options",
        "Audio",
        [
            "Up/Down selects an option.",
            "Left/Right adjusts SFX volume.",
            "Enter toggles mute.",
        ],
        display_items,
        selected_index,
    )


def draw_game_over_menu_overlay(
    surface,
    fonts: dict[str, object],
    match: MatchState,
    items: list[MenuItem],
    selected_index: int,
) -> None:
    """Draw winner text with restart/menu actions."""

    winner_name = "Left Player" if match.winner is PlayerId.LEFT else "Right Player"
    _draw_menu_overlay(
        surface,
        fonts,
        f"{winner_name} Wins",
        f"Final Score {match.left_player.score} - {match.right_player.score}",
        [],
        items,
        selected_index,
    )


def _draw_menu_overlay(
    surface,
    fonts: dict[str, object],
    title: str,
    subtitle: str,
    lines: list[str],
    items: list[MenuItem],
    selected_index: int,
) -> None:
    """Draw a centered translucent menu panel."""

    import pygame

    overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 15, 24, 126))
    surface.blit(overlay, (0, 0))

    panel_width = 560
    line_height = 28
    menu_height = len(items) * 34
    text_height = len(lines) * line_height
    panel_height = 136 + text_height + menu_height
    panel_height = max(260, panel_height)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 30, 45, 218))
    panel_rect = panel.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
    surface.blit(panel, panel_rect)
    pygame.draw.rect(surface, (255, 255, 255), panel_rect, 2, border_radius=8)

    title_font = fonts["title"]
    body_font = fonts["body"]
    small_font = fonts["small"]

    y = panel_rect.top + 26
    title_surface = title_font.render(title, True, (255, 246, 204))
    surface.blit(title_surface, (panel_rect.centerx - title_surface.get_width() * 0.5, y))
    y += title_surface.get_height() + 8

    if subtitle:
        subtitle_surface = body_font.render(subtitle, True, (221, 246, 255))
        surface.blit(subtitle_surface, (panel_rect.centerx - subtitle_surface.get_width() * 0.5, y))
        y += subtitle_surface.get_height() + 18
    else:
        y += 14

    for line in lines:
        text_surface = small_font.render(line, True, (246, 247, 249))
        surface.blit(text_surface, (panel_rect.left + 38, y))
        y += line_height

    y += 12
    for index, item in enumerate(items):
        selected = index == selected_index
        color = (255, 244, 201) if selected else (246, 247, 249)
        prefix = "> " if selected else "  "
        item_surface = body_font.render(f"{prefix}{item.label}", True, color)
        surface.blit(item_surface, (panel_rect.left + 180, y))
        y += 34


def draw_help(surface, font) -> None:
    """Draw the main control legend."""

    import pygame

    lines = [
        "A/D or Left/Right: move active player  Mouse: aim  LMB: shoot",
        "Turn switches when shots run out or the ball crosses the net",
        "Space: pause  O: toggle overlay  H: help  R: restart match  TAB: screenshot  `: GIF  Esc: quit",
    ]
    width = max(font.size(line)[0] for line in lines) + 18
    height = len(lines) * 20 + 14
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 135))
    x = 18
    y = config.WINDOW_HEIGHT - height - 18
    surface.blit(panel, (x, y))
    text_y = y + 8
    for line in lines:
        surface.blit(font.render(line, True, (250, 250, 250)), (x + 9, text_y))
        text_y += 20


def _wind_label(active_effects: list[ActiveEffect], wind_force_x: float) -> str:
    if any(effect.kind is PowerupKind.NULL_WIND for effect in active_effects):
        return "Wind: nulled"
    direction = "->" if wind_force_x > 10.0 else "<-" if wind_force_x < -10.0 else "--"
    return f"Wind: {direction} {abs(wind_force_x):.0f}"


def _effect_lines(match: MatchState, active_effects: list[ActiveEffect]) -> list[str]:
    lines: list[str] = []

    left_effects = ", ".join(
        f"{name} {remaining:0.1f}s"
        for name, remaining in match.left_player.effect_timers.items()
    ) or "none"
    right_effects = ", ".join(
        f"{name} {remaining:0.1f}s"
        for name, remaining in match.right_player.effect_timers.items()
    ) or "none"

    lines.append(f"Left effects: {left_effects}")
    lines.append(f"Right effects: {right_effects}")

    global_effects = [
        f"{effect.kind.label()} {effect.remaining:0.1f}s"
        for effect in active_effects
        if effect.owner is None
    ]
    if global_effects:
        lines.append(f"Global: {', '.join(global_effects)}")
    return lines
