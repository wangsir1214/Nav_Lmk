# Cognitive Map Framework

## Conceptual position

This project treats cognitive maps as task-relevant, landmark-anchored internal or external representations of urban space.

A cognitive map in this project is not:

- a complete metric map;
- a SLAM reconstruction;
- a road graph alone;
- a list of visual objects;
- a VLM text description.

It is:

> a structured representation that links places, directions, landmarks, routes, and regions in a way that supports spatial understanding and navigation.

## Operational definition

A landmark-anchored cognitive map can be represented as a graph:

```text
street-view node
→ visible landmark anchors
→ landmark directions / azimuths
→ candidate road edges
→ route memory
→ scene-level or area-level identity
```

## Point–line–area structure

### Point: street-view node

At a street-view node, the audit first uses four fixed FOV=90-degree views to
identify landmark candidates. A formal direction task uses route-aligned views
reprojected from the preserved ERP source.

Questions:

- What is visible here?
- Which elements are distinctive, describable, stable, and navigation-relevant?
- Which elements can serve as memory anchors?

### Line: road edge / route segment

A landmark becomes action-relevant when it aligns with a road edge or direction.

Questions:

- Which outgoing edge does this landmark support?
- Does the landmark reduce ambiguity between multiple candidate directions?
- Can the landmark be used in route instructions?

### Area: scene field / district / cognitive region

Multiple landmarks and scene-level cues can form an area-level cognitive structure.

Questions:

- Does a scene cluster create a recognizable place identity?
- Do repeated cues define a corridor, square, commercial street, or residential zone?
- Does this area-level identity help route memory or place recognition?

## Main mechanism

The proposed mechanism is:

```text
visual cue
→ landmarkness
→ cognitive anchor
→ edge / route / area relation
→ spatial understanding and navigation support
```

## Evaluation targets

A landmark-anchored cognitive map is useful if it improves or explains:

- place recognition;
- orientation judgment;
- road-edge selection;
- route instruction generation;
- route recall;
- ambiguity detection;
- recovery from wrong turns;
- human-model agreement in landmark selection.
