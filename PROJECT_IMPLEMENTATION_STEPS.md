# SWGCG 352 Project Implementation Steps (Updated)

## 1. Locked Scope Decision

1. The project is now **2D-only**.
2. We are dropping 3D work completely.
3. `pygame` remains the visualization/input layer.
4. Physics and engine modularity remain the main grading focus.

## 2. Current Status Snapshot (2026-03-21)

| Area | Status | Current Evidence |
|---|---|---|
| Engine core (loop, timing, math, forces, collisions, constraints) | In place | `engine/core.py`, `engine/math2d.py`, `engine/integrators.py`, `engine/forces.py`, `engine/collisions.py`, `engine/constraints.py` |
| Particle foundations | Partially complete | `engine/particle.py` is implemented, but `demos/particle_demo.py` is still a placeholder |
| Mass-spring models | Implemented | `demos/spring_demo.py`, `engine/spring.py`, `demos/softbody_demo.py`, `engine/softbody.py` |
| Rigid body dynamics | Implemented demo | `demos/rigidbody_demo.py`, `engine/rigidbody.py`, `engine/broadphase.py` |
| PBD | Not implemented as a full module yet | `engine/pbd.py` has helper scaffolding only, `demos/pbd_demo.py` is a placeholder |
| FK | Partially complete | `engine/kinematics.py` has FK helper (`forward_chain`), but no runnable demo yet |
| IK | Not started | No solver/demo integrated yet |
| Final integrated game | Not started | No `game_scene.py` or equivalent playable loop yet |

## 3. Direct Answer: What Is Next?

1. Yes: **mass-spring work is done enough to count as implemented demos**.
2. Particle system is **partially done** (engine-level done, dedicated particle demo still pending).
3. The next major physics module should be **PBD**.

## 4. Updated Execution Order From Here

1. Finish the standalone particle demo (emitter + lifetime + burst/reset controls).
2. Build the full PBD module and demo (rope/cloth with distance constraints).
3. Build FK demo scene (interactive 2D joint chain).
4. Build IK demo scene (CCD or FABRIK target reaching).
5. Integrate final game using at least three modules.
6. Finalize report/presentation assets while implementing.

## 5. Immediate PBD Plan (Next Milestone)

1. Implement predicted-position buffers in `engine/pbd.py`.
2. Add distance constraint projection with iteration count control.
3. Add pin/anchor constraints.
4. Add boundary/ground handling.
5. Compute velocities from corrected positions.
6. Build `demos/pbd_demo.py` with keyboard controls for:
   - reset
   - pause
   - solver iteration up/down
7. Compare spring rope vs PBD rope behavior in notes/screenshots.

## 6. Definition of Done for Remaining Modules

### Particle Demo (remaining work)

1. Continuous emitter.
2. Gravity + drag toggles.
3. Burst trigger.
4. Particle cleanup by lifetime.

### PBD Demo

1. Stable rope or cloth.
2. Adjustable solver iterations.
3. Clear visual difference from force-based springs.

### FK/IK Demo

1. FK chain with controllable joint angles.
2. IK chain that reaches a moving target.
3. Segment length constraints preserved.

### Final Game Integration

1. Uses at least three physics modules in gameplay.
2. Has win/lose or goal progression.
3. Has restart and basic UI/help text.

## 7. Recommended Final Game Module Mix (2D)

1. Rigid bodies for interaction and collision gameplay.
2. PBD ropes/constraints for mechanics.
3. IK arm/tool for player interaction.
4. Particle effects for feedback/polish.

## 8. Run Commands (Current)

From `project/`:

```bash
python main.py spring
python main.py softbody
python main.py rigidbody
```

Planned additions once implemented:

```bash
python main.py particle
python main.py pbd
python main.py kinematics
```

## 9. Bottom Line

1. Scope is now clean and lower-risk: **2D only**.
2. You have already completed key engine modules and two strong deformable/rigid demo tracks.
3. The next main module is **PBD** (after or alongside finishing the particle demo scene).
4. Then finish FK/IK and move to final game integration.
