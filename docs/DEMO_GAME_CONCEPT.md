# Required Demo Game Concept

## Working Title
2D Physics Beach Ball Duel (1v1)

## Pitch
A 1v1 physics arcade game where each player uses a projectile gun to strike an air-filled beach ball over a net. Wind and optional damping randomness make trajectories non-memorizeable. The ball drips water particles and its drip state influences shot behavior. The rally is turn-based, and points are scored when the ball hits the water level.

## Core Gameplay Idea

- Match format: 1v1.
- Objective: win more rally points than the opponent before time ends or score cap is reached.
- Interaction rule: players can only influence the ball using shot projectiles.
- Turn system: active player gets 1-2 shots per turn.
- Turn switch: switch immediately when the active player uses all shots, or when the ball crosses the net to the opponent side.
- Anti-memorization: wind is randomized over time and damping can optionally be randomized.
- Match pacing: random airborne powerups alter tempo and tactical options.

## Physics Design Decision (Locked)

- Ball: rigid circle with soft-contact tuning to mimic an air-filled ball.
- Shots: rigid circles for reliable aiming and consistent hit feedback.
- Theme: beach ball (better fit than stiff water polo ball for windy, bouncy gameplay).
- Soft-contact behavior comes from tuning restitution, damping, and drag, not from full mass-spring deformation.

## Player Controls

- `A / D` or `Left / Right`: move horizontally.
- `Mouse`: aim gun direction.
- `Left Click`: shoot rigid circle projectile.
- (Optional) `Space`: quick hop/dash.

## Physics Systems Used

### 1. Rigid Body Dynamics

- Beach ball is simulated as a rigid circle.
- Projectiles are rigid circles.
- Net, side walls, and bounds use collision handling/constraints.
- Impulse response controls redirects, rebounds, and shot quality.

### 2. Random Wind (Required)

- Time-varying horizontal force applied to ball and projectiles.
- Wind can change in intervals or with smooth interpolation.
- HUD displays direction and strength.

### 3. Random Damping (Optional Mode)

- Standard mode: fixed damping.
- Chaos mode: damping sampled per rally or per time window from safe ranges.

### 4. Water Drip Effect on Ball

- Ball emits particle drips.
- Drip intensity modifies gameplay through tuned physics parameters.
- Candidate effects: increased drag, reduced energy transfer, temporary heavier-feel motion.

### 5. Particle System

- Drip trail from ball.
- Optional splash bursts on strong collisions and water contact.

## Turn + Shot Rules

- Each turn starts with 1 or 2 available shots.
- Active player may shoot until shot count is exhausted.
- Turn may end early if ball crosses the net to opponent territory.
- Cooldown limits spam within a turn.
- Projectile lifetime is limited.
- Direct player-ball collision can be disabled to preserve projectile-first gameplay.

## Powerup System

Powerups spawn randomly in the air. Collected powerups apply temporary effects.

### Example Powerup Pool

- `Heavy Shot`: higher projectile mass/impulse.
- `Rapid Fire`: shorter shot cooldown.
- `Curve Wind`: temporary wind amplification.
- `Sticky Ball`: temporary increase in ball damping.
- `Slipstream`: lower movement friction, faster horizontal control.
- `Shield Ring`: absorbs one opponent projectile impact.
- `Double Shot`: fires two projectiles with small spread.
- `Water Burst`: increases drip intensity and drag effect.
- `Null Wind`: temporary wind cancel.
- `Rebound Core`: boosts wall restitution for your shots.

## Match Flow

1. Rally starts with ball at center.
2. Player 1 turn starts (1-2 shots available).
3. Turn switches when shots are spent or ball crosses net.
4. Player 2 turn follows with the same rules.
5. Rally ends when ball touches water level.
6. Point is awarded.
7. Ball and players reset for next rally.
8. Match ends by timer or score cap.

## Scoring and Win Conditions

- Rally point scoring: 1 point whenever ball hits water level.
- Recommended rule: point is awarded to the player opposite the side where the ball touches water.
- Winner: highest score at timer end, or first to score cap.
- Tie handling: sudden death or draw.

## Visual/UI Requirements

- Scoreboard and timer.
- Turn indicator and shots-left counter.
- Wind indicator (direction and strength).
- Optional damping mode indicator.
- Water-level line marker for clear scoring trigger.
- Powerup indicator and active effect timers.
- Impact/splash particle feedback.

## Technical Scope (MVP vs Stretch)

### MVP (Submission-Safe)

- 1v1 playable loop.
- Horizontal movement, mouse aim, and shooting.
- Turn system with 1-2 shots per turn.
- Ball/projectile rigid-body collisions.
- Random wind.
- Water-level scoring and rally reset.
- At least 3 powerups.
- Timer and final winner state.

### Stretch Goals

- Optional random damping mode toggle.
- Charge shot + recoil tuning.
- Better single-player AI fallback.
- Replay camera or highlight clips.

## Balancing Notes

- Clamp wind and damping to fairness ranges.
- Keep shot cooldown short enough for responsiveness.
- Limit active powerup stacking.
- Keep powerup durations short and readable.

## Risks and Mitigations

- Risk: chaos becomes unreadable. Mitigation: strong HUD indicators and capped randomness.
- Risk: projectile spam dominates. Mitigation: cooldown + lifetime + optional ammo cap per turn.
- Risk: powerups overshadow skill. Mitigation: low spawn rate and short durations.