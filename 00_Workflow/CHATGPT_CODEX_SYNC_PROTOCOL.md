# ChatGPT ↔ Codex Sync Protocol

ChatGPT web and local Codex do not automatically share complete conversation histories.

Use Markdown files as the synchronization layer.

## ChatGPT web → Codex

ChatGPT web is used for:

- research direction;
- experiment design;
- paper logic;
- interpretation of results;
- next-step planning.

After a web discussion, update or send these files to Codex:

```text
00_Core_Context/CORE_RESEARCH_MEMORY.md
01_Navigational_Landmarkness_Cognitive_Map/PROJECT_CONTEXT.md
01_Navigational_Landmarkness_Cognitive_Map/COGNITIVE_MAP_FRAMEWORK.md
01_Navigational_Landmarkness_Cognitive_Map/EXPERIMENT_DESIGN.md
01_Navigational_Landmarkness_Cognitive_Map/DECISIONS.md
01_Navigational_Landmarkness_Cognitive_Map/TODO.md
01_Navigational_Landmarkness_Cognitive_Map/CODEX_TASKS.md
```

Prompt for Codex:

```text
请先读取根目录 AGENTS.md，
再读取 00_Core_Context/CORE_RESEARCH_MEMORY.md，
以及 01_Navigational_Landmarkness_Cognitive_Map 下的 PROJECT_CONTEXT.md、COGNITIVE_MAP_FRAMEWORK.md、EXPERIMENT_DESIGN.md、DECISIONS.md、TODO.md、CODEX_TASKS.md。

当前只执行 01_Navigational_Landmarkness_Cognitive_Map。
请先复述当前研究目标和任务边界，再开始执行。
```

## Codex → ChatGPT web

Codex is used for:

- repository inspection;
- data schema checking;
- code modification;
- experiment execution;
- bug fixing;
- logging;
- generating result tables and figures.

After Codex work, send these files back to ChatGPT web:

```text
01_Navigational_Landmarkness_Cognitive_Map/WORKLOG.md
01_Navigational_Landmarkness_Cognitive_Map/RESULTS_SUMMARY.md
01_Navigational_Landmarkness_Cognitive_Map/ERROR_LOG.md
01_Navigational_Landmarkness_Cognitive_Map/TODO.md
01_Navigational_Landmarkness_Cognitive_Map/DECISIONS.md
outputs/tables/*.csv
outputs/figures/*.png or *.pdf
outputs/cases/*.jsonl or *.md
```

Prompt for ChatGPT web:

```text
这是 Codex 最近一次执行后的 WORKLOG、RESULTS_SUMMARY、ERROR_LOG、TODO 和实验输出。
请基于这些结果判断：
1. 当前实验是否支撑 navigational landmarkness / cognitive map 研究问题；
2. 结果有什么科学解释；
3. 哪些是代码问题，哪些是研究设计问题；
4. 下一轮应该让 Codex 做什么；
5. 是否需要更新 PROJECT_CONTEXT / COGNITIVE_MAP_FRAMEWORK / EXPERIMENT_DESIGN / DECISIONS。
```

## Rule

Do not sync full raw transcripts unless debugging requires it. Sync project-state files instead.
