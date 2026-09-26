# Theory of Space Transfer Notes

## Position

Theory of Space and related spatial intelligence papers are conceptual references, not templates to mechanically copy.

The user's project should remain grounded in urban navigation, landmarks, and city understanding.

## What to learn

Theory of Space is useful because it emphasizes:

1. Spatial beliefs rather than one-shot perception  
   An agent should not merely classify an image. It should form a belief about where it is, what it faces, which landmarks are useful, and what action is plausible.

2. Construct–revise–exploit  
   An agent constructs spatial understanding from views, revises it when evidence conflicts, and exploits it to act.

3. Partial observability  
   A street-view image is only partial evidence. Navigation decisions often require resolving ambiguity.

4. Evidence acquisition  
   Active viewing or requesting additional context is useful only when it reduces uncertainty for the task.

5. Cognitive map evaluation  
   A meaningful evaluation should test whether the agent's internal or external spatial representation supports localization, orientation, memory, and route decisions.

## How to transfer to this project

Use these ideas to frame urban navigation:

- What spatial belief does the agent need at a street-view node?
- Which landmarks anchor that belief?
- Which landmarks are stable across views or adjacent nodes?
- When does the agent need additional evidence?
- Can the agent revise its decision after seeing a better cue?
- Does the agent know when the current evidence is ambiguous?

## What not to do

- Do not force full active exploration into the first experiment.
- Do not design artificial actions unrelated to street-view navigation or cognitive maps.
- Do not claim this work is a direct implementation of Theory of Space.
- Do not make active exploration the contribution unless the basic landmarkness and cognitive-map relation is already shown.

## Suggested wording

This project is inspired by recent spatial intelligence work that views spatial understanding as the construction and revision of task-relevant spatial beliefs. Rather than directly reproducing active-exploration paradigms, we ground the problem in urban street-view environments and study how navigation-useful landmarks function as anchors for cognitive maps.
