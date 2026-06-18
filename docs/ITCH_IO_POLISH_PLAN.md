# Splashline Showdown Lean Itch.io Release Plan

## Goal

Ship Splashline Showdown as a small, complete, playable itch.io game without letting polish expand into a second project.

The release target is:

> A clean local arcade physics duel with a start menu, pause overlay, clear controls, powerup explanations, basic audio controls, stable match rules, and a downloadable build.

This plan intentionally avoids engine work, art overhauls, AI, replay systems, full settings persistence, and large UI frameworks.

## Product Scope

### Keep

- Current custom physics engine as-is.
- Current pygame rendering style.
- Current core gameplay loop.
- Local turn-based 1v1.
- Three-shot possession rule after final rule lock.
- Wind, particles, powerups, scoring, timer, and game-over state.
- Existing capture tools for screenshots/GIFs.

### Add

- Minimal overlay menu.
- Minimal pause overlay.
- How-to-play overlay.
- Powerups list overlay.
- Simple options overlay for audio levels and mute.
- Basic audio manager with a small set of sound effects.
- Final rule fix for ammo/turn clarity.
- Release packaging script.
- Player-facing README/build instructions.
- Clean repository state before release.

### Cut

- No engine refactor.
- No deep physics upgrades.
- No graphics overhaul.
- No new sprite pipeline.
- No title art requirement.
- No AI opponent for first release.
- No controller support for first release.
- No input rebinding for first release.
- No tutorial mode for first release.
- No replay/highlight system.
- No persistent settings unless it is trivial after options exist.
- No online multiplayer.
- No full scene manager.
- No ECS.

## Priority Legend

- P0: Required for first itch.io release.
- P1: Do only if P0 is finished and stable.
- P2: Post-release.

## Final P0 Release Scope

The game is ready for first itch.io release when:

- `python main.py splashline` launches the game.
- A minimal start overlay appears before gameplay begins.
- The player can start, pause, resume, restart, read controls, read powerups, change audio volume/mute, and exit.
- A full match can be completed from start to winner.
- Ammo/turn behavior is clear and does not silently reload in a confusing way.
- HUD shows only necessary match information during gameplay.
- Debug/performance overlay is hidden by default.
- Basic sound effects exist or the game degrades cleanly if audio files are missing.
- A Windows downloadable build exists.
- README explains source launch, packaged launch, controls, and powerups.
- Tests pass.
- Git status is clean before tagging/uploading.

## Recommended Implementation Order

```text
1. Lock final turn/ammo rule
2. Add lean overlay menu system
3. Add how-to-play and powerups overlays
4. Add minimal options overlay for audio
5. Add basic audio manager and core SFX
6. Hide/debug-separate nonessential overlays
7. Add build script and player README
8. Clean repo and capture final media
9. Run QA checklist
10. Upload to itch.io
```

## P0: Final Turn And Ammo Rule

### Objective

Remove the remaining rule confusion around ammo refilling and turn ownership.

### Current Code

- `game/state.py`: `TurnState`, `switch_turn`, `reset_rally`.
- `game/input.py`: `consume_shot_or_reject`, `try_fire_projectiles`, turn-cross helpers.
- `game/scene.py`: current shot firing and turn-switch orchestration.
- `game/physics.py`: `update_ball_side`.
- `tests/test_game_state.py`
- `tests/test_game_physics.py`

### Final Rule

Use a possession model:

1. The controlling player receives exactly 3 shots.
2. Shooting reduces ammo.
3. Reaching 0 ammo does not instantly refill.
4. Control switches and ammo refills when the ball clearly enters the opponent side.
5. If the controlling player has 0 ammo and the ball does not cross after a short failsafe window, control switches to prevent soft-locks.
6. After a point, the player who lost the point serves next.

### Implementation Steps

1. Update `TurnState` in `game/state.py`.
   - Add `awaiting_cross: bool = False`.
   - Add `out_of_ammo_timer: float = 0.0`.
   - Reset both in `reset_rally` and `switch_turn`.

2. Update `try_fire_projectiles` in `game/input.py`.
   - Keep it responsible for spawning and spending shots only.
   - When `shots_left` becomes `0`, set `turn.awaiting_cross = True`.
   - Do not call `switch_turn` from inside input helpers.

3. Update `SplashlineScene.step` in `game/scene.py`.
   - Remove immediate turn switch after `shots_left <= 0`.
   - Keep side-cross and side-sync logic as the normal switch path.
   - Add failsafe logic:
     - If `turn.awaiting_cross` is true, increment `out_of_ammo_timer`.
     - If the timer exceeds a config value such as `OUT_OF_AMMO_TURN_FAILSAFE = 4.0`, call `switch_turn`.
   - Reset timer when control switches or point scores.

4. Update HUD wording in `game/ui.py`.
   - Use "Control" instead of "Turn".
   - When ammo is 0, show a short phrase such as `Shots: 0`.
   - Keep the message compact.

5. Add regression tests.
   - Firing the third shot leaves ammo at 0 and does not refill immediately.
   - Ball crossing refills the opponent to 3.
   - Failsafe eventually switches control.

### Done When

- The player never sees ammo silently reload before possession changes.
- The defender gets control when the ball enters their side.
- A rally cannot stall forever because one player has no ammo.

## P0: Lean Overlay Menu System

### Objective

Add the smallest possible player-facing menu system without building a full scene framework.

### Current Code

- `game/scene.py`: owns `run()`, event loop, pause, restart, help, overlay.
- `game/ui.py`: owns drawing.

### Screens To Support

Use overlays, not separate full-screen scenes:

- `START`
- `PLAYING`
- `PAUSED`
- `HOW_TO_PLAY`
- `POWERUPS`
- `OPTIONS`
- `GAME_OVER`

### Implementation Steps

1. Add a small enum.
   - Create `game/screens.py`.
   - Add `ScreenMode` enum with the values above.
   - Add a minimal `MenuItem` dataclass if useful: `label`, `action`.

2. Update `run()` in `game/scene.py`.
   - Replace `paused = False` with `screen_mode = ScreenMode.START`.
   - Only call `scene.step(...)` when `screen_mode is ScreenMode.PLAYING`.
   - Continue drawing the arena/game behind overlays.
   - On start screen, draw the freshly initialized scene in the background but keep gameplay frozen.

3. Add menu state.
   - Track `selected_menu_index`.
   - Use `Up/Down` or `W/S` to move selection.
   - Use `Enter`, `Space`, or left click to activate.
   - Use `Esc` to go back or exit depending on screen.

4. Add start overlay.
   - Buttons:
     - Start
     - How To Play
     - Powerups
     - Options
     - Exit
   - Do not create a new visual art screen.
   - Draw a translucent panel over the game.

5. Add pause overlay.
   - Buttons:
     - Resume
     - Restart Match
     - How To Play
     - Powerups
     - Options
     - Exit To Desktop
   - `Esc` while playing opens pause.
   - `Esc` while paused resumes or returns to prior overlay.

6. Keep game-over simple.
   - Reuse existing `draw_game_over`.
   - Add options:
     - Restart
     - Main Menu
     - Exit

### Done When

- A player can operate the game without knowing keyboard debug shortcuts.
- Gameplay pauses whenever an overlay is open.

## P0: How-To-Play Overlay

### Objective

Explain the game in one readable overlay instead of a full tutorial.

### Current Code

- `game/ui.py::draw_help` already has basic controls text.

### Implementation Steps

1. Replace or reuse `draw_help`.
   - Rename to `draw_how_to_play_overlay` or keep `draw_help` but make it menu-quality.

2. Include only essential text.
   - Objective: score by making the ball hit water on the opponent side.
   - Move: `A/D` or arrow keys.
   - Aim: mouse.
   - Shoot: left click.
   - Ammo: 3 shots per possession.
   - Control changes when the ball crosses sides.
   - Pause: `Esc`.

3. Keep text short.
   - Use 5-8 lines maximum.
   - Avoid explaining implementation details.

4. Add a Back option.
   - From start menu, Back returns to start.
   - From pause menu, Back returns to pause.

### Done When

- A new player can understand the match without opening README.

## P0: Powerups Overlay

### Objective

List every powerup and what it does.

### Current Code

- `game/powerups.py`: `PowerupKind`, labels, effect behavior.
- `game/ui.py`: powerup drawing.

### Implementation Steps

1. Add `draw_powerups_overlay` in `game/ui.py`.

2. Pull names from `PowerupKind.label()`.
   - Heavy Shot: next shot is heavier and faster.
   - Double Shot: next shot fires two projectiles.
   - Null Wind: temporarily cancels wind.

3. Show activation rule.
   - Ball or projectile touching a pickup activates it.
   - Projectile pickups belong to the projectile owner.
   - Ball pickup ownership should match the final rule decided in the turn/ammo task.

4. Add a Back option.

### Done When

- Players can understand powerups before entering a match.

## P0: Minimal Options Overlay

### Objective

Provide only options that matter for a small itch.io release.

### Current Code

- No settings module exists.
- No audio manager exists.

### Options To Include

- SFX volume.
- Music volume, only if music is added.
- Mute.
- Debug overlay toggle, optional and hidden from normal players if preferred.

### Implementation Steps

1. Add a small runtime settings dataclass.
   - Create `game/settings.py`.
   - Add `sfx_volume: float = 0.8`.
   - Add `music_volume: float = 0.5`.
   - Add `muted: bool = False`.
   - Do not add persistence for first release unless it takes very little time.

2. Initialize settings in `game/scene.py`.
   - Create settings once in `run()`.
   - Pass settings to audio and options drawing.

3. Add `draw_options_overlay` in `game/ui.py`.
   - Use left/right keys to adjust volume.
   - Use Enter/Space to toggle mute.
   - Keep it text-based.

4. Wire menu input.
   - Up/Down selects row.
   - Left/Right adjusts volume.
   - Enter toggles mute or Back.

### Done When

- The player can lower or mute audio from inside the game.

## P0: Basic Audio

### Objective

Add enough sound to make the game feel responsive without building a large audio system.

### Current Code

- No audio module.
- `game/scene.py` knows when shots fire, impacts happen, powerups collect, points score, and match ends.

### Required Sounds

Minimum viable set:

- Menu select.
- Shot fired.
- Ball hit.
- Splash/point.
- Powerup collect.
- Match over.

Optional:

- Short music loop or beach ambience.

### Implementation Steps

1. Create `game/audio.py`.
   - Add `AudioManager`.
   - Methods:
     - `load()`
     - `play(name)`
     - `set_sfx_volume(value)`
     - `set_music_volume(value)`
     - `set_muted(enabled)`
   - Missing files must not crash the game.

2. Add audio assets folder.
   - Use `assets/audio/`.
   - Use only licensed or self-made sounds.
   - Keep filenames simple: `shot.wav`, `hit.wav`, `splash.wav`, `powerup.wav`, `menu.wav`, `match_over.wav`.

3. Trigger sounds in `game/scene.py`.
   - On successful projectile spawn: `shot`.
   - On projectile-ball impact: `hit`.
   - On water contact/point: `splash`.
   - When `collect_powerups` returns collected items: `powerup`.
   - When match enters game over: `match_over`.
   - On menu selection: `menu`.

4. Add simple spam protection.
   - In `AudioManager`, track short cooldowns per sound name.
   - Prevent `hit` and `splash` from playing every fixed step.

5. Connect options.
   - Apply `settings.sfx_volume`.
   - Apply mute.

### Done When

- The game has basic feedback and still launches if audio assets are missing.

## P0: HUD And Debug Cleanup

### Objective

Keep gameplay readable and remove demo clutter from the default experience.

### Current Code

- `game/ui.py::draw_hud` always draws score/timer/turn/wind/effects.
- `game/scene.py` defaults `show_help = True` and `show_overlay = True`.

### Implementation Steps

1. Change defaults in `game/scene.py`.
   - `show_help = False`.
   - `show_overlay = False`.

2. Keep one compact gameplay HUD.
   - Score.
   - Timer.
   - Control player.
   - Shots.
   - Wind.
   - Active powerups, compact text is acceptable.

3. Move controls into How-To-Play overlay.
   - Do not show help by default.
   - `H` can still open the How-To-Play overlay.

4. Keep debug overlay available.
   - `O` can still toggle FPS/projectiles/particles/capture.
   - Do not advertise debug overlay heavily in player-facing UI.

### Done When

- Default gameplay looks like a game, not a demo diagnostics screen.

## P0: Build And Player README

### Objective

Produce a downloadable Windows build and clear player instructions.

### Current Code

- `main.py` launches demos.
- `requirements.txt` contains pygame and Pillow.
- No build script exists.

### Implementation Steps

1. Add `requirements-dev.txt`.
   - Include PyInstaller.
   - Keep `requirements.txt` runtime-only.

2. Add `build_release.ps1`.
   - Run tests.
   - Run compileall with redirected cache if needed.
   - Build with PyInstaller.
   - Copy README/player instructions.
   - Zip output folder.

3. Add a simple release entry option.
   - Either package `main.py` and document launching the splashline mode.
   - Or add a tiny release launcher file that calls `main(["splashline"])`.

4. Add `release/README_PLAYER.txt`.
   - What the game is.
   - How to run.
   - Controls.
   - Powerups.
   - Credits/licenses.

5. Update root README.
   - Source run command.
   - Build command.
   - Link to itch.io once published.

### Done When

- A player can download, unzip, and run without installing Python.

## P0: Repository Cleanup

### Objective

Make the project presentable before publishing or sending to recruiters.

### Current State To Address

- `demos/rigidbody_cube_demo.py` may show modified due to line-ending/index noise.
- Several timestamped capture files may be untracked.
- Generated local folders such as `__pycache__/` and `.tmp_pypdf/` should not be part of release.

### Implementation Steps

1. Decide curated media.
   - Keep only final screenshots/GIFs used by README or itch.
   - Ignore raw timestamp captures.

2. Update `.gitignore` if needed.
   - Ignore raw capture folders.
   - Keep generated caches ignored.

3. Resolve line-ending noise.
   - Add `.gitattributes` if needed.
   - Normalize tracked files carefully.

4. Clean local generated files.
   - Remove ignored caches locally before final status check.

5. Final verification.
   - Run tests.
   - Run compileall.
   - Confirm `git status --short` is clean.

### Done When

- The repo is clean and release-ready.

## P0: Minimal QA Checklist

### Objective

Catch release-breaking issues without building a huge QA process.

### Implementation Steps

Create `docs/RELEASE_QA_CHECKLIST.md` with these checks:

- Launch from source.
- Launch packaged build.
- Start match from menu.
- Open How To Play.
- Open Powerups.
- Change/mute audio.
- Pause and resume.
- Restart match.
- Complete match by score cap.
- Complete or test timer end.
- Confirm ammo does not silently reload.
- Collect each powerup at least once.
- Toggle debug overlay.
- Quit cleanly.
- Run for 10 minutes without crash.
- Confirm README instructions match the build.

### Done When

- Every release candidate can be tested the same way.

## P1: Small Visual Cleanups Only

Do not do a graphics overhaul.

Allowed if P0 is done:

- Improve HUD spacing.
- Make menu panels cleaner.
- Make powerup colors more readable.
- Add one small visual cue for selected menu item.
- Add a slightly better title text treatment using pygame fonts.

Avoid:

- New sprite pipeline.
- Complex animations.
- New background art requirement.
- Big palette redesign.
- Camera systems.
- Screen shake.
- Hit-stop.

## P1: Simple Balance Pass

### Objective

Tune only the variables that affect fairness and clarity.

### Files

- `game/config.py`

### Tune Only

- `PROJECTILE_SPEED`
- `PROJECTILE_MASS`
- `SHOT_COOLDOWN`
- `BALL_MASS`
- `BALL_RESTITUTION`
- `WIND_MIN_FORCE`
- `WIND_MAX_FORCE`
- `POWERUP_SPAWN_MIN`
- `POWERUP_SPAWN_MAX`
- `MATCH_DURATION`
- `SCORE_CAP`

### Process

1. Play 5 no-powerup matches if you add a debug way to disable powerups.
2. Play 5 normal matches.
3. Change only one group of values at a time.
4. Stop tuning once the game feels fair enough.

### Done When

- Rallies are usually readable and not dominated by wind or powerups.

## P1: Final Itch Media

### Objective

Produce enough page assets to publish.

### Required

- 3 screenshots.
- 1 short gameplay GIF.
- Short page description.
- Controls section.
- Powerups section.
- Credits/license section.

### Implementation

1. Use existing `CaptureController`.
2. Capture after menus/HUD are finished.
3. Keep only curated media in the repo.
4. Put raw media outside tracked files or in an ignored folder.

## P2: Post-Release Ideas

Only consider after first release:

- CPU opponent.
- Controller support.
- Input remapping.
- Persistent settings.
- Tutorial mode.
- Improved art.
- More powerups.
- Replay/highlight system.
- Larger engine cleanup.

## Lean Sprint Plan

### Sprint 1: Rules And Menus

Tasks:

1. Fix final turn/ammo rule.
2. Add `game/screens.py`.
3. Add start overlay.
4. Add pause overlay.
5. Add how-to-play overlay.
6. Add powerups overlay.

Done when:

- The game feels like it has a real beginning and pause flow.

### Sprint 2: Audio And Options

Tasks:

1. Add `game/settings.py`.
2. Add options overlay.
3. Add `game/audio.py`.
4. Add minimal sound effects.
5. Wire volume/mute.

Done when:

- The game has basic feedback and player-controlled audio.

### Sprint 3: Release Build

Tasks:

1. Hide debug/help overlays by default.
2. Add player README.
3. Add build script.
4. Build packaged release.
5. Run QA checklist.
6. Capture final media.
7. Clean repo.

Done when:

- A zip is ready to upload to itch.io.

## Final Release Checklist

- Start overlay exists.
- Pause overlay exists.
- How-To-Play overlay exists.
- Powerups overlay exists.
- Options overlay exists.
- Audio can be muted/lowered.
- Full match works.
- Ammo rule is clear.
- Three powerups work.
- Debug overlay hidden by default.
- Source launch works.
- Packaged build works.
- README is accurate.
- QA checklist passes.
- Git status is clean.

## Portfolio Framing

Use this project as a finished-product story:

> Built a custom Python/pygame physics sandbox, then shipped Splashline Showdown as a lean arcade physics game using that engine. The final release includes fixed-timestep rigid-circle gameplay, particles, wind, powerups, scoring, menus, audio controls, tests, packaging, and itch.io-ready documentation.

This is stronger than claiming the physics engine is a commercial-grade engine. It is honest, complete, and easy to verify.

