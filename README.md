# 2D Physics Engine

A modular Python physics engine and simulation sandbox for building interactive 2D gameplay systems. The project is organized around reusable engine modules, deterministic fixed-timestep simulation, and runnable visual demos that validate each physics feature before it is integrated into a playable game.

The engine is primarily 2D, with a contained 3D rigid-body rotation demo used to demonstrate quaternion orientation, inertia tensors, and torque-driven angular motion.

## Highlights

- Fixed-timestep simulation loop with reusable timing and world-stepping utilities.
- Vector math, force accumulation, integration helpers, constraints, collisions, and broadphase acceleration.
- Interactive demos for particles, springs, pressure soft bodies, 2D rigid-body collisions, and 3D rigid-body rotation.
- Stdlib regression tests for rigid-body inertia, quaternion math, and angular dynamics.
- XML-style code comments across tracked Python files for function, parameter, return, and file-level documentation.
- Planned playable demo game: a 1v1 physics beach-ball duel using rigid bodies, wind, particles, powerups, and scoring.

## Current Status

| Area | Status | Notes |
|---|---|---|
| Engine core | Implemented | Fixed timestep, shared world stepping, math, forces, constraints, and integration helpers |
| Particle system | Implemented demo | Interactive emitter with gravity, damping, drag, wind, trails, bursts, color modes, and capture support |
| Mass-spring system | Implemented demo | Spring-net cloth-like scene using particles and damped springs |
| Pressure soft body | Implemented demo | Closed spring loop with pressure forces and boundary constraints |
| Rigid-body dynamics | Implemented demos | 2D circle collisions with broadphase plus a torque-driven cube rotation demo |
| 3D rotation support | Implemented | `Vec3`, `Mat3`, quaternions, rotation matrices, and common inertia tensor helpers |
| Tests | Implemented | Stdlib `unittest` coverage for rigid-body math and dynamics |
| PBD | Scaffolded | `engine/pbd.py` and `demos/pbd_demo.py` are placeholders |
| FK | Partially scaffolded | `engine/kinematics.py` contains forward-chain helper logic |
| IK | Planned | Solver and demo still pending |
| Demo game | Designed | Beach Ball Duel concept is documented; implementation is planned |

## Quick Start

### Requirements

- Python 3.10+
- `pip`

### Install

```bash
pip install -r requirements.txt
```

### Run

Launch the default demo:

```bash
python main.py
```

Run a specific demo:

```bash
python main.py particle
python main.py spring
python main.py softbody
python main.py rigidbody
python main.py rigidbody_cube
```

List available demos:

```bash
python main.py --help
```

### Test

```bash
python -m unittest discover -s tests
python -m compileall engine demos main.py media_capture.py tests
```

## Demo Game Concept

The planned playable integration is **2D Physics Beach Ball Duel**, a 1v1 arcade physics game where players use projectile shots to redirect an air-filled beach ball over a net.

Core idea:

- Players move horizontally, aim with the mouse, and fire rigid-body projectiles.
- The beach ball and shots use rigid circle dynamics with tuned restitution, damping, drag, and impulse response.
- Wind changes over time so trajectories stay dynamic rather than memorized.
- The ball emits water-drip particles, and drip intensity can influence drag or energy transfer.
- Rallies are turn-based: players have limited shots, turns can switch when the ball crosses the net, and points are scored when the ball hits the water level.
- Random airborne powerups can temporarily alter shot mass, cooldowns, wind, damping, shields, rebounds, or particle effects.

MVP target:

- 1v1 playable loop.
- Movement, aiming, shooting, turn management, and scoring.
- Rigid-body ball/projectile collisions.
- Random wind and clear HUD feedback.
- Water-level scoring and rally reset.
- At least three powerups.

The full concept is documented in [docs/DEMO_GAME_CONCEPT.md](docs/DEMO_GAME_CONCEPT.md).

## Demo Guide

### Particle Demo

Run:

```bash
python main.py particle
```

Features:

- Continuous emission and burst spawning.
- Gravity, damping, drag, and wind controls.
- Theme, color, draw-mode, trail, lifetime, and visual-scale controls.
- Screenshot and GIF capture support.

Key controls:

- `LMB`: move emitter
- `X`: burst
- `Space`: pause/resume
- `R`: reset
- `E`: emitter mode
- `C`: color mode
- `V`: draw mode
- `B`: background theme
- `T`: trails
- `H`: help panel
- `G`: gravity
- `D`: linear damping
- `F`: drag
- `W`: wind
- `Esc`: quit

### Spring Demo

Run:

```bash
python main.py spring
```

Features:

- Pinned spring-net scene.
- Damped springs and particle integration.
- Boundary constraints and reset/pause controls.

Controls:

- `R`: reset
- `Space`: pause/resume
- `Esc`: quit

### Soft Body Demo

Run:

```bash
python main.py softbody
```

Features:

- Pressure-based soft body built from particles and perimeter springs.
- Area-derived pressure force.
- Boundary constraints and reset/pause controls.

Controls:

- `R`: reset
- `Space`: pause/resume
- `Esc`: quit

### Rigid Body Demo

Run:

```bash
python main.py rigidbody
```

Features:

- Hundreds of circle bodies.
- Fixed-timestep rigid-body stepping.
- Circle-circle collision response.
- Spatial hash broadphase.
- Sleeping and wakeup behavior for resting bodies.

Controls:

- `R`: reset
- `Space`: pause/resume
- `Esc`: quit

### Rigid Body Cube Demo

Run:

```bash
python main.py rigidbody_cube
```

Features:

- Torque-driven wireframe cube.
- Solid-cube inertia tensor.
- Angular momentum and Newton-Euler rotation.
- Semi-implicit angular integration.
- Quaternion orientation normalization.
- Quaternion-to-rotation-matrix projection.

Controls:

- `Arrows`: apply torque on X/Y axes
- `Q` / `E`: apply torque on Z axis
- `R`: reset
- `Space`: pause/resume
- `Esc`: quit

## Demo Media

Capture previews are stored in `captures/`.

<table>
  <tr>
    <td align="center">
      <img src="captures/particle_20260420_150431_638548.gif" alt="Particle Demo" width="460" />
    </td>
    <td align="center">
      <img src="captures/spring_20260420_150012_788560.gif" alt="Spring Demo" width="460" />
    </td>
  </tr>
  <tr>
    <td align="center"><em>Particle Demo: emitter, forces, and lifetime behavior.</em></td>
    <td align="center"><em>Spring Demo: mass-spring cloth-like net simulation.</em></td>
  </tr>
  <tr>
    <td align="center">
      <img src="captures/softbody_20260420_145947_770496.gif" alt="Softbody Demo" width="460" />
    </td>
    <td align="center">
      <img src="captures/rigidbody_20260420_145913_278522.gif" alt="Rigid Body Demo" width="460" />
    </td>
  </tr>
  <tr>
    <td align="center"><em>Soft Body Demo: pressure and spring deformation.</em></td>
    <td align="center"><em>Rigid Body Demo: circle collisions with broadphase acceleration.</em></td>
  </tr>
</table>

## Architecture

```text
project/
|-- main.py
|-- media_capture.py
|-- requirements.txt
|-- engine/
|   |-- broadphase.py
|   |-- collisions.py
|   |-- config.py
|   |-- constraints.py
|   |-- core.py
|   |-- debug.py
|   |-- forces.py
|   |-- integrators.py
|   |-- kinematics.py
|   |-- math2d.py
|   |-- math3d.py
|   |-- particle.py
|   |-- pbd.py
|   |-- rigidbody.py
|   |-- softbody.py
|   |-- spring.py
|-- demos/
|   |-- base_demo.py
|   |-- kinematics_demo.py
|   |-- particle_demo.py
|   |-- pbd_demo.py
|   |-- rigidbody_cube_demo.py
|   |-- rigidbody_demo.py
|   |-- softbody_demo.py
|   |-- spring_demo.py
|-- docs/
|   |-- DEMO_GAME_CONCEPT.md
|   |-- PHYSICS_ENGINE_PIPELINE.md
|   |-- PORTFOLIO_POLISH_PLAN.md
|-- tests/
|   |-- test_rigidbody.py
```

### Engine Modules

- `core.py`: fixed-timestep clock and simple physics-world stepping.
- `math2d.py`: mutable 2D vector utilities.
- `math3d.py`: 3D vectors, matrices, quaternions, and inertia helpers.
- `integrators.py`: explicit and semi-implicit Euler helpers.
- `forces.py`: gravity, drag, and force accumulation.
- `collisions.py`: circle contact generation and impulse response.
- `constraints.py`: distance constraint projection.
- `particle.py`: point-mass particles and batched particle stepping.
- `spring.py`: damped spring force model.
- `softbody.py`: pressure soft body built on particles and springs.
- `rigidbody.py`: 2D circle bodies, 2D angular rigid bodies, and 3D quaternion rigid-body state.
- `broadphase.py`: spatial hash collision candidate generation.
- `kinematics.py`: forward-kinematics helper scaffolding.
- `pbd.py`: PBD scaffolding.
- `debug.py`: performance overlay utilities.

## Documentation

- [docs/DEMO_GAME_CONCEPT.md](docs/DEMO_GAME_CONCEPT.md): planned playable demo game.
- [docs/PHYSICS_ENGINE_PIPELINE.md](docs/PHYSICS_ENGINE_PIPELINE.md): engine development pipeline.
- [PROJECT_IMPLEMENTATION_STEPS.md](PROJECT_IMPLEMENTATION_STEPS.md): implementation milestones.
- [optimizations.md](optimizations.md): performance notes.

## Roadmap

1. Complete the PBD solver and replace the placeholder demo with an interactive rope or cloth scene.
2. Build the FK/IK demo with controllable joints and target reaching.
3. Implement the Beach Ball Duel demo game using rigid bodies, particles, wind, powerups, and scoring.
4. Add focused tests for collisions, constraints, particles, springs, and game-state rules.
5. Capture fresh media for all completed demos, including the rigid-body cube and final game.
