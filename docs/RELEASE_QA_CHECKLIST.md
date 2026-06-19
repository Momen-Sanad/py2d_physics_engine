# Splashline Showdown Release QA Checklist

Build/date:

Tester:

## Source Launch

- [ ] `python main.py splashline` launches.
- [ ] Start menu appears before gameplay advances.
- [ ] Local 1v1 begins a match.
- [ ] Vs CPU begins a match.
- [ ] Esc pauses during gameplay.
- [ ] Pause Resume returns to gameplay.
- [ ] Pause Restart starts a fresh match.
- [ ] Pause Exit closes the game.

## Overlays

- [ ] How To Play opens from start menu.
- [ ] How To Play opens with `H`.
- [ ] Powerups opens from start menu.
- [ ] Options opens from start menu.
- [ ] Tutorial opens from start menu.
- [ ] Tutorial Start Practice begins a CPU match.
- [ ] SFX volume changes with Left/Right.
- [ ] Mute toggles with Enter.
- [ ] Controls menu opens from Options.
- [ ] Move Left, Move Right, and Fire Key can be rebound.
- [ ] Reset Defaults restores movement to A/D and fire to F.
- [ ] Back returns to the previous menu.

## Gameplay

- [ ] A full match can be completed.
- [ ] Ammo reaches 0 without instantly refilling.
- [ ] Control changes when the ball crosses sides.
- [ ] Out-of-ammo failsafe eventually changes control.
- [ ] CPU controls only the right player during Vs CPU.
- [ ] Heavy Shot can be collected and used.
- [ ] Double Shot can be collected and used.
- [ ] Quick Shot can be collected and used.
- [ ] Null Wind can be collected and used.
- [ ] Sticky Ball can be collected and used.
- [ ] Game-over menu appears after a winner is decided.
- [ ] Game-over Restart works.
- [ ] Game-over Main Menu works.

## Release Build

- [ ] `build_release.ps1` completes.
- [ ] Packaged `SplashlineShowdown.exe` launches.
- [ ] Packaged build includes `release/README_PLAYER.txt`.
- [ ] Packaged build can complete one match.
- [ ] `dist/SplashlineShowdown.zip` exists.

## Final Repo

- [ ] `python -m unittest discover -s tests` passes.
- [ ] Compile check passes with redirected cache.
- [ ] README instructions match the current game.
- [ ] SFX volume, mute, bindings, and tutorial progress persist after relaunch.
- [ ] `git status --short` is clean.
