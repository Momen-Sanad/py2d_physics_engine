# 2D Physics Engine

A modular 2D physics engine in Python for the SWGCG 352 course project.

The current scope is engine-first: build the simulation systems as standalone demos before adding any game layer.

## Scope

Planned physics modules:

1. Particle systems
2. Mass-spring systems
3. Position-Based Dynamics (PBD)
4. Rigid body dynamics
5. Forward kinematics (FK)
6. Inverse kinematics (IK)

## Project Structure

```text
.
|-- main.py
|-- requirements.txt
|-- engine/
|   |-- config.py
|   |-- core.py
|   |-- math2d.py
|   |-- integrators.py
|   |-- forces.py
|   |-- collisions.py
|   |-- constraints.py
|   |-- particle.py
|   |-- spring.py
|   |-- pbd.py
|   |-- rigidbody.py
|   |-- kinematics.py
|-- demos/
|   |-- particle_demo.py
|   |-- spring_demo.py
|   |-- pbd_demo.py
|   |-- rigidbody_demo.py
|   |-- kinematics_demo.py
|-- docs/
|   |-- PHYSICS_ENGINE_PIPELINE.md
|-- PROJECT_IMPLEMENTATION_STEPS.md
```

## Current Status

The repository is scaffolded with:

1. Shared engine modules
2. Placeholder demo modules
3. A documented implementation pipeline

The actual runnable simulation scenes are still to be implemented.

## Getting Started

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the entry point:

```bash
python main.py
```

## Recommended Build Order

1. Engine foundation and fixed timestep
2. Particle system
3. Mass-spring system
4. PBD
5. Rigid bodies
6. FK and IK

## Notes

This project is intentionally limited to 2D to keep implementation time under control and improve stability and presentation quality.
