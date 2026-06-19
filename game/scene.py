"""Playable pygame scene for Splashline Showdown."""

from __future__ import annotations

from random import Random

from engine.broadphase import SpatialHashGrid
from engine.core import SimulationClock
from engine.debug import PerformanceOverlay
from engine.forces import drag_force
from engine.math2d import Vec2

from media_capture import CaptureController

from . import config
from .ai import CpuController
from .audio import AudioManager
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
    can_fire_projectile,
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
    sticky_ball_drag_bonus,
    tick_pickups,
)
from .screens import MenuAction, MenuItem, ScreenMode, clamp_menu_index
from .settings import load_settings, save_settings
from .state import MatchPhase, MatchState, PlayerId, award_point, reset_rally, start_match, switch_turn, tick_match_timer
from .ui import (
    draw_arena,
    draw_ball,
    draw_controls_overlay,
    draw_game_over_menu_overlay,
    draw_how_to_play_overlay,
    draw_hud,
    draw_options_overlay,
    draw_particles,
    draw_pause_overlay,
    draw_players,
    draw_powerups,
    draw_powerups_overlay,
    draw_projectiles,
    draw_start_overlay,
    draw_tutorial_overlay,
    draw_wind_background,
)
from .ui_effects import UiConfetti, draw_ui_confetti, spawn_victory_confetti, step_ui_confetti


START_MENU = [
    MenuItem("Local 1v1", MenuAction.START_GAME),
    MenuItem("Vs CPU", MenuAction.START_CPU),
    MenuItem("Tutorial", MenuAction.TUTORIAL),
    MenuItem("How To Play", MenuAction.HOW_TO_PLAY),
    MenuItem("Powerups", MenuAction.POWERUPS),
    MenuItem("Options", MenuAction.OPTIONS),
    MenuItem("Exit", MenuAction.EXIT),
]
PAUSE_MENU = [
    MenuItem("Resume", MenuAction.RESUME),
    MenuItem("Restart Match", MenuAction.RESTART),
    MenuItem("Main Menu", MenuAction.MAIN_MENU),
    MenuItem("Tutorial", MenuAction.TUTORIAL),
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
OPTIONS_MENU = [
    MenuItem("SFX Volume", MenuAction.SFX_VOLUME),
    MenuItem("Mute", MenuAction.MUTE),
    MenuItem("Controls", MenuAction.CONTROLS),
    MenuItem("Back", MenuAction.BACK),
]
CONTROLS_MENU = [
    MenuItem("Move Left", MenuAction.REMAP_LEFT),
    MenuItem("Move Right", MenuAction.REMAP_RIGHT),
    MenuItem("Fire Key", MenuAction.REMAP_FIRE),
    MenuItem("Reset Defaults", MenuAction.RESET_BINDINGS),
    MenuItem("Back", MenuAction.BACK),
]
BACK_MENU = [MenuItem("Back", MenuAction.BACK)]
TUTORIAL_PAGES = [
    (
        "Goal And Scoring",
        [
            "Knock the beach ball into the opponent water.",
            "The side where the ball splashes gives up the point.",
            "First to the score cap wins before time runs out.",
        ],
    ),
    (
        "Move, Aim, Shoot",
        [
            "Move the controlling player with your bound keys.",
            "Aim with the mouse toward the beach ball.",
            "Shoot with left click or your bound fire key.",
        ],
    ),
    (
        "Possession",
        [
            "Each possession gets exactly 3 shots.",
            "Ammo refills only when control changes.",
            "Control changes when the ball clearly crosses the net.",
        ],
    ),
    (
        "Wind And Powerups",
        [
            "Wind bends shots and the ball, so watch the HUD.",
            "Pickups activate when hit by the ball or a projectile.",
            "Practice mode starts a match against the CPU.",
        ],
    ),
]


def logical_viewport(display_size: tuple[int, int]) -> tuple[int, int, int, int]:
    """Return the stretched fullscreen viewport for the fixed logical canvas."""

    display_width, display_height = display_size
    return (0, 0, max(1, display_width), max(1, display_height))


def display_to_logical_mouse(
    mouse_pos: tuple[int, int],
    viewport: tuple[int, int, int, int],
) -> tuple[int, int]:
    """Map fullscreen display mouse coordinates into logical game coordinates."""

    viewport_x, viewport_y, viewport_width, viewport_height = viewport
    logical_x = (mouse_pos[0] - viewport_x) * config.WINDOW_WIDTH / viewport_width
    logical_y = (mouse_pos[1] - viewport_y) * config.WINDOW_HEIGHT / viewport_height
    return (
        int(min(max(logical_x, 0.0), config.WINDOW_WIDTH - 1)),
        int(min(max(logical_y, 0.0), config.WINDOW_HEIGHT - 1)),
    )


def menu_items_for(screen_mode: ScreenMode) -> list[MenuItem]:
    """Return keyboard menu rows for the active overlay."""

    if screen_mode is ScreenMode.START:
        return START_MENU
    if screen_mode is ScreenMode.PAUSED:
        return PAUSE_MENU
    if screen_mode is ScreenMode.GAME_OVER:
        return GAME_OVER_MENU
    if screen_mode is ScreenMode.OPTIONS:
        return OPTIONS_MENU
    if screen_mode is ScreenMode.CONTROLS:
        return CONTROLS_MENU
    if screen_mode in {ScreenMode.HOW_TO_PLAY, ScreenMode.POWERUPS}:
        return BACK_MENU
    return []


def tutorial_menu_items(page_index: int) -> list[MenuItem]:
    """Return tutorial actions for the current page."""

    items: list[MenuItem] = []
    if page_index < len(TUTORIAL_PAGES) - 1:
        items.append(MenuItem("Next", MenuAction.TUTORIAL_NEXT))
    if page_index > 0:
        items.append(MenuItem("Previous", MenuAction.TUTORIAL_PREVIOUS))
    items.append(MenuItem("Start Practice", MenuAction.START_PRACTICE))
    items.append(MenuItem("Back", MenuAction.BACK))
    return items


class SplashlineScene:
    """Owns the full match, entities, effects, and gameplay loop state."""

    def __init__(self, cpu_enabled: bool = False) -> None:
        self.cpu_enabled = cpu_enabled
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
        self.turn_side_sync_guard = 0.0
        self.audio_events: list[str] = []
        self.match_over_audio_sent = False
        self.cpu = CpuController() if cpu_enabled else None
        self.last_cpu_input = InputState(0.0, Vec2(self.arena.net_x, self.arena.serve_y))
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
        self.match_over_audio_sent = False
        if self.cpu is not None:
            self.cpu.reset()
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
        self.turn_side_sync_guard = 0.0
        reset_wind(self.wind, self.rng)
        reset_rally(self.match, starting_player=starting_player)
        reset_ball(self.ball, self.arena, self.rng)

    def switch_control(self) -> PlayerId:
        """Switch active player control and prevent immediate side resync."""

        active_player = switch_turn(self.match)
        self.block_turn_side_sync()
        return active_player

    def block_turn_side_sync(self) -> None:
        """Briefly suppress side-sync so crossings do not bounce ownership."""

        self.allow_turn_side_sync = False
        self.turn_side_sync_guard = config.TURN_SIDE_SYNC_GUARD

    def drain_audio_events(self) -> list[str]:
        """Return and clear queued gameplay audio events."""

        events = self.audio_events[:]
        self.audio_events.clear()
        return events

    def queue_match_over_audio(self) -> None:
        """Queue match-over audio once per match."""

        if not self.match_over_audio_sent:
            self.audio_events.append("match_over")
            self.audio_events.append("victory")
            self.match_over_audio_sent = True

    def cpu_input(self, dt: float) -> InputState:
        """Return CPU input for this fixed step."""

        if self.cpu is None:
            return InputState(0.0, self.last_cpu_input.aim_world)

        self.last_cpu_input = self.cpu.build_input(
            self.right_player,
            self.ball,
            self.match.turn,
            self.arena,
            len(self.projectiles),
            dt,
        )
        return self.last_cpu_input

    def step(self, input_state: InputState, dt: float) -> None:
        """Advance gameplay by one fixed update step."""

        self.match.turn.cooldown_remaining = max(0.0, self.match.turn.cooldown_remaining - dt)
        expire_effects(self.active_effects, dt, self.match.players())
        tick_pickups(self.pickups, dt)
        if self.turn_side_sync_guard > 0.0:
            self.turn_side_sync_guard = max(0.0, self.turn_side_sync_guard - dt)
        if self.turn_side_sync_guard <= 0.0:
            self.allow_turn_side_sync = True

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
            self.queue_match_over_audio()
            step_effect_particles(self.emitter, dt, effective_wind_x)
            return

        update_wind(self.wind, dt, self.rng)
        effective_wind_x = apply_active_effects(self.active_effects, self.wind.current_force_x)

        active_player = self.match.player(self.match.turn.active_player)
        update_player_movement(active_player, input_state, dt)

        projectile_budget = config.MAX_PROJECTILES - len(self.projectiles)
        if can_fire_projectile(input_state, self.match.turn, projectile_budget):
            modifiers = pop_fire_modifiers(self.active_effects, active_player.player_id, self.match.players())
            spawned = try_fire_projectiles(
                active_player,
                input_state,
                self.match.turn,
                self.arena,
                fire_count=modifiers.projectile_count,
                speed_scale=modifiers.speed_scale,
                mass_scale=modifiers.mass_scale,
                cooldown_scale=modifiers.cooldown_scale,
                projectile_budget=projectile_budget,
            )
            if spawned:
                self.block_turn_side_sync()
                self.projectiles.extend(spawned)
                self.audio_events.append("shot")

        self.powerup_spawn_timer -= dt
        if self.powerup_spawn_timer <= 0.0:
            spawn_powerup(self.rng, self.arena, self.pickups)
            self.powerup_spawn_timer = self.rng.uniform(config.POWERUP_SPAWN_MIN, config.POWERUP_SPAWN_MAX)

        self.ball.body.apply_force(
            drag_force(
                self.ball.body.velocity,
                config.BALL_DRIP_DRAG_BASE
                + config.BALL_DRIP_DRAG_BONUS * self.ball.drip_intensity
                + sticky_ball_drag_bonus(self.active_effects),
            )
        )
        apply_wind_to_bodies([self.ball.body, *(projectile.body for projectile in self.projectiles)], effective_wind_x)
        step_rigid_bodies(self.ball, self.projectiles, dt)
        resolve_net_collisions(self.ball, self.projectiles, self.arena)
        impact_speed = resolve_projectile_collisions(self.ball, self.projectiles, self.broadphase)
        update_drip_intensity(self.ball, impact_speed, dt)
        if impact_speed > 0.0:
            self.audio_events.append("hit")
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

        collected_powerups = collect_powerups(
            self.ball,
            self.projectiles,
            self.pickups,
            self.active_effects,
            self.match.turn.active_player,
            self.match.players(),
        )
        if collected_powerups:
            self.audio_events.append("powerup")
        emit_ball_drips(self.ball, self.emitter, effective_wind_x, self.rng, dt)
        step_effect_particles(self.emitter, dt, effective_wind_x)

        if self.ball.touched_water:
            self.audio_events.append("splash")
            spawn_splash_burst(self.emitter, self.ball.body.position, effective_wind_x, self.rng, count=20)
            award_point(
                self.match,
                water_side=ball_water_side(self.ball, self.arena),
                last_side=self.ball.last_side,
            )
            if self.match.phase is MatchPhase.GAME_OVER:
                self.queue_match_over_audio()
            self.round_reset_timer = config.ROUND_RESET_DELAY


def run() -> None:
    """Run the interactive Splashline Showdown pygame scene."""

    import pygame

    settings = load_settings()
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
    pygame.init()
    display_info = pygame.display.Info()
    display_size = (
        display_info.current_w or config.WINDOW_WIDTH,
        display_info.current_h or config.WINDOW_HEIGHT,
    )
    display = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
    screen = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT)).convert()
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=config.FIXED_DT, max_substeps=config.MAX_SUBSTEPS)
    overlay = PerformanceOverlay(font_size=20)
    capture = CaptureController(demo_name="splashline_showdown")
    audio = AudioManager()
    audio.load()
    audio.set_sfx_volume(settings.effective_sfx_volume())
    audio.set_muted(settings.muted)

    fonts = {
        "title": pygame.font.Font(None, 48),
        "body": pygame.font.Font(None, 28),
        "small": pygame.font.Font(None, 23),
    }

    scene = SplashlineScene()
    ui_confetti = UiConfetti()
    screen_mode = ScreenMode.START
    return_mode = ScreenMode.START
    selected_index = 0
    remap_action: MenuAction | None = None
    tutorial_page = 0
    show_overlay = False
    running = True

    def apply_audio_settings() -> None:
        audio.set_sfx_volume(settings.effective_sfx_volume())
        audio.set_muted(settings.muted)
        save_settings(settings)

    def set_screen(next_mode: ScreenMode) -> None:
        nonlocal screen_mode, selected_index, remap_action

        previous_mode = screen_mode
        screen_mode = next_mode
        selected_index = 0
        remap_action = None
        if next_mode is ScreenMode.GAME_OVER and previous_mode is not ScreenMode.GAME_OVER:
            spawn_victory_confetti(ui_confetti, scene.rng)
        elif previous_mode is ScreenMode.GAME_OVER and next_mode is not ScreenMode.GAME_OVER:
            ui_confetti.clear()

    def bind_key(action: MenuAction, key_name: str) -> None:
        if action is MenuAction.REMAP_LEFT:
            settings.bindings.move_left = key_name
        elif action is MenuAction.REMAP_RIGHT:
            settings.bindings.move_right = key_name
        elif action is MenuAction.REMAP_FIRE:
            settings.bindings.fire = key_name
        save_settings(settings)

    def handle_menu_action(action: MenuAction) -> None:
        nonlocal return_mode, running, scene, remap_action, tutorial_page

        audio.play("menu")
        if action is MenuAction.START_GAME:
            ui_confetti.clear()
            scene = SplashlineScene()
            set_screen(ScreenMode.PLAYING)
        elif action is MenuAction.START_CPU:
            ui_confetti.clear()
            scene = SplashlineScene(cpu_enabled=True)
            set_screen(ScreenMode.PLAYING)
        elif action is MenuAction.RESUME:
            set_screen(ScreenMode.PLAYING)
        elif action is MenuAction.RESTART:
            ui_confetti.clear()
            scene = SplashlineScene(cpu_enabled=scene.cpu_enabled)
            set_screen(ScreenMode.PLAYING)
        elif action is MenuAction.HOW_TO_PLAY:
            return_mode = screen_mode
            set_screen(ScreenMode.HOW_TO_PLAY)
        elif action is MenuAction.TUTORIAL:
            return_mode = screen_mode
            tutorial_page = 0
            set_screen(ScreenMode.TUTORIAL)
        elif action is MenuAction.TUTORIAL_NEXT:
            tutorial_page = min(len(TUTORIAL_PAGES) - 1, tutorial_page + 1)
            selected_index = 0
        elif action is MenuAction.TUTORIAL_PREVIOUS:
            tutorial_page = max(0, tutorial_page - 1)
            selected_index = 0
        elif action is MenuAction.START_PRACTICE:
            settings.tutorial_seen = True
            save_settings(settings)
            ui_confetti.clear()
            scene = SplashlineScene(cpu_enabled=True)
            set_screen(ScreenMode.PLAYING)
        elif action is MenuAction.POWERUPS:
            return_mode = screen_mode
            set_screen(ScreenMode.POWERUPS)
        elif action is MenuAction.OPTIONS:
            return_mode = screen_mode
            set_screen(ScreenMode.OPTIONS)
        elif action is MenuAction.CONTROLS:
            return_mode = screen_mode
            set_screen(ScreenMode.CONTROLS)
        elif action in {MenuAction.REMAP_LEFT, MenuAction.REMAP_RIGHT, MenuAction.REMAP_FIRE}:
            remap_action = action
        elif action is MenuAction.RESET_BINDINGS:
            settings.reset_bindings()
            save_settings(settings)
        elif action is MenuAction.MAIN_MENU:
            ui_confetti.clear()
            scene = SplashlineScene()
            set_screen(ScreenMode.START)
        elif action is MenuAction.SFX_VOLUME:
            settings.adjust_sfx_volume(0.1)
            apply_audio_settings()
        elif action is MenuAction.MUTE:
            settings.toggle_muted()
            apply_audio_settings()
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
            ui_confetti.clear()
            scene = SplashlineScene()
            set_screen(ScreenMode.START)
        else:
            set_screen(return_mode)

    while running:
        frame_time = min(clock.tick(config.RENDER_FPS) / 1000.0, 0.25)
        audio.step(frame_time)
        step_ui_confetti(ui_confetti, frame_time)
        events = list(pygame.event.get())
        viewport = logical_viewport(display.get_size())
        mouse_pos = display_to_logical_mouse(pygame.mouse.get_pos(), viewport)

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if remap_action is not None:
                    if event.key == pygame.K_ESCAPE:
                        remap_action = None
                    else:
                        key_name = pygame.key.name(event.key).lower()
                        if key_name:
                            bind_key(remap_action, key_name)
                        remap_action = None
                    audio.play("menu")
                    continue
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
                    ui_confetti.clear()
                    scene = SplashlineScene(cpu_enabled=scene.cpu_enabled)
                    set_screen(ScreenMode.PLAYING)
                elif screen_mode is not ScreenMode.PLAYING:
                    items = tutorial_menu_items(tutorial_page) if screen_mode is ScreenMode.TUTORIAL else menu_items_for(screen_mode)
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_index = clamp_menu_index(selected_index - 1, len(items))
                        audio.play("menu")
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_index = clamp_menu_index(selected_index + 1, len(items))
                        audio.play("menu")
                    elif screen_mode is ScreenMode.OPTIONS and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        if items:
                            action = items[selected_index].action
                            direction = -1.0 if event.key == pygame.K_LEFT else 1.0
                            if action is MenuAction.SFX_VOLUME:
                                settings.adjust_sfx_volume(direction * 0.1)
                                apply_audio_settings()
                                audio.play("menu")
                            elif action is MenuAction.MUTE:
                                settings.toggle_muted()
                                apply_audio_settings()
                                audio.play("menu")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        if items:
                            handle_menu_action(items[selected_index].action)

        keys = pygame.key.get_pressed()
        frame_input = read_input(events, keys, mouse_pos, settings.bindings)
        aim_world = frame_input.aim_world

        if screen_mode is ScreenMode.PLAYING:
            fire_consumed = False
            for _ in range(simulation_clock.consume(frame_time)):
                if scene.cpu_enabled and scene.match.turn.active_player is PlayerId.RIGHT:
                    step_input = scene.cpu_input(config.FIXED_DT)
                    aim_world = step_input.aim_world
                else:
                    step_input = InputState(
                        move_axis=frame_input.move_axis,
                        aim_world=frame_input.aim_world,
                        fire_pressed=frame_input.fire_pressed and not fire_consumed,
                        hop_pressed=False,
                    )
                scene.step(step_input, config.FIXED_DT)
                for audio_event in scene.drain_audio_events():
                    audio.play(audio_event)
                fire_consumed = True
            if scene.match.phase is MatchPhase.GAME_OVER:
                set_screen(ScreenMode.GAME_OVER)

        draw_arena(screen, scene.arena)
        draw_wind_background(screen, scene.wind)
        draw_powerups(screen, scene.pickups)
        draw_players(
            screen,
            scene.match.players(),
            scene.match.turn.active_player,
            aim_world,
        )
        draw_particles(screen, scene.emitter)
        draw_projectiles(screen, scene.projectiles)
        draw_ball(screen, scene.ball)
        draw_hud(screen, fonts, scene.match, scene.wind, scene.active_effects)

        items = tutorial_menu_items(tutorial_page) if screen_mode is ScreenMode.TUTORIAL else menu_items_for(screen_mode)
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
            draw_options_overlay(screen, fonts, settings, items, selected_index)
        elif screen_mode is ScreenMode.CONTROLS:
            draw_controls_overlay(screen, fonts, settings, items, selected_index, remap_action)
        elif screen_mode is ScreenMode.TUTORIAL:
            title, lines = TUTORIAL_PAGES[tutorial_page]
            draw_tutorial_overlay(
                screen,
                fonts,
                title,
                lines,
                tutorial_page,
                len(TUTORIAL_PAGES),
                items,
                selected_index,
            )
        elif screen_mode is ScreenMode.GAME_OVER:
            draw_game_over_menu_overlay(screen, fonts, scene.match, items, selected_index)
            draw_ui_confetti(screen, ui_confetti)

        if show_overlay:
            overlay_lines = [
                f"Projectiles: {len(scene.projectiles)}/{config.MAX_PROJECTILES}",
                f"Particles: {len(scene.emitter.particles)}/{config.MAX_EFFECT_PARTICLES}",
            ]
            overlay_lines.extend(capture.overlay_lines())
            overlay.draw(screen, frame_time, config.FIXED_DT, extra_lines=overlay_lines)

        capture.update(screen, frame_time)
        viewport = logical_viewport(display.get_size())
        display.fill((0, 0, 0))
        scaled_frame = pygame.transform.smoothscale(screen, (viewport[2], viewport[3]))
        display.blit(scaled_frame, (viewport[0], viewport[1]))
        pygame.display.flip()

    save_settings(settings)
    pygame.quit()
