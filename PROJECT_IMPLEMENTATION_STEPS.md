# SWGCG 352 Project Implementation Steps

## 1. What the project is asking for

You are not just building a game. You are building:

1. A modular physics engine.
2. Separate physics modules inside that engine.
3. A simple interactive game that uses the engine.
4. A report and presentation that explain the work.

The document explicitly requires these physics areas:

1. Particle systems
2. Mass-spring models
3. Position-Based Dynamics (PBD)
4. Rigid body dynamics
5. Forward kinematics (FK)
6. Inverse kinematics (IK)
7. Core engine architecture:
   - object representation
   - simulation update loop
   - force accumulation
   - numerical integration
   - collision handling
   - constraint resolution

The game must clearly demonstrate at least **three** of the implemented physics modules.

## 2. Best scope for a Python version

The safest approach is:

1. Build the physics engine in Python as a renderer-independent system.
2. Use `pygame` for input, timing, drawing, and quick visualization.
3. If your team already has a different rendering library for 3D transforms and drawing, keep that renderer separate from the physics code and plug the engine into it.

Important practical point:

1. The brief does **not** say you must build full 3D physics.
2. A strong course-project version can be done in **2D physics** with clear visualization.
3. If you already have a 3D renderer, use it mainly for presentation, not to make the physics problem harder than necessary.

Recommended strategy:

1. Implement the physics logic in 2D first.
2. Make the engine modular enough that rendering can be swapped.
3. Only add 3D visualization if it does not risk the schedule.

## 3. Minimum success criteria

To satisfy the brief, your project should include:

1. A reusable simulation framework.
2. A working particle system.
3. A working soft/deformable system using springs.
4. A working PBD example using constraints.
5. A working rigid body example with collisions.
6. At least one FK example.
7. At least one IK example.
8. A playable game that uses at least three of those systems.
9. A report with architecture, formulas, implementation notes, challenges, screenshots, and game explanation.
10. A presentation with a live demo.

## 4. Recommended Python stack

### Option A: simplest and safest

Use:

1. Python 3.x
2. `pygame`
3. Your own math/physics code

Why:

1. Fast to set up
2. Easy to visualize particles, springs, collisions, and articulated chains
3. Good enough for a complete course project

### Option B: if you already have a 3D renderer

Use:

1. Python 3.x
2. Your previous rendering/transform library
3. The same physics engine underneath

Why:

1. Better visuals
2. Lets you reuse earlier work
3. Still keeps the engine modular

Rule:

1. Do not bury physics logic inside rendering code.
2. Physics state should update first.
3. Rendering should only display the current state.

## 5. Recommended architecture

Use a structure like this:

```text
project/
  main.py
  engine/
    math2d.py
    core.py
    integrators.py
    collisions.py
    constraints.py
    particle.py
    spring.py
    pbd.py
    rigidbody.py
    kinematics.py
  scenes/
    particle_demo.py
    spring_demo.py
    pbd_demo.py
    rigidbody_demo.py
    kinematics_demo.py
    game_scene.py
  docs/
    report_assets/
```

Core responsibilities:

1. `math2d.py`
   Vector operations, dot product, normalization, rotation helpers.
2. `core.py`
   Simulation objects, world state, update loop, scene management.
3. `integrators.py`
   Explicit Euler, semi-implicit Euler, optional Verlet.
4. `collisions.py`
   Ground collision, circle-circle or box-box tests, response.
5. `constraints.py`
   Distance constraints and positional correction.
6. `particle.py`
   Particle data, forces, integration, emitters.
7. `spring.py`
   Hooke's law, damping, spring networks, soft body.
8. `pbd.py`
   Constraint projection on positions.
9. `rigidbody.py`
   Linear motion, angular motion, impulses, collision response.
10. `kinematics.py`
    Bone/joint chain, FK transforms, IK solver.

## 6. Build order

Follow this order. It reduces risk and lets you demo progress every week.

### Step 1: define the project scope

Decide these things first:

1. Will the physics be 2D only, or 2D with optional 3D rendering?
2. Which three modules will definitely appear in the final game?
3. What is the game idea?

Good low-risk game ideas:

1. Physics puzzle game with launchable objects, soft obstacles, and an IK arm.
2. Arena game with rigid bodies, particles, and rope/cloth constraints.
3. Platformer with particle effects, moving rigid bodies, and an IK-controlled grabbing tool.

Best recommendation:

1. Final game uses rigid bodies + springs/PBD + IK.
2. Particle system is used for polish and feedback.

### Step 2: set up the base project

Create:

1. Window loop
2. Fixed timestep update
3. Render loop
4. Input handling
5. Debug drawing helpers

You should already be able to:

1. Open a window
2. Pause/resume simulation
3. Step one frame at a time
4. Draw points, lines, circles, rectangles
5. Display FPS and current scene

### Step 3: implement common math and engine primitives

Build:

1. `Vector2`
2. Transform helpers
3. Particle base class
4. Rigid body base class
5. Force accumulator
6. Constraint interface

Essential formulas:

1. Force: `F = m a`
2. Velocity update: `v = v + a * dt`
3. Position update: `x = x + v * dt`

Recommended integrator:

1. Start with semi-implicit Euler because it is simple and usually more stable than explicit Euler.

### Step 4: particle system module

Implement:

1. Particle data:
   - position
   - velocity
   - acceleration
   - mass
   - lifetime
2. Global forces:
   - gravity
   - drag
   - wind
3. Emitters
4. Particle spawning and cleanup
5. Visual styles:
   - sparks
   - smoke
   - explosions

Demo target:

1. A scene where particles are emitted continuously.
2. User can toggle forces and spawn bursts.

### Step 5: mass-spring system

Implement:

1. Spring connection between particles
2. Rest length
3. Stiffness
4. Damping
5. Fixed anchor points
6. Structural spring network

Essential formulas:

1. Spring force: `F = -k (length - rest_length)`
2. Damping force depends on relative velocity along the spring direction

Demo target:

1. Rope
2. Cloth strip
3. Jelly/soft-body grid

Important note:

1. Start with a rope or small cloth grid.
2. Do not begin with a large soft body because stability problems will slow you down.

### Step 6: PBD module

Implement:

1. Position prediction
2. Constraint projection
3. Velocity update from corrected positions
4. Distance constraints
5. Optional pin constraints or ground constraints

PBD loop idea:

1. Predict positions
2. Solve constraints several iterations
3. Update velocities
4. Commit corrected positions

Demo target:

1. Stable rope
2. Stable cloth patch
3. Constraint-based chain

Why this matters:

1. PBD is often easier to stabilize visually than force-based soft-body simulation.
2. It gives you a second style of deformable simulation distinct from springs.

### Step 7: rigid body dynamics

Implement:

1. Linear position and velocity
2. Orientation and angular velocity
3. Forces and torques
4. Impulse-based collision response
5. Ground collision
6. Object-object collision

Start with simple shapes:

1. Circles and oriented rectangles in 2D

Essential formulas:

1. Linear momentum update from net force
2. Angular update from torque and moment of inertia
3. Impulse response using relative velocity along collision normal

Demo target:

1. Falling objects
2. Bouncing and sliding
3. Stack or pile of objects
4. User can push or launch bodies

### Step 8: forward kinematics

Implement:

1. Joint chain
2. Parent-child transforms
3. Local rotation per joint
4. End-effector position computation

Demo target:

1. A 2-link or 3-link arm
2. Keys rotate each joint
3. End effector updates correctly

### Step 9: inverse kinematics

Implement:

1. Target point
2. IK solver for a chain
3. Either CCD or FABRIK

Recommended solver:

1. CCD is easy to implement.
2. FABRIK is also a good option if your team prefers geometric reasoning.

Demo target:

1. Mouse-controlled arm reaching a target
2. Chain follows cursor while respecting segment lengths

### Step 10: integrate the demos into one engine

By this point, do not leave each module as isolated code. Make sure:

1. All modules use the same update timing approach.
2. Scenes can be switched from one menu.
3. Physics objects share common interfaces where possible.
4. Debug overlays can display vectors, constraints, and collision normals.

This is important for the rubric because architecture and engine design are graded separately from raw physics correctness.

## 7. Suggested timeline mapped to the course milestones

### Phase 1 (Week 8): research, planning, and core framework

Deliver:

1. Project proposal
2. Architecture diagram
3. Base loop and scene system
4. First particle demo

Checklist:

1. Choose `pygame` or your existing renderer
2. Define scope and game concept
3. Create repository structure
4. Implement vector math and timestep loop
5. Show one simple particle scene

### Phase 2 (Week 9): particle systems and mass-spring systems

Deliver:

1. Particle effects demo
2. Soft-body prototype

Checklist:

1. Add emitters and forces
2. Add spring connections
3. Build rope or cloth prototype
4. Tune damping and stiffness

### Phase 3 (Week 10): PBD

Deliver:

1. Constraint-based simulation demo

Checklist:

1. Implement prediction and correction loop
2. Add distance constraints
3. Compare PBD rope/cloth against spring version
4. Record screenshots for report

### Phase 4 (Week 11): rigid body dynamics

Deliver:

1. Rigid body motion
2. Collisions
3. Rigid body simulation scene

Checklist:

1. Add body shapes
2. Add linear and angular motion
3. Add collision detection
4. Add collision response
5. Build a short interactive test scene

### Phase 5 (Week 12): kinematics

Deliver:

1. Animated articulated system

Checklist:

1. Implement FK chain
2. Implement IK solver
3. Build a scene where the chain reaches for a target

### Phase 6 (Week 13): game development

Deliver:

1. Integrated engine
2. Environment
3. Playable prototype

Checklist:

1. Pick at least three modules for the final gameplay
2. Build win/lose conditions
3. Add UI, restart, and instructions
4. Add sound and particle polish if time allows

### Week 14: submission and discussion

Deliver:

1. Final report
2. Final presentation
3. Live gameplay demo

Checklist:

1. Record clean screenshots
2. Explain architecture clearly
3. Show formulas used
4. Show module demos before the final game
5. Prepare backup video in case live demo fails

## 8. Strong final-game combinations

Pick one combination and design around it.

### Combination A: physics puzzle game

Use:

1. Rigid bodies for movable objects
2. Springs or PBD for ropes/bridges/soft obstacles
3. IK for a robotic arm or grabbing tool
4. Particles for visual feedback

### Combination B: soft-body challenge game

Use:

1. PBD cloth or rope
2. Rigid body hazards
3. IK-driven helper mechanism
4. Particle effects for impacts

### Combination C: launcher or sandbox game

Use:

1. Rigid body projectiles
2. Spring-based targets or deformable barriers
3. Particle explosions
4. IK-controlled aiming mechanism or enemy limb

## 9. Report structure

Your report should contain these sections:

1. Project overview
2. Engine architecture
3. Physics modules implemented
4. Mathematical formulas and methods
5. Game design and how the physics is used
6. Challenges and solutions
7. Results and screenshots
8. Conclusion

What to include under formulas:

1. Particle integration
2. Hooke's law for springs
3. PBD constraint correction
4. Rigid body motion equations
5. FK transform chain
6. IK solver idea

## 10. Presentation structure

A clean presentation flow is:

1. Problem statement
2. Engine architecture
3. Demo of each module
4. Final integrated game
5. Technical challenges
6. Lessons learned

Best demo order:

1. Particle system
2. Spring or PBD
3. Rigid body collision scene
4. FK/IK arm
5. Final game

## 11. Rubric-driven priorities

Because of the rubric, you should optimize for this order:

1. Correctness of physics modules
2. Clean modular code
3. Stable engine behavior
4. Clear game integration
5. Good documentation

This means:

1. A smaller but stable project is better than a larger but broken one.
2. A clean architecture helps both code-quality and engine-design marks.
3. A simple game that clearly uses the physics is better than a complex game with weak connection to the engine.

## 12. Recommended execution plan for your team

If you want the lowest-risk plan, do this:

1. Use `pygame`.
2. Implement the engine in 2D.
3. Build these required demos:
   - particle emitter
   - spring rope or cloth
   - PBD rope or cloth
   - rigid body collision scene
   - FK/IK arm
4. Build a final game using:
   - rigid bodies
   - PBD or springs
   - IK
   - particles as polish

This is enough to satisfy the brief well without taking on unnecessary 3D complexity.

## 13. First concrete tasks to start today

Do these in order:

1. Decide whether the final project is 2D-only or 2D physics with optional 3D rendering.
2. Decide the final game idea in one sentence.
3. Set up the project structure and base window loop.
4. Implement vector math and fixed timestep update.
5. Build the particle demo first.
6. Build the spring demo second.
7. Build the PBD demo third.
8. Build the rigid body demo fourth.
9. Build the FK/IK demo fifth.
10. Merge the needed modules into the final game.
11. Capture screenshots and formulas while building, not at the end.
12. Keep every module demo runnable from a menu.

## 14. Bottom line

The document is asking for a **physics engine first** and a **game second**.

The best way to succeed is:

1. Keep the engine modular.
2. Implement each module as a small demo scene.
3. Build the final game only after the engine pieces are working.
4. Use Python with `pygame` unless your existing rendering stack gives a clear advantage without increasing risk.
