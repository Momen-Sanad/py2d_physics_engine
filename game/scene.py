"""Playable pygame scene for Splashline Showdown."""

from __future__ import annotations

from random import Random

from engine.broadphase import SpatialHashGrid
from engine.core import SimulationClock
from engine.debug import PerformanceOverlay
from engine.forces import drag_force

from media_capture import CaptureController

from . import config
from .effects import (
    DripEmitter,
    WindState,
    apply_wind_to_bodies,
    emit_ball_drips,
    reset_wind,
    spawn_splash_burst,
    step_effect_particles,
    update_drip_intensity,
    update_wind,
)
from .entities import build_arena, build_players
from .input import (
    InputState,
    check_turn_cross_net,
    read_input,
    should_sync_turn_to_ball_side,
    try_fire_projectiles,
    update_player_movement,
)
from .physics import (
    ball_water_side,
    build_ball,
    reset_ball,
    resolve_arena_bounds,
    resolve_net_collisions,
    resolve_projectile_collisions,
    step_rigid_bodies,
    update_ball_side,
)
from .powerups import (
    ActiveEffect,
    PowerupPickup,
    apply_active_effects,
    collect_powerups,
    expire_effects,
    pop_fire_modifiers,
    spawn_powerup,
    tick_pickups,
)
from .screens import MenuAction, MenuItem, ScreenMode, clamp_menu_index
from .state import MatchPhase, MatchState, PlayerId, award_point, reset_rally, start_match, switch_turn, tick_match_timer
from .ui import (
    draw_arena,
    draw_ball,
    draw_game_over_menu_overlay,
    draw_how_to_play_overlay,
    draw_hud,
    draw_options_placeholder_overlay,
    draw_particles,
    draw_pause_overlay,
    draw_players,
    draw_powerups,
    draw_powerups_overlay,
    draw_projectiles,
    draw_start_overlay,
)


START_MENU = [
    MenuItem("Start", MenuAction.START_GAME),
    MenuItem("How To Play", MenuAction.HOW_TO_PLAY),
    MenuItem("Powerups", MenuAction.POWERUPS),
    MenuItem("Options", MenuAction.OPTIONS),
    MenuItem("Exit", MenuAction.EXIT),
]
PAUSE_MENU = [
    MenuItem("Resume", MenuAction.RESUME),
    MenuItem("Restart Match", MenuAction.RESTART),
    MenuItem("How To Play", MenuAction.HOW_TO_PLAY),
    MenuItem("Powerups", MenuAction.POWERUPS),
    MenuItem("Options", MenuAction.OPTIONS),
    MenuItem("Exit", MenuAction.EXIT),
]
GAME_OVER_MENU = [
    MenuItem("Restart", MenuAction.RESTART),
    MenuItem("Main Menu", MenuAction.MAIN_MENU),
    MenuItem("Exit", MenuAction.EXIT),
]
BACK_MENU = [MenuItem("Back", MenuAction.BACK)]


def menu_items_for(screen_mode: ScreenMode) -> list[MenuItem]:
    """Return keyboard menu rows for the active overlay."""

    if screen_mode is ScreenMode.START:
        return START_MENU
    if screen_mode is ScreenMode.PAUSED:
        return PAUSE_MENU
    if screen_mode is ScreenMode.GAME_OVER:
        return GAME_OVER_MENU
    if screen_mode in {ScreenMode.HOW_TO_PLAY, ScreenMode.POWERUPS, ScreenMode.OPTIONS}:
        return BACK_MENU
    return []


class SplashlineScene:
    """Owns the full match, entities, effects, and gameplay loop state."""

    def __init__(self) -> None:
        self.rng = Random(14)
        self.arena = build_arena()
        self.left_player, self.right_player = build_players(self.arena)
        self._left_spawn = self.left_player.position.copy()
        self._right_spawn = self.right_player.position.copy()
        self.match = start_match(
            self.left_player,
            self.right_player,
            shots_per_turn=config.SHOTS_PER_TURN,
            match_duration=config.MATCH_DURATION,
            score_cap=config.SCORE_CAP,
            starting_player=PlayerId.LEFT,
        )
        self.ball = build_ball(self.arena)
        self.projectiles: list = []
        self.wind = WindState(next_change=1.6)
        self.emitter = DripEmitter()
        self.pickups: list[PowerupPickup] = []
        self.active_effects: list[ActiveEffect] = []
        self.broadphase = SpatialHashGrid(cell_size=64.0)
        self.round_reset_timer = 0.0
        self.powerup_spawn_timer = self.rng.uniform(config.POWERUP_SPAWN_MIN, config.POWERUP_SPAWN_MAX)
        self.allow_turn_side_sync = True
        self.begin_match()

    def begin_match(self) -> None:
        """Restart the entire match and first rally."""

        self.left_player.score = 0
        self.right_player.score = 0
        self.match.timer_remaining = self.match.match_duration
        self.match.winner = None
        self.match.sudden_death = False
        self.match.last_point_winner = None
        self.match.rally_index = 0
        self.match.turn.active_player = PlayerId.LEFT
        reset_wind(self.wind, self.rng)
        self.begin_rally(starting_player=PlayerId.LEFT)

    def begin_rally(self, starting_player: PlayerId | None = None) -> None:
        """Reset the live rally state while preserving the match score."""

        self.left_player.position.set(self._left_spawn.x, self._left_spawn.y)
        self.right_player.position.set(self._right_spawn.x, self._right_spawn.y)
        self.projectiles.clear()
        self.pickups.clear()
        self.active_effects.clear()
        self.left_player.effect_timers.clear()
        self.right_player.effect_timers.clear()
        self.emitter.particles.clear()
        self.emitter.birth_lifetimes.clear()
        self.emitter.emit_accumulator = 0.0
        self.round_reset_timer = 0.0
        self.powerup_spawn_timer = self.rng.uniform(config.POWERUP_SPAWN_MIN, config.POWERUP_SPAWN_MAX)
        self.allow_turn_side_sync = True
        reset_wind(self.wind, self.rng)
        reset_rally(self.match, starting_player=starting_player)
        reset_ball(self.ball, self.arena, self.rng)

    def switch_control(self) -> PlayerId:
        """Switch active player control and prevent immediate side resync."""

        active_player = switch_turn(self.match)
        self.allow_turn_side_sync = False
        return active_player

    def step(self, input_state: InputState, dt: float) -> None:
        """Advance gameplay by one fixed update step."""

        self.match.turn.cooldown_remaining = max(0.0, self.match.turn.cooldown_remaining - dt)
        expire_effects(self.active_effects, dt, self.match.players())
        tick_pickups(self.pickups, dt)

        effective_wind_x = apply_active_effects(self.active_effects, self.wind.current_force_x)

        if self.match.phase is MatchPhase.GAME_OVER:
            step_effect_particles(self.emitter, dt, effective_wind_x)
            return

        if self.match.phase is MatchPhase.POINT_SCORED:
            self.round_reset_timer = max(0.0, self.round_reset_timer - dt)
            step_effect_particles(self.emitter, dt, effective_wind_x)
            if self.round_reset_timer <= 0.0 and self.match.winner is None:
                self.begin_rally()
            return

        tick_match_timer(self.match, dt)
        if self.match.phase is MatchPhase.GAME_OVER:
            step_effect_particles(self.emitter, dt, effective_wind_x)
            return

        update_wind(self.wind, dt, self.rng)
        effective_wind_x = apply_active_effects(self.active_effects, self.wind.current_force_x)

        active_player = self.match.player(self.match.turn.active_player)
        update_player_movement(active_player, input_state, dt)

        if input_state.fire_pressed and len(self.projectiles) < config.MAX_PROJECTILES:
            modifiers = pop_fire_modifiers(self.active_effects, active_player.player_id, self.match.players())
            spawned = try_fire_projectiles(
                active_player,
                input_state,
                self.match.turn,
                self.arena,
                fire_count=modifiers.projectile_count,
                speed_scale=modifiers.speed_scale,
                mass_scale=modifiers.mass_scale,
                projectile_budget=config.MAX_PROJECTILES - len(self.projectiles),
            )
            if spawned:
                self.allow_turn_side_sync = False
                self.projectiles.extend(spawned)

        self.powerup_spawn_timer -= dt
        if self.powerup_spawn_timer <= 0.0:
            spawn_powerup(self.rng, self.arena, self.pickups)
            self.powerup_spawn_timer = self.rng.uniform(config.POWERUP_SPAWN_MIN, config.POWERUP_SPAWN_MAX)

        self.ball.body.apply_force(
            drag_force(
                self.ball.body.velocity,
                config.BALL_DRIP_DRAG_BASE + config.BALL_DRIP_DRAG_BONUS * self.ball.drip_intensity,
            )
        )
        apply_wind_to_bodies([self.ball.body, *(projectile.body for projectile in self.projectiles)], effective_wind_x)
        step_rigid_bodies(self.ball, self.projectiles, dt)
        resolve_net_collisions(self.ball, self.projectiles, self.arena)
        impact_speed = resolve_projectile_collisions(self.ball, self.projectiles, self.broadphase)
        update_drip_intensity(self.ball, impact_speed, dt)
        if impact_speed > 220.0:
            spawn_splash_burst(self.emitter, self.ball.body.position, effective_wind_x, self.rng, count=7)

        resolve_arena_bounds(self.ball, self.projectiles, self.arena, dt)
        previous_side, current_side = update_ball_side(self.ball, self.arena)
        turn_switched = False
        if (
            check_turn_cross_net(self.match.turn.active_player, previous_side, current_side)
            or (
                self.allow_turn_side_sync
                and should_sync_turn_to_ball_side(
                    self.match.turn.active_player,
                    current_side,
                    self.ball.body.position.x,
                    self.arena.net_x,
                    settle_distance=self.ball.body.radius + self.arena.net_width,
                )
            )
        ):
            self.switch_control()
            turn_switched = True

        turn = self.match.turn
        if not turn_switched and turn.awaiting_cross:
            turn.out_of_ammo_timer += dt
            if turn.out_of_ammo_timer >= config.OUT_OF_AMMO_TURN_FAILSAFE:
                self.switch_control()

        collect_powerups(
            self.ball,
            self.projectiles,
            self.pickups,
            self.active_effects,
            self.match.turn.active_player,
            self.match.players(),
        )
        emit_ball_drips(self.ball, self.emitter, effective_wind_x, self.rng, dt)
        step_effect_particles(self.emitter, dt, effective_wind_x)

        if self.ball.touched_water:
            spawn_splash_burst(self.emitter, self.ball.body.position, effective_wind_x, self.rng, count=20)
            award_point(
                self.match,
                water_side=ball_water_side(self.ball, self.arena),
                last_side=self.ball.last_side,
            )
            self.round_reset_timer = config.ROUND_RESET_DELAY


def run() -> None:
    """Run the interactive Splashline Showdown pygame scene."""

    import pygame

    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=config.FIXED_DT, max_substeps=config.MAX_SUBSTEPS)
    overlay = PerformanceOverlay(font_size=20)
    capture = CaptureController(demo_name="splashline_showdown")

    fonts = {
        "title": pygame.font.Font(None, 42),
        "body": pygame.font.Font(None, 27),
        "small": pygame.font.Font(None, 22),
    }

    scene = SplashlineScene()
    screen_mode = ScreenMode.START
    return_mode = ScreenMode.START
    selected_index = 0
    show_overlay = False
    running = True

    def set_screen(next_mode: ScreenMode) -> None:
        nonlocal screen_mode, selected_index

        screen_mode = next_mode
        selected_index = 0

    def handle_menu_action(action: MenuAction) -> None:
        nonlocal return_mode, running, scene

        if action is MenuAction.START_GAME:
            scene = SplashlineScene()
            set_screen(ScreenMode.PLAYING)
        elif action is MenuAction.RESUME:
            set_screen(ScreenMode.PLAYING)
        elif action is MenuAction.RESTART:
            scene = SplashlineScene()
            set_screen(ScreenMode.PLAYING)
        elif action is MenuAction.HOW_TO_PLAY:
            return_mode = screen_mode
            set_screen(ScreenMode.HOW_TO_PLAY)
        elif action is MenuAction.POWERUPS:
            return_mode = screen_mode
            set_screen(ScreenMode.POWERUPS)
        elif action is MenuAction.OPTIONS:
            return_mode = screen_mode
            set_screen(ScreenMode.OPTIONS)
        elif action is MenuAction.MAIN_MENU:
            scene = SplashlineScene()
            set_screen(ScreenMode.START)
        elif action is MenuAction.BACK:
            set_screen(return_mode)
        elif action is MenuAction.EXIT:
            running = False

    def handle_escape() -> None:
        nonlocal running, scene

        if screen_mode is ScreenMode.PLAYING:
            set_screen(ScreenMode.PAUSED)
        elif screen_mode is ScreenMode.PAUSED:
            set_screen(ScreenMode.PLAYING)
        elif screen_mode is ScreenMode.START:
            running = False
        elif screen_mode is ScreenMode.GAME_OVER:
            scene = SplashlineScene()
            set_screen(ScreenMode.START)
        else:
            set_screen(return_mode)

    while running:
        frame_time = min(clock.tick(config.RENDER_FPS) / 1000.0, 0.25)
        events = list(pygame.event.get())
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if capture.handle_keydown(event, screen):
                    continue
                if event.key == pygame.K_ESCAPE:
                    handle_escape()
                elif event.key == pygame.K_SPACE and screen_mode is ScreenMode.PLAYING:
                    set_screen(ScreenMode.PAUSED)
                elif event.key == pygame.K_h:
                    if screen_mode is ScreenMode.HOW_TO_PLAY:
                        set_screen(return_mode)
                    else:
                        return_mode = screen_mode
                        set_screen(ScreenMode.HOW_TO_PLAY)
                elif event.key == pygame.K_o:
                    show_overlay = not show_overlay
                elif event.key == pygame.K_r:
                    scene = SplashlineScene()
                    set_screen(ScreenMode.PLAYING)
                elif screen_mode is not ScreenMode.PLAYING:
                    items = menu_items_for(screen_mode)
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_index = clamp_menu_index(selected_index - 1, len(items))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_index = clamp_menu_index(selected_index + 1, len(items))
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        if items:
                            handle_menu_action(items[selected_index].action)

        keys = pygame.key.get_pressed()
        frame_input = read_input(events, keys, mouse_pos)

        if screen_mode is ScreenMode.PLAYING:
            fire_consumed = False
            for _ in range(simulation_clock.consume(frame_time)):
                step_input = InputState(
                    move_axis=frame_input.move_axis,
                    aim_world=frame_input.aim_world,
                    fire_pressed=frame_input.fire_pressed and not fire_consumed,
                    hop_pressed=False,
                )
                scene.step(step_input, config.FIXED_DT)
                fire_consumed = True
            if scene.match.phase is MatchPhase.GAME_OVER:
                set_screen(ScreenMode.GAME_OVER)

        draw_arena(screen, scene.arena)
        draw_powerups(screen, scene.pickups)
        draw_players(
            screen,
            scene.match.players(),
            scene.match.turn.active_player,
            frame_input.aim_world,
        )
        draw_particles(screen, scene.emitter)
        draw_projectiles(screen, scene.projectiles)
        draw_ball(screen, scene.ball)
        draw_hud(screen, fonts, scene.match, scene.wind, scene.active_effects)

        items = menu_items_for(screen_mode)
        selected_index = clamp_menu_index(selected_index, len(items))
        if screen_mode is ScreenMode.START:
            draw_start_overlay(screen, fonts, items, selected_index)
        elif screen_mode is ScreenMode.PAUSED:
            draw_pause_overlay(screen, fonts, items, selected_index)
        elif screen_mode is ScreenMode.HOW_TO_PLAY:
            draw_how_to_play_overlay(screen, fonts, items, selected_index)
        elif screen_mode is ScreenMode.POWERUPS:
            draw_powerups_overlay(screen, fonts, items, selected_index)
        elif screen_mode is ScreenMode.OPTIONS:
            draw_options_placeholder_overlay(screen, fonts, items, selected_index)
        elif screen_mode is ScreenMode.GAME_OVER:
            draw_game_over_menu_overlay(screen, fonts, scene.match, items, selected_index)

        if show_overlay:
            overlay_lines = [
                f"Projectiles: {len(scene.projectiles)}/{config.MAX_PROJECTILES}",
                f"Particles: {len(scene.emitter.particles)}/{config.MAX_EFFECT_PARTICLES}",
            ]
            overlay_lines.extend(capture.overlay_lines())
            overlay.draw(screen, frame_time, config.FIXED_DT, extra_lines=overlay_lines)

        capture.update(screen, frame_time)
        pygame.display.flip()

    pygame.quit()
