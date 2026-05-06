# Physics Engine Implementation Steps (Updated 2026-05-06)

## 1. Locked Scope Decision

1. The project is **2D-only**.
2. 3D work is out of scope.
3. `pygame` remains the visualization/input layer.
4. Physics modularity and clean demo isolation remain the grading focus.

## 2. Current Status Snapshot (2026-05-06)

| Area | Status | Current Evidence |
|---|---|---|
| Engine core (loop, timing, math, forces, collisions, constraints) | Implemented | `engine/core.py`, `engine/math2d.py`, `engine/integrators.py`, `engine/forces.py`, `engine/collisions.py`, `engine/constraints.py` |
| Particle demo | Implemented | `demos/particle_demo.py` + launcher key `particle` |
| Mass-spring demos | Implemented | `demos/spring_demo.py`, `engine/spring.py`, `demos/softbody_demo.py`, `engine/softbody.py` |
| Rigid body dynamics demos | Implemented | `demos/rigidbody_demo.py`, `demos/rigidbody_cube_demo.py`, `engine/rigidbody.py`, `engine/math3d.py`, `engine/broadphase.py` |
| PBD | Implemented demo | `engine/pbd.py` solver types/functions, `demos/pbd_demo.py`, launcher key `pbd` |
| FK | Implemented demo | `engine/kinematics.py` (`forward_chain`, `KinematicChain`), `demos/kinematics_demo.py` |
| IK | Implemented demo | CCD solver in `engine/kinematics.py`, mouse-target IK behavior in `demos/kinematics_demo.py` |
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

1. Integrate at least three modules into a final playable scene.
2. Finalize report and presentation assets.
3. Continue cleanup/tests/docs polish.

## 5. Completed PBD Implementation

1. Predicted-position buffers live in `engine/pbd.py`.
2. Iterative distance constraint projection supports configurable iteration count.
3. Pin/anchor constraints are available for fixed or dragged particles.
4. Boundary handling keeps movable particles inside demo bounds.
5. Velocities are reconstructed from corrected positions.
6. `demos/pbd_demo.py` provides an interactive rope scene.

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
python main.py pbd
python main.py rigidbody
python main.py rigidbody_cube
python main.py kinematics
```

## 9. Bottom Line

1. Scope is stable and low-risk: **2D-first**, with a contained 3D rigid-body rotation demo for quaternion and inertia coverage.
2. Particle, spring/soft-body, and rigid-body demos are already in place.
3. PBD, FK, and IK are implemented as isolated engine modules with runnable demos.
4. The next major implementation target is final multi-module game integration and presentation polish.
