# 2D Physics Engine Development Pipeline

## Goal

This repository is now scoped to a **2D physics engine only**. The game layer is intentionally postponed.

The short-term goal is to build a clean engine with standalone demos for:

1. Particle systems
2. Mass-spring systems
3. Position-Based Dynamics (PBD)
4. Rigid body dynamics
5. Forward kinematics (FK)
6. Inverse kinematics (IK)

## Current Implementation Snapshot (2026-04-20)

| Area | Status | Evidence |
|---|---|---|
| Engine core (loop/timing/math/integrators/forces/collisions/constraints) | Implemented | `engine/core.py`, `engine/math2d.py`, `engine/integrators.py`, `engine/forces.py`, `engine/collisions.py`, `engine/constraints.py` |
| Particle system | Implemented demo | `demos/particle_demo.py` + launcher key `particle` |
| Mass-spring system | Implemented demo | `demos/spring_demo.py`, `engine/spring.py` |
| Pressure soft body | Implemented demo | `demos/softbody_demo.py`, `engine/softbody.py` |
| Rigid body dynamics | Implemented demo | `demos/rigidbody_demo.py`, `engine/rigidbody.py`, `engine/broadphase.py` |
| PBD | Scaffolded only | `engine/pbd.py`, `demos/pbd_demo.py` placeholder |
| FK | Scaffolded helper only | `engine/kinematics.py` (`forward_chain`) |
| IK | Not implemented | No IK solver/demo integrated yet |

## File Structure

```text
project/
  main.py
  requirements.txt
  engine/
    __init__.py
    config.py
    math2d.py
    core.py
    integrators.py
    forces.py
    collisions.py
    constraints.py
    particle.py
    spring.py
    softbody.py
    pbd.py
    rigidbody.py
    kinematics.py
  demos/
    __init__.py
    base_demo.py
    particle_demo.py
    spring_demo.py
    softbody_demo.py
    pbd_demo.py
    rigidbody_demo.py
    kinematics_demo.py
  docs/
    PHYSICS_ENGINE_PIPELINE.md
```

## Extracted Reference Systems

The repo currently has these runnable and scaffolded systems:

1. Interactive particle playground in `demos/particle_demo.py`
2. Falling spring-net demo in `demos/spring_demo.py`
3. Pressure-based soft-body demo in `demos/softbody_demo.py`
4. Circle rigid-body demo with broadphase in `demos/rigidbody_demo.py`
5. PBD/FK module scaffolding in `engine/pbd.py` and `engine/kinematics.py`

## Development Rules

Keep these rules from the start:

1. Use a fixed timestep for simulation.
2. Keep physics logic separate from drawing code.
3. Build one isolated demo per module.
4. Add debug views early:
   - velocity vectors
   - force vectors
   - collision normals
   - constraint links
5. Keep every module testable on its own before integrating anything else.
6. Prefer stable, simple implementations over ambitious ones.

## Recommended Build Order

### Stage 1: foundation (implemented)

Build this first:

1. `Vec2` math utilities
2. Engine configuration
3. Fixed-timestep clock
4. World/system stepping
5. Basic debug drawing plan

Definition of done:

1. You can update a system at a fixed `dt`.
2. Shared math utilities are available to every module.
3. There is one place for gravity, solver iterations, and timing settings.

### Stage 2: particle system (implemented)

Build next:

1. Particle data structure
2. Force accumulation
3. Gravity
4. Drag
5. Lifetime handling
6. Emitter behavior

Definition of done:

1. Particles spawn and expire correctly.
2. Gravity and drag visibly affect motion.
3. You can reset the scene and spawn bursts.

### Stage 3: mass-spring system (implemented)

Build after particles:

1. Spring connection data
2. Hooke's law force
3. Damping term
4. Pinned particles
5. Rope scene first
6. Small cloth or soft-body scene second

Definition of done:

1. Rope behaves stably at a reasonable timestep.
2. Stiffness and damping are adjustable.
3. The spring network does not explode immediately under gravity.

### Stage 4: PBD (scaffolded, not complete)

Build after the spring demo:

1. Predicted positions
2. Distance constraints
3. Iterative solver
4. Velocity reconstruction from corrected positions
5. Rope or cloth demo

Definition of done:

1. PBD rope is visibly more stable than the force-based rope at similar settings.
2. Constraint iterations can be tuned.
3. Pin constraints or ground constraints work.

### Stage 5: rigid body dynamics (implemented)

Build after PBD:

1. Rigid body state
2. Linear integration
3. Angular integration
4. Circle-ground collisions
5. Circle-circle collisions
6. Impulse response

Definition of done:

1. Bodies fall, collide, and separate correctly.
2. Resting and bouncing behavior are at least believable.
3. You can spawn or launch rigid bodies in a demo scene.

### Stage 6: kinematics (FK scaffolded, IK pending)

Build after rigid bodies:

1. FK chain positions
2. Joint angle control
3. IK target handling
4. CCD or FABRIK solver

Definition of done:

1. A multi-link arm updates correctly with FK.
2. The end effector can reach toward a target using IK.
3. Segment lengths stay fixed.

### Stage 7: engine cleanup (in progress)

Do this before any game work:

1. Normalize naming and file responsibilities
2. Remove duplicated math or update code
3. Make module parameters configurable
4. Add a demo selector
5. Add screenshots and notes as you go

Definition of done:

1. Each demo is isolated and runnable.
2. Shared code lives in `engine/`, not copied across demos.
3. The engine is ready to be used later by a game layer.

## Step-by-Step Working Plan

development order:

1. Finish `math2d.py`.
2. Finish `core.py` and fixed timestep management.
3. Implement the first runnable particle demo.
4. Add spring data and rope simulation.
5. Add PBD distance-constraint solving.
6. Add rigid body integration and the first collision case.
7. Add rigid body impulse response.
8. Add FK chain rendering and controls.
9. Add IK solver.
10. Refactor shared helpers into reusable engine code.

Remaining order from the current repo state:

1. Finish full PBD module + runnable demo.
2. Build a dedicated FK demo scene.
3. Add IK solver + target-driven demo behavior.
4. Continue engine cleanup/tests/docs polish.

## Suggested Weekly Breakdown

### Week 1

1. Finish engine foundation
2. Finish particle demo

### Week 2

1. Finish spring demo
2. Start PBD demo

### Week 3

1. Finish PBD demo
2. Start rigid body demo

### Week 4

1. Finish rigid body demo
2. Start FK and IK demo

### Week 5

1. Finish kinematics demo
2. Refactor and clean engine interfaces
