# SWGCG 352 Project Implementation Steps (Updated 2026-04-20)

## 1. Locked Scope Decision

1. The project is **2D-only**.
2. 3D work is out of scope.
3. `pygame` remains the visualization/input layer.
4. Physics modularity and clean demo isolation remain the grading focus.

## 2. Current Status Snapshot (2026-04-20)

| Area | Status | Current Evidence |
|---|---|---|
| Engine core (loop, timing, math, forces, collisions, constraints) | Implemented | `engine/core.py`, `engine/math2d.py`, `engine/integrators.py`, `engine/forces.py`, `engine/collisions.py`, `engine/constraints.py` |
| Particle demo | Implemented | `demos/particle_demo.py` + launcher key `particle` |
| Mass-spring demos | Implemented | `demos/spring_demo.py`, `engine/spring.py`, `demos/softbody_demo.py`, `engine/softbody.py` |
| Rigid body dynamics demos | Implemented | `demos/rigidbody_demo.py`, `demos/rigidbody_cube_demo.py`, `engine/rigidbody.py`, `engine/math3d.py`, `engine/broadphase.py` |
| PBD | Scaffolded only | `engine/pbd.py` helper types/functions, `demos/pbd_demo.py` placeholder |
| FK | Scaffolded helper only | `engine/kinematics.py` (`forward_chain`) |
| IK | Not started | No IK solver/demo integrated yet |
| Final integrated game | Not started | No playable multi-module game loop yet |

## 3. Development Order Policy

Canonical order (from scratch):

1. Foundation
2. Particle system
3. Mass-spring / soft-body
4. PBD
5. Rigid body dynamics
6. Forward kinematics (FK)
7. Inverse kinematics (IK)
8. Final game integration and polish

Important ordering rule:

1. **Rigid bodies come before FK/IK** in the implementation sequence.

## 4. Remaining Execution Order From Current State

1. Complete the full PBD module and runnable demo (rope/cloth with constraints).
2. Build a dedicated FK demo scene (interactive joint chain).
3. Build IK solver behavior (CCD or FABRIK) into the kinematics demo.
4. Integrate at least three modules into a final playable scene.
5. Finalize report and presentation assets.

## 5. Immediate PBD Plan

1. Extend predicted-position buffers in `engine/pbd.py`.
2. Add iterative distance constraint projection with configurable iteration count.
3. Add pin/anchor constraints.
4. Add boundary/ground handling.
5. Reconstruct velocities from corrected positions.
6. Replace placeholder `demos/pbd_demo.py` with an interactive scene.
7. Compare spring-rope vs PBD-rope behavior in notes/captures.

## 6. Definition of Done for Remaining Modules

### PBD Demo

1. Stable rope or cloth scene.
2. Adjustable solver iterations.
3. Clear stability/behavior difference versus force-based springs.

### FK/IK Demo

1. FK chain with controllable joint angles.
2. IK chain reaches a moving target.
3. Segment lengths remain fixed.

### Final Game Integration

1. Uses at least three physics modules in gameplay.
2. Has win/lose or goal progression.
3. Has restart and basic UI/help text.

## 7. Recommended Final Game Module Mix (2D)

1. Rigid bodies for interaction/collision gameplay.
2. PBD ropes/constraints for mechanics.
3. IK arm/tool for player interaction.
4. Particle effects for feedback/polish.

## 8. Run Commands (Current)

From `project/`:

```bash
python main.py particle
python main.py spring
python main.py softbody
python main.py rigidbody
python main.py rigidbody_cube
```

Planned additions once implemented:

```bash
python main.py pbd
python main.py kinematics
```

## 9. Bottom Line

1. Scope is stable and low-risk: **2D-first**, with a contained 3D rigid-body lecture demo for Lec09 rotation coverage.
2. Particle, spring/soft-body, and rigid-body demos are already in place.
3. The next major implementation target is full **PBD**.
4. After PBD, finish **FK then IK**, then move to final integration.
