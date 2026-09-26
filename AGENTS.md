# Global AGENTS.md

This is the root instruction file for Codex.

## Current active project

The only active project is:

`01_Navigational_Landmarkness_Cognitive_Map`

Do not expand into other projects unless the user explicitly asks.

## Mandatory context files

Before doing research or coding tasks, read:

1. `00_Core_Context/CORE_RESEARCH_MEMORY.md`
2. `00_Core_Context/THEORY_OF_SPACE_TRANSFER.md`
3. `00_Core_Context/PANORAMIC_PAPERS_TRANSFER.md`
4. `00_Core_Context/URBANHUE_POSITION.md`
5. `00_Workflow/CHATGPT_CODEX_SYNC_PROTOCOL.md`
6. `00_Workflow/REMOTE_SSH_VSCODE_WORKFLOW.md`
7. the active project's `AGENTS.md`
8. the active project's `PROJECT_CONTEXT.md`
9. the active project's `COGNITIVE_MAP_FRAMEWORK.md`
10. the active project's `EXPERIMENT_DESIGN.md`
11. the active project's `DECISIONS.md`
12. the active project's `TODO.md`

## Research principles

- Use Chinese for research planning, explanation, and paper logic unless the user asks for English.
- The user's research line is urban visual intelligence, street-view representation, urban navigation, landmarks, and geographic spatial understanding.
- The current project must be driven by the scientific question of navigational landmarkness and cognitive maps, not by mechanically imitating popular active-exploration frameworks.
- Define landmarks functionally: landmarks are navigation-useful and cognition-useful cues.
- Do not claim that landmarks or cognitive maps are newly proposed concepts.
- The novelty should be in operationalization, data construction, evaluation design, and empirical findings.
- Do not reduce the work to a pure VLM leaderboard.
- Large models are tools, probes, or agent implementations, not necessarily the scientific target.
- APRS / EAGLE-360 are technical inspirations for panoramic evidence organization and localization; do not make them the main framework.
- UrbanHue is archived context and review-response support; do not make it the protagonist of the current project.
- When the task involves figures, read `00_Standards/FIGURE_STYLE_GUIDE.md`.
- When the task involves paper writing, read `00_Standards/PAPER_WRITING_GUIDE.md`.
- When the task involves code release or reproducibility, read `00_Standards/CODE_REPRODUCIBILITY_GUIDE.md`.

## Execution principles

- Prefer small runnable experiments over abstract planning.
- First-stage image input should default to four FOV=90° perspective views per panorama; full ERP panorama is optional raw source/future extension.
- Before modifying code, do repository inventory and confirm paths.
- Preserve commands, file paths, outputs, and errors in logs.
- After every session, update `WORKLOG.md`, `RESULTS_SUMMARY.md`, `ERROR_LOG.md`, and `TODO.md`.
- If a new research or engineering decision is made, update `DECISIONS.md`.
- Do not modify `99_Archive/UrbanHue/` unless the task explicitly concerns UrbanHue review response, revision, or archival update.
