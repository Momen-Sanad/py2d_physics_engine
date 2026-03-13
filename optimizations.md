# 2D Physics Engine Performance Plan

This document replaces the earlier demo-specific notes with a repo-level optimization plan for simulating **hundreds of particles and springs** while preserving the same physics model.

## Goal

Optimize for speed **without reducing physical fidelity**.

That means:

1. Keep the same fixed timestep.
2. Keep the same force equations.
3. Keep the same collision candidates.
4. Keep the same solver iteration counts unless profiling proves they are already excessive.
5. Avoid "optimizations" that simply simulate less.

## What matters most in this repo

The current bottlenecks are not the tiny Python details first. The major costs are:

1. **Allocation churn from immutable `Vec2` objects**
   - [engine/math2d.py](d:/pba/project/engine/math2d.py) uses a frozen dataclass.
   - Every `+`, `-`, `*`, `/`, `normalized()`, and `distance_to()` creates new objects.
   - In particle, spring, and soft-body loops this becomes expensive quickly.
2. **Repeated spring recomputation**
   - [engine/softbody.py](d:/pba/project/engine/softbody.py) currently calls `spring.force()`, `spring.normal()`, and `spring.length()` inside the same loop.
   - That recomputes the same edge direction and distance multiple times per spring per step.
3. **Object-graph traversal**
   - `Spring -> Particle -> Vec2` is clean, but Python pays for every attribute lookup in hot loops.
4. **Quadratic collision scaling**
   - [demos/rigidbody_demo.py](d:/pba/project/demos/rigidbody_demo.py) still checks every body pair.
   - This becomes the first hard wall once body count grows.
5. **Per-frame temporary lists**
   - Area computation and rendering build new lists every frame.

If you want hundreds of particles with headroom, the biggest wins are **data layout**, **broadphase**, and **single-pass spring evaluation**.

## Non-negotiable rule

If the requirement is "maximum performance without any physics loss", do **not** do these:

1. Do not reduce spring count.
2. Do not reduce solver iterations just to gain FPS.
3. Do not increase `dt` just to make the simulation cheaper.
4. Do not skip collision pairs that can actually overlap.
5. Do not switch to approximate rendering-driven physics.

Those are scope cuts, not performance improvements.

## Highest-impact optimizations

### 1. Replace hot-path object math with indexed numeric storage

Current style:

1. `Particle.position` is a `Vec2`
2. `Particle.velocity` is a `Vec2`
3. `Spring` stores particle objects
4. Inner loops repeatedly dereference objects and allocate vectors

Recommended hot-path layout:

1. `positions_x: list[float]`
2. `positions_y: list[float]`
3. `velocities_x: list[float]`
4. `velocities_y: list[float]`
5. `forces_x: list[float]`
6. `forces_y: list[float]`
7. `inverse_mass: list[float]`
8. `radius: list[float]`
9. Springs stored as endpoint indices:
   - `spring_a`
   - `spring_b`
   - `rest_length`
   - `stiffness`
   - `damping`

Why this matters:

1. Removes most temporary `Vec2` allocations.
2. Reduces attribute lookup overhead.
3. Makes hot loops easier to optimize later with `NumPy`, `Numba`, or `Cython`.
4. Preserves the same formulas and same simulation behavior.

Important:

1. You can still keep `Vec2` for editor/debug/API code.
2. The hot simulation core should not depend on immutable vector objects.

### 2. Fuse spring calculations into one pass

Current soft-body loop does too much repeated work per spring.

For each spring, compute these exactly once:

1. `dx`, `dy`
2. `distance_sq`
3. `distance`
4. `nx`, `ny`
5. `relative_velocity_along_spring`
6. spring force
7. pressure force, if applicable

Then write the force results directly into the particle force arrays.

This matters because for hundreds of springs, repeated `length()`, `normalized()`, and `distance_to()` calls cost more than the actual physics arithmetic.

### 3. Add a proper broadphase for particle or rigid-body collisions

Any all-pairs loop becomes the dominant cost once body count grows.

Use one of these:

1. Uniform grid
2. Spatial hash

Requirements for zero physics loss:

1. Cell size must be at least the maximum interaction radius you need to catch.
2. Check the current cell and all neighboring cells required by the shape size.
3. Rebuild the broadphase each step or maintain it exactly when objects move.

This changes the candidate search cost without changing the collision response model.

### 4. Pool particles instead of constantly creating and deleting them

This matters most for particle emitters.

Recommended:

1. Preallocate capacity for the maximum expected particle count.
2. Reuse dead particle slots.
3. Use swap-remove or an active-count scheme instead of frequent `list.remove()`.

This preserves behavior and removes garbage-collection spikes.

### 5. Reuse scratch buffers every frame

Do not allocate scratch structures in hot loops.

Examples:

1. Predicted position buffers for PBD
2. Temporary broadphase buckets
3. Render point lists
4. Collision pair work lists
5. Area accumulation helpers

Allocate once, then clear or overwrite.

### 6. Decouple rendering cost from simulation cost

For large particle counts, drawing can become expensive too.

Keep:

1. Fixed-timestep simulation
2. Rendering once per frame

Add:

1. Debug-draw toggles for springs, normals, velocity vectors, and particle IDs
2. Optional render interpolation later if needed

This keeps the simulation exact while preventing debug visuals from being mistaken for physics cost.

### 7. Move only the hot loops to compiled execution if Python is still the bottleneck

If the engine still struggles after the structural optimizations above, the next safe step is compiled acceleration of the same math:

1. `Numba`
2. `Cython`
3. A small Rust or C++ extension for the solver core

This is the right kind of "maximum performance" improvement because it preserves the same equations and same timestep.

## Current code-specific fixes to prioritize

These are the first things to change in this repo.

### A. `Vec2` immutability is expensive in the solver

In [engine/math2d.py](d:/pba/project/engine/math2d.py), every vector operation allocates a new object.

That is acceptable for setup code and debug tools, but not ideal for:

1. particle integration
2. spring force accumulation
3. soft-body pressure updates
4. collision resolution

Best fix:

1. Keep `Vec2` for public-facing code.
2. Move simulation internals to numeric arrays or mutable components.

### B. `SoftBody.step()` should become a single-pass spring loop

In [engine/softbody.py](d:/pba/project/engine/softbody.py), this pattern is too expensive:

1. compute spring force
2. compute spring normal
3. compute spring length

That repeats the same edge math. Replace it with one loop that computes all spring-derived quantities once.

### C. `polygon_area()` should avoid rebuilding point lists

Current usage builds a new `list[Vec2]` first.

Better:

1. iterate directly over particle positions
2. or store particle coordinates in arrays and compute area directly from them

### D. Collision loops must stop using full pair scans

In [demos/rigidbody_demo.py](d:/pba/project/demos/rigidbody_demo.py), this is still quadratic:

```python
for index, body in enumerate(bodies):
    for other in bodies[index + 1:]:
        resolve_circle_collision(body, other)
```

For a few bodies this is fine. For hundreds, use a grid.

## Medium-impact optimizations

These help, but only after the structural items above.

### 1. Remove list slicing in pair loops

Use indexed loops instead of `bodies[index + 1:]`.

### 2. Cache loop-invariant values once per frame

Examples:

1. friction factor
2. gravity components
3. screen bounds
4. solver constants

### 3. Use squared distances when normalization is not required

Use `distance_sq` for:

1. broadphase rejection
2. overlap checks
3. cheap early-outs

Take the square root only when you actually need the distance magnitude or unit normal.

### 4. Minimize Python function dispatch in hot loops

Calling tiny helper methods thousands of times can be slower than one flat loop.

In the solver core, it is often better to inline the arithmetic than to call:

1. `length()`
2. `normalized()`
3. `distance_to()`
4. `apply_force()`

Keep the object-oriented wrappers for clarity outside the hottest path.

### 5. Pre-render repeated visuals when render cost matters

If the render path becomes expensive:

1. cache circle sprites by radius/color
2. keep debug lines optional
3. avoid rebuilding draw data unnecessarily

This improves rendering without touching the physics.

## Optimizations that preserve behavior but can change floating-point details

These are usually acceptable, but they can slightly change step-to-step trajectories due to operation order:

1. parallel spring solving
2. changing collision resolution order
3. changing constraint solve order
4. switching between AoS and SoA if arithmetic order changes

If strict determinism matters for grading or debugging, keep iteration order stable.

## Recommended implementation order

Do this in order:

1. Replace hot-path `Vec2` usage with numeric storage in the solver core.
2. Rewrite spring and soft-body force accumulation as a single-pass indexed loop.
3. Add a uniform-grid broadphase for circle and particle collisions.
4. Add particle pooling for emitter-heavy demos.
5. Reuse all scratch buffers and render point arrays.
6. Profile again.
7. If still needed, compile the hot loops with `Numba` or `Cython`.

## Practical target for "hundreds of particles"

For this project, a strong target is:

1. hundreds of particles
2. hundreds of springs
3. fixed timestep maintained
4. no visible instability from frame spikes

You are unlikely to reach that comfortably in pure Python if the solver keeps:

1. immutable vector allocation in hot loops
2. repeated spring recomputation
3. all-pairs collision checks

Those three issues should be treated as the main blockers.

## Profiling rule

Before and after each optimization pass, measure:

1. total frame time
2. simulation step time
3. render time
4. collision time
5. spring/constraint solve time

Use profiling to confirm the bottleneck moved. Do not rely on assumptions after the first optimization pass.

## Bottom line

If you want the best performance **without physics loss**, the winning strategy is:

1. keep the same physics model
2. change the data layout
3. eliminate repeated spring math
4. add broadphase collision detection
5. reuse memory aggressively
6. compile only the hot loops if Python still tops out

That is the path that increases scale without "cheating" the simulation.
