# AGENTS.md for Navigational Landmarkness and Cognitive Map

## Active project

This is the only active research project in this workspace.

## Goal

Build a fast, feasible, scientifically meaningful prototype for studying navigational landmarkness and landmark-anchored cognitive maps in street-view environments.

## Required reading

Before acting, read:

- `../AGENTS.md`
- `PROJECT_CONTEXT.md`
- `COGNITIVE_MAP_FRAMEWORK.md`
- `LANDMARKNESS_SCHEMA.md`
- `LANDMARK_ANCHORED_GRAPH_SCHEMA.md`
- `EXPERIMENT_DESIGN.md`
- `IMAGE_INPUT_POLICY.md`
- `CODEX_TASKS.md`
- `DATA_SCHEMA.md`
- `DECISIONS.md`
- `TODO.md`

## Task boundary

- Use street-view environments and urban navigation as the task context.
- Define landmarks through navigation and cognitive-map function.
- Large models are tools, probes, or annotators, not the research endpoint.
- Active inspection is optional and should only be used as an experimental condition or evidence acquisition cost.
- Do not modify `../99_Archive/UrbanHue/` unless explicitly asked.

## Execution style

- Prefer small runnable experiments.
- First run repository inventory.
- Build data schemas before model-heavy experiments.
- Make CLI scripts configurable.
- Save results in `outputs/`.
- Update `WORKLOG.md`, `RESULTS_SUMMARY.md`, `ERROR_LOG.md`, and `TODO.md` after each session.
