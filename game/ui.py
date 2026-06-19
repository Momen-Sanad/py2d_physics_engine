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
POWERUP_COLORS = {
    PowerupKind.HEAVY_SHOT: (236, 72, 82),
    PowerupKind.DOUBLE_SHOT: (255, 198, 58),
    PowerupKind.QUICK_SHOT: (145, 116, 255),
    PowerupKind.NULL_WIND: (42, 204, 174),
    PowerupKind.STICKY_BALL: (92, 184, 87),
}
PLAYER_COLORS = {
    PlayerId.LEFT: {
        "shorts": (42, 184, 178),
        "trim": (255, 229, 105),
        "skin": (255, 204, 145),
        "skin_shadow": (224, 153, 101),
        "hair": (116, 78, 48),
        "hat": (246, 215, 136),
        "hat_band": (48, 153, 191),
        "blaster": (70, 213, 229),
        "blaster_tip": (255, 229, 105),
    },
    PlayerId.RIGHT: {
        "shorts": (106, 91, 196),
        "trim": (255, 181, 91),
        "skin": (242, 177, 122),
        "skin_shadow": (204, 128, 85),
        "hair": (80, 57, 43),
        "hat": (255, 232, 157),
        "hat_band": (237, 96, 119),
        "blaster": (255, 126, 164),
        "blaster_tip": (255, 245, 176),
    },
}


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
        palette = PLAYER_COLORS[player.player_id]
        facing = 1 if player.player_id is PlayerId.LEFT else -1
        center_x = int(round(player.position.x))
        feet_y = int(round(player.position.y + config.PLAYER_HEIGHT * 0.5))
        active = player.player_id is active_player

        shadow_rect = pygame.Rect(0, 0, int(config.PLAYER_WIDTH * 1.15), 10)
        shadow_rect.center = (center_x, feet_y + 3)
        pygame.draw.ellipse(surface, (119, 151, 143), shadow_rect)

        hip_y = feet_y - 22
        leg_width = 11
        for offset in (-10, 10):
            leg_rect = pygame.Rect(0, 0, leg_width, 27)
            leg_rect.midtop = (center_x + offset, hip_y)
            pygame.draw.rect(surface, palette["skin"], leg_rect, border_radius=5)
            foot_rect = pygame.Rect(0, 0, 18, 7)
            foot_rect.midleft = (
                leg_rect.left - 3 if offset < 0 else leg_rect.left,
                feet_y - 2,
            )
            if offset > 0:
                foot_rect.midright = (leg_rect.right + 3, feet_y - 2)
            pygame.draw.rect(surface, (80, 155, 187), foot_rect, border_radius=4)
            pygame.draw.line(
                surface,
                (255, 244, 205),
                foot_rect.midtop,
                foot_rect.center,
                2,
            )

        body_rect = pygame.Rect(0, 0, int(config.PLAYER_WIDTH), 38)
        body_rect.center = (center_x, feet_y - 42)
        shorts_rect = pygame.Rect(0, 0, int(config.PLAYER_WIDTH * 0.92), 20)
        shorts_rect.midtop = (center_x, body_rect.bottom - 2)
        pygame.draw.rect(surface, palette["shorts"], shorts_rect, border_radius=8)
        pygame.draw.line(
            surface,
            palette["trim"],
            (shorts_rect.left + 7, shorts_rect.top + 5),
            (shorts_rect.right - 7, shorts_rect.top + 5),
            3,
        )

        pygame.draw.rect(surface, palette["skin"], body_rect, border_radius=13)
        pygame.draw.rect(surface, palette["skin_shadow"], body_rect, 2, border_radius=13)
        pygame.draw.arc(
            surface,
            palette["skin_shadow"],
            body_rect.inflate(-22, -18),
            3.35,
            6.05,
            2,
        )
        pygame.draw.line(
            surface,
            (255, 224, 171),
            (body_rect.left + 12, body_rect.top + 8),
            (body_rect.left + 18, body_rect.top + 5),
            2,
        )

        head_pos = (center_x, body_rect.top - 10)
        pygame.draw.circle(surface, palette["skin"], head_pos, 15)
        pygame.draw.circle(surface, palette["hair"], (center_x - 6 * facing, body_rect.top - 20), 7)
        pygame.draw.circle(surface, palette["hair"], (center_x + 4 * facing, body_rect.top - 22), 6)

        brim_rect = pygame.Rect(0, 0, 42, 9)
        brim_rect.center = (center_x, body_rect.top - 23)
        pygame.draw.ellipse(surface, palette["hat"], brim_rect)
        crown_rect = pygame.Rect(0, 0, 26, 14)
        crown_rect.midbottom = (center_x, body_rect.top - 21)
        pygame.draw.ellipse(surface, palette["hat"], crown_rect)
        pygame.draw.line(
            surface,
            palette["hat_band"],
            (crown_rect.left + 4, crown_rect.centery + 2),
            (crown_rect.right - 4, crown_rect.centery + 2),
            3,
        )

        eye_y = body_rect.top - 11
        pygame.draw.circle(surface, (67, 55, 47), (center_x - 5, eye_y), 2)
        pygame.draw.circle(surface, (67, 55, 47), (center_x + 6, eye_y), 2)
        smile_rect = pygame.Rect(0, 0, 12, 7)
        smile_rect.center = (center_x + 1 * facing, body_rect.top - 3)
        pygame.draw.arc(
            surface,
            (124, 75, 60),
            smile_rect,
            0.15,
            3.0,
            2,
        )

        gun_origin = (
            int(player.position.x + (config.PLAYER_GUN_OFFSET_X if player.player_id is PlayerId.LEFT else -config.PLAYER_GUN_OFFSET_X)),
            int(player.position.y + config.PLAYER_GUN_OFFSET_Y),
        )
        if active:
            aim_dx = aim_world.x - gun_origin[0]
            aim_dy = aim_world.y - gun_origin[1]
        else:
            aim_dx = float(facing)
            aim_dy = -0.12
        aim_length = max((aim_dx * aim_dx + aim_dy * aim_dy) ** 0.5, 0.001)
        aim_unit = (aim_dx / aim_length, aim_dy / aim_length)
        side_unit = (-aim_unit[1], aim_unit[0])

        shoulder = (center_x + 18 * facing, body_rect.top + 16)
        grip = (
            int(round(gun_origin[0] - aim_unit[0] * 4)),
            int(round(gun_origin[1] - aim_unit[1] * 4)),
        )
        barrel_end = (
            int(round(gun_origin[0] + aim_unit[0] * 28)),
            int(round(gun_origin[1] + aim_unit[1] * 28)),
        )
        tank_center = (
            int(round(gun_origin[0] - aim_unit[0] * 7 + side_unit[0] * 6)),
            int(round(gun_origin[1] - aim_unit[1] * 7 + side_unit[1] * 6)),
        )
        handle_end = (
            int(round(gun_origin[0] - aim_unit[0] * 3 + side_unit[0] * 13)),
            int(round(gun_origin[1] - aim_unit[1] * 3 + side_unit[1] * 13)),
        )
        pygame.draw.line(surface, palette["skin"], shoulder, gun_origin, 7)
        pygame.draw.line(
            surface,
            palette["blaster"],
            grip,
            barrel_end,
            5,
        )
        pygame.draw.line(surface, palette["blaster_tip"], gun_origin, handle_end, 4)
        pygame.draw.circle(surface, palette["blaster"], tank_center, 7)
        pygame.draw.circle(surface, palette["blaster_tip"], gun_origin, 5)
        pygame.draw.circle(
            surface,
            palette["blaster_tip"],
            barrel_end,
            4,
        )

        if active:
            pygame.draw.ellipse(surface, (255, 246, 156), body_rect.inflate(18, 54), 3)
            pygame.draw.line(surface, (255, 248, 210), barrel_end, aim_world.to_tuple(), 2)


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
        color = emitter.colors.get(id(particle))
        if color is None:
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

    for pickup in pickups:
        center = pickup.position.to_tuple()
        radius = int(pickup.radius)
        color = POWERUP_COLORS[pickup.kind]
        shadow_center = (center[0] + 2, center[1] + 3)
        pygame.draw.circle(surface, (20, 36, 52), shadow_center, radius)
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, (255, 255, 255), center, radius, 2)
        pygame.draw.circle(surface, (31, 45, 64), center, max(4, radius // 3), 2)
        if pickup.kind is PowerupKind.HEAVY_SHOT:
            pygame.draw.line(surface, (255, 255, 255), (center[0] - 7, center[1]), (center[0] + 7, center[1]), 3)
            pygame.draw.line(surface, (255, 255, 255), (center[0], center[1] - 7), (center[0], center[1] + 7), 3)
        elif pickup.kind is PowerupKind.DOUBLE_SHOT:
            pygame.draw.circle(surface, (255, 255, 255), (center[0] - 5, center[1]), 4)
            pygame.draw.circle(surface, (255, 255, 255), (center[0] + 5, center[1]), 4)
        elif pickup.kind is PowerupKind.QUICK_SHOT:
            pygame.draw.polygon(
                surface,
                (255, 255, 255),
                [
                    (center[0] - 6, center[1] + 7),
                    (center[0] + 1, center[1] - 2),
                    (center[0] - 1, center[1] - 2),
                    (center[0] + 6, center[1] - 8),
                ],
            )
        elif pickup.kind is PowerupKind.NULL_WIND:
            pygame.draw.line(surface, (255, 255, 255), (center[0] - 8, center[1] + 6), (center[0] + 8, center[1] - 6), 3)
        else:
            pygame.draw.circle(surface, (255, 255, 255), center, 5)
            pygame.draw.circle(surface, (31, 45, 64), center, 2)


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

    panel_rect = pygame.Rect(16, 16, config.WINDOW_WIDTH - 32, 88)
    panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    panel.fill((18, 30, 45, 142))
    surface.blit(panel, panel_rect)
    pygame.draw.rect(surface, (238, 248, 255), panel_rect, 1, border_radius=8)

    left_score = title_font.render(str(match.left_player.score), True, (255, 255, 255))
    right_score = title_font.render(str(match.right_player.score), True, (255, 255, 255))
    timer_text = f"{int(match.timer_remaining // 60):02d}:{int(match.timer_remaining % 60):02d}"
    if match.sudden_death and match.winner is None:
        timer_text = "SD"
    timer_surface = title_font.render(timer_text, True, (255, 244, 201))

    left_label = small_font.render("LEFT", True, (214, 232, 241))
    right_label = small_font.render("RIGHT", True, (214, 232, 241))
    surface.blit(left_label, (46, 29))
    surface.blit(left_score, (46, 49))
    surface.blit(right_label, (config.WINDOW_WIDTH - 46 - right_label.get_width(), 29))
    surface.blit(right_score, (config.WINDOW_WIDTH - 46 - right_score.get_width(), 49))
    surface.blit(timer_surface, (config.WINDOW_WIDTH * 0.5 - timer_surface.get_width() * 0.5, 27))

    control_name = "Left" if match.turn.active_player is PlayerId.LEFT else "Right"
    cooldown = "Ready" if match.turn.cooldown_remaining <= 0.0 else f"{match.turn.cooldown_remaining:0.2f}s"
    status = f"Control: {control_name}   Shots: {match.turn.shots_left}/{match.shots_per_turn}   {cooldown}"
    phase = "Sudden Death" if match.sudden_death and match.winner is None else match.phase.value.replace("_", " ").title()
    wind_label = _wind_label(active_effects, wind.current_force_x)

    surface.blit(body_font.render(status, True, (246, 247, 249)), (140, 64))
    phase_surface = small_font.render(phase, True, (245, 231, 145))
    surface.blit(phase_surface, (config.WINDOW_WIDTH * 0.5 - phase_surface.get_width() * 0.5, 68))
    wind_surface = body_font.render(wind_label, True, (221, 246, 255))
    surface.blit(wind_surface, (config.WINDOW_WIDTH - 146 - wind_surface.get_width(), 64))

    active_lines = _effect_lines(match, active_effects)
    chip_x = 24
    for line in active_lines:
        text = small_font.render(line, True, (252, 252, 252))
        chip = pygame.Surface((text.get_width() + 20, 26), pygame.SRCALPHA)
        chip.fill((18, 30, 45, 155))
        chip_rect = chip.get_rect(topleft=(chip_x, 110))
        surface.blit(chip, chip_rect)
        pygame.draw.rect(surface, (238, 248, 255), chip_rect, 1, border_radius=6)
        surface.blit(text, (chip_rect.left + 10, chip_rect.top + 4))
        chip_x += chip_rect.width + 8


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
            f"{PowerupKind.QUICK_SHOT.label()}: next shot cools down faster.",
            f"{PowerupKind.NULL_WIND.label()}: temporarily cancels wind.",
            f"{PowerupKind.STICKY_BALL.label()}: temporarily adds ball drag.",
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
            "Controls opens keyboard remapping.",
        ],
        display_items,
        selected_index,
    )


def draw_controls_overlay(
    surface,
    fonts: dict[str, object],
    settings: GameSettings,
    items: list[MenuItem],
    selected_index: int,
    remap_action: MenuAction | None,
) -> None:
    """Draw keyboard remapping options."""

    display_items: list[MenuItem] = []
    for item in items:
        label = item.label
        if item.action is MenuAction.REMAP_LEFT:
            label = f"Move Left: {_format_key_name(settings.bindings.move_left)}"
        elif item.action is MenuAction.REMAP_RIGHT:
            label = f"Move Right: {_format_key_name(settings.bindings.move_right)}"
        elif item.action is MenuAction.REMAP_FIRE:
            label = f"Fire Key: {_format_key_name(settings.bindings.fire)}"
        display_items.append(MenuItem(label, item.action))

    waiting_text = "Press any key to bind, or Esc to cancel." if remap_action is not None else "Menu keys stay fixed."
    _draw_menu_overlay(
        surface,
        fonts,
        "Controls",
        "Keyboard remapping",
        [
            waiting_text,
            "Mouse aim and left click always work.",
        ],
        display_items,
        selected_index,
    )


def draw_tutorial_overlay(
    surface,
    fonts: dict[str, object],
    page_title: str,
    page_lines: list[str],
    page_index: int,
    page_count: int,
    items: list[MenuItem],
    selected_index: int,
) -> None:
    """Draw one page of the guided tutorial."""

    _draw_menu_overlay(
        surface,
        fonts,
        "Tutorial",
        f"{page_title}  ({page_index + 1}/{page_count})",
        page_lines,
        items,
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
    overlay.fill((8, 15, 24, 112))
    surface.blit(overlay, (0, 0))

    panel_width = 590
    padding_x = 42
    line_height = 30
    menu_row_height = 38
    menu_height = len(items) * menu_row_height
    text_height = len(lines) * line_height
    panel_height = 150 + text_height + menu_height
    panel_height = max(276, panel_height)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 30, 45, 226))
    panel_rect = panel.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
    surface.blit(panel, panel_rect)
    pygame.draw.rect(surface, (238, 248, 255), panel_rect, 2, border_radius=8)

    title_font = fonts["title"]
    body_font = fonts["body"]
    small_font = fonts["small"]

    y = panel_rect.top + 24
    title_surface = title_font.render(title, True, (255, 246, 204))
    surface.blit(title_surface, (panel_rect.centerx - title_surface.get_width() * 0.5, y))
    y += title_surface.get_height() + 9

    if subtitle:
        subtitle_surface = body_font.render(subtitle, True, (221, 246, 255))
        surface.blit(subtitle_surface, (panel_rect.centerx - subtitle_surface.get_width() * 0.5, y))
        y += subtitle_surface.get_height() + 22
    else:
        y += 18

    pygame.draw.line(
        surface,
        (255, 220, 112),
        (panel_rect.left + padding_x, int(y - 12)),
        (panel_rect.right - padding_x, int(y - 12)),
        2,
    )

    for line in lines:
        text_surface = small_font.render(line, True, (246, 247, 249))
        surface.blit(text_surface, (panel_rect.left + padding_x, y))
        y += line_height

    y += 12
    for index, item in enumerate(items):
        selected = index == selected_index
        item_rect = pygame.Rect(panel_rect.left + 152, y - 4, panel_width - 304, 32)
        if selected:
            selected_fill = pygame.Surface(item_rect.size, pygame.SRCALPHA)
            selected_fill.fill((255, 220, 112, 42))
            surface.blit(selected_fill, item_rect)
            pygame.draw.rect(surface, (255, 220, 112), item_rect, 1, border_radius=6)
            pygame.draw.rect(surface, (255, 220, 112), (item_rect.left, item_rect.top, 4, item_rect.height), border_radius=3)
        color = (255, 246, 204) if selected else (246, 247, 249)
        item_surface = body_font.render(item.label, True, color)
        surface.blit(item_surface, (item_rect.centerx - item_surface.get_width() * 0.5, y))
        y += menu_row_height


def draw_help(surface, font) -> None:
    """Draw the main control legend."""

    import pygame

    lines = [
        "A/D or Left/Right: move active player  Mouse: aim  LMB: shoot",
        "You get 3 shots; control switches when the ball crosses or after the failsafe",
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


def _format_key_name(key_name: str) -> str:
    if len(key_name) == 1:
        return key_name.upper()
    return key_name.replace("_", " ").title()


def _effect_lines(match: MatchState, active_effects: list[ActiveEffect]) -> list[str]:
    lines: list[str] = []

    left_effects = ", ".join(
        f"{name} {remaining:0.1f}s"
        for name, remaining in match.left_player.effect_timers.items()
    )
    right_effects = ", ".join(
        f"{name} {remaining:0.1f}s"
        for name, remaining in match.right_player.effect_timers.items()
    )

    if left_effects:
        lines.append(f"L: {left_effects}")
    if right_effects:
        lines.append(f"R: {right_effects}")

    global_effects = [
        f"{effect.kind.label()} {effect.remaining:0.1f}s"
        for effect in active_effects
        if effect.owner is None
    ]
    if global_effects:
        lines.append(f"Global: {', '.join(global_effects)}")
    return lines
