# Splashline Showdown Release QA Checklist

Build/date: June 19, 2026 - P2 release build with victory feedback

Tester: Codex automated verification and release smoke pass

## Source Launch

- [x] `python main.py splashline` launches.
- [x] Start menu appears before gameplay advances.
- [x] Local 1v1 begins a match.
- [x] Vs CPU begins a match.
- [x] Esc pauses during gameplay.
- [x] Pause Resume returns to gameplay.
- [x] Pause Restart starts a fresh match.
- [x] Pause Main Menu returns to mode select so Local 1v1 and Vs CPU can be switched.
- [x] Pause Exit closes the game.

## Overlays

- [x] How To Play opens from start menu.
- [x] How To Play opens with `H`.
- [x] Powerups opens from start menu.
- [x] Options opens from start menu.
- [x] Tutorial opens from start menu.
- [x] Tutorial Start Practice begins a CPU match.
- [x] SFX volume changes with Left/Right.
- [x] Mute toggles with Enter.
- [x] Controls menu opens from Options.
- [x] Move Left, Move Right, and Fire Key can be rebound.
- [x] Reset Defaults restores movement to A/D and fire to F.
- [x] Back returns to the previous menu.

## Gameplay

- [x] A full match can be completed.
- [x] Ammo reaches 0 without instantly refilling.
- [x] Control changes when the ball crosses sides.
- [x] Out-of-ammo failsafe eventually changes control.
- [x] CPU controls only the right player during Vs CPU.
- [x] Heavy Shot can be collected and used.
- [x] Double Shot can be collected and used.
- [x] Quick Shot can be collected and used.
- [x] Null Wind can be collected and used.
- [x] Sticky Ball can be collected and used.
- [x] Game-over menu appears after a winner is decided.
- [x] Game-over Restart works.
- [x] Game-over Main Menu works.

## Release Build

- [x] `build_release.ps1` completes.
- [x] Packaged `SplashlineShowdown.exe` launches.
- [x] Packaged build includes `release/README_PLAYER.txt`.
- [x] Packaged build can complete one match.
- [x] `dist/SplashlineShowdown.zip` exists.

## Final Repo

- [x] `python -m unittest discover -s tests` passes.
- [x] Compile check passes with redirected cache.
- [x] README instructions match the current game.
- [x] SFX volume, mute, bindings, and tutorial progress persist after relaunch.
- [x] `git status --short` is clean.
