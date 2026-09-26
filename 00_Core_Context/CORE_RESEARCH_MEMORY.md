# Core Research Memory

## User research line

The user's long-term research line is urban visual intelligence and geographic spatial intelligence, centered on how humans or agents perceive, understand, remember, and navigate urban environments.

The most relevant themes are:

- street-view visual representation;
- urban navigation / vision-language navigation;
- landmarks as navigation-useful and cognition-useful cues;
- cognitive maps and spatial memory;
- object-level, structural, text/sign, and scene-level visual cues;
- city-scale spatial understanding;
- VLM / agent cue grounding and cue selection;
- active evidence acquisition only when useful;
- interpretable spatial evaluation.

## Current research orientation

The current project should start from the user's own urban navigation and city understanding questions, not from mechanically applying popular spatial intelligence frameworks.

The core question is:

> Which visual or spatial cues in street-view environments become navigational landmarks, and how do these landmarks anchor a cognitive map that supports localization, orientation, place memory, and route decisions?

## Functional definition of landmarks

In this project, landmarks are defined functionally:

> A landmark is any object-level, structural, textual, scene-level, or atmospheric urban cue that helps a human or agent reduce spatial uncertainty, localize, orient, remember places, choose road edges, or understand the surrounding environment during navigation.

This definition means landmarks are not limited to famous buildings or named POIs. They may include:

- salient objects;
- road intersections;
- distinctive facades;
- traffic signs and shop signs;
- street width and enclosure;
- vegetation or openness;
- commercial atmosphere;
- repeated but recognizable scene clusters;
- transitions between urban visual fields;
- visual cues that distinguish one route decision from another.

## Relationship to GeoSI and cognitive map

Geographic Spatial Intelligence / GeoSI remains the larger framing, but the current work should be task-driven and empirically grounded.

The key scientific idea is:

> Landmarks are not only local visual cues for action. They can also serve as anchors in a cognitive map, organizing how humans or agents remember, connect, and reason about urban space.

## Research structure

Treat the work as one integrated research program with expandable modules:

1. Landmarkness estimation at street-view nodes  
   What makes a visible element function as a landmark?

2. Landmark-to-edge alignment at intersections  
   How does a landmark support a road choice or direction judgment?

3. Landmark-anchored cognitive map evaluation  
   How do landmarks, route edges, and scene-level fields support place memory, route recall, and spatial understanding?

4. Optional closed-loop navigation extension  
   Only after the above mechanisms are established.

## What should not happen

- Do not start from a broad GeoSI theory without concrete street-view tasks.
- Do not mechanically imitate active-exploration papers.
- Do not make “active” the paper's main selling point.
- Do not make UrbanHue the protagonist of the new project.
- Do not reduce the work to a pure VLM leaderboard.
- Do not claim that landmarks or cognitive maps are newly proposed.
- Do not define landmarks independently of navigation or spatial cognition.
- Do not overcomplicate the first prototype with full continuous navigation.
