# Portfolio Polish Plan

## Objective

- Make this repo portfolio-grade via engineering quality, consistency, and presentation.
- Do not deviate from the current engine and demo scope.

## Current Implemented State (2026-04-20)

- Runnable launcher demos: `particle`, `spring`, `softbody`, `rigidbody`.
- `demos/pbd_demo.py` and `demos/kinematics_demo.py` are still placeholders.
- FK helper logic exists in `engine/kinematics.py`; IK solver is not implemented.
- No pytest suite or CI workflow exists yet in this repo.
- Capture pipeline exists and has particle assets in `captures/`.

## Scope Guardrails

- 2D only.
- Keep current runnable demos.
- No large architecture rewrites.
- PBD/FK/IK remain next-phase items

## Milestones

- [ ] M1 Demo consistency and UX polish
- [ ] M2 Engine/docs cleanup and interface polish
- [ ] M3 Minimal strict quality gate (pytest + CI)
- [ ] M4 Portfolio presentation assets and final README pass

## Task Board (Step-by-Step)

- [ ] T1 Standardize controls across implemented demos (Esc/Space/R/help)
  Owner:
  Planned Commit Message:
  Done When: All implemented demos expose consistent core controls and help visibility.
  Evidence:

- [x] T2 Ensure direct run entry (`if __name__ == "__main__": run()`) where missing
  Owner:
  Planned Commit Message:
  Done When: Each implemented demo can run both via launcher and direct file execution.
  Evidence: `demos/particle_demo.py`, `demos/spring_demo.py`, `demos/softbody_demo.py`, `demos/rigidbody_demo.py`.

- [ ] T3 Normalize overlays and runtime parameter visibility
  Owner:
  Planned Commit Message:
  Done When: Overlays consistently show state, counts, and key physics toggles/coefficients.
  Evidence:

- [x] T4 Sync roadmap/status docs with actual repo state
  Owner:
  Planned Commit Message:
  Done When: `README.md`, `PROJECT_IMPLEMENTATION_STEPS.md`, and docs pipeline/plan files match current implementation.
  Evidence: Updated on 2026-04-20 to align demo/module status and development order.

- [ ] T5 Add `main.py --list` and short demo descriptions
  Owner:
  Planned Commit Message:
  Done When: `python main.py --list` prints demo keys plus one-line descriptions.
  Evidence:

- [ ] T6 Add pytest setup and first core tests (math2d + particle)
  Owner:
  Planned Commit Message:
  Done When: Core tests exist and pass locally via `pytest`.
  Evidence:

- [ ] T7 Add collision/rigidbody regression sanity tests
  Owner:
  Planned Commit Message:
  Done When: Basic deterministic rigidbody/collision checks are covered by tests.
  Evidence:

- [ ] T8 Add launcher smoke tests
  Owner:
  Planned Commit Message:
  Done When: Tests verify launcher imports demos and discovers runnable entries.
  Evidence:

- [ ] T9 Add GitHub Actions test workflow
  Owner:
  Planned Commit Message:
  Done When: CI runs tests on push/PR and reports pass/fail status.
  Evidence:

- [ ] T10 Capture screenshots for all implemented demos
  Owner:
  Planned Commit Message:
  Done When: Portfolio-ready screenshots are stored and referenced from README.
  Evidence:

- [ ] T11 Capture one short GIF for flagship demo
  Owner:
  Planned Commit Message:
  Done When: One polished short GIF is exported and embedded in README.
  Evidence:

- [ ] T12 Final README polish and consistency check
  Owner:
  Planned Commit Message:
  Done When: README is accurate, professional, and fully aligned with code/docs.
  Evidence:

## Weekly Checkpoint Log

Week:

Completed Tasks:

Blocked Tasks:

Decisions Taken:

Next 3 Tasks:

## Completion Criteria

- All milestone checkboxes complete.
- Implemented demos run from launcher without errors.
- Tests pass locally and in CI.
- README and planning docs reflect real implementation state.
- Portfolio media section is present and reproducible.

## Deferred (Post-Polish)

- Full PBD implementation.
- FK demo scene.
- IK solver demo.
- Final multi-module game integration.

## Test Plan

1. Markdown renders cleanly on GitHub (headings, checkboxes, code ticks, links).
2. Every task has measurable "Done When" criteria (no vague wording).
3. Task ordering supports incremental execution with no blocked first step.
4. Plan content matches existing repo reality (no claims of finished PBD/FK/IK demos).

## Assumptions and Defaults

1. File path is fixed to `docs/PORTFOLIO_POLISH_PLAN.md`.
2. Tracking style is checklist + milestones.
3. Tooling scope for this polish phase is minimal strict core: pytest + one CI workflow.
4. No breaking changes to current user-facing demo commands in this phase.
