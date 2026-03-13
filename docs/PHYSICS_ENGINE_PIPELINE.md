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

The repo now has working systems extracted from your older code:

1. A falling spring-net demo in `demos/spring_demo.py`
2. A pressure-based soft-body demo in `demos/softbody_demo.py`
3. Circle collision handling in `engine/collisions.py`
4. A circle rigid-body demo in `demos/rigidbody_demo.py`

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

### Stage 1: foundation

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

### Stage 2: particle system

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

### Stage 3: mass-spring system

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

### Stage 4: PBD

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

### Stage 5: rigid body dynamics

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

### Stage 6: kinematics

Build after rigid bodies:

1. FK chain positions
2. Joint angle control
3. IK target handling
4. CCD or FABRIK solver

Definition of done:

1. A multi-link arm updates correctly with FK.
2. The end effector can reach toward a target using IK.
3. Segment lengths stay fixed.

### Stage 7: engine cleanup

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

Use this order during development:

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

## Immediate Next Tasks

If you start coding right now, do this:

1. Install dependencies from `requirements.txt`.
2. Build a tiny window loop and frame timer.
3. Connect the fixed timestep to one empty demo scene.
4. Make the particle demo the first truly runnable module.
5. Do not start rigid bodies until particles and springs are stable.

## What Not To Do Yet

Avoid these until the engine demos are stable:

1. Do not build gameplay rules yet.
2. Do not add menus beyond a simple demo selector.
3. Do not attempt full 3D rendering.
4. Do not mix rendering code into the physics module logic.
