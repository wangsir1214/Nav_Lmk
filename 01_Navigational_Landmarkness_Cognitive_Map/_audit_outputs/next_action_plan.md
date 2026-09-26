# Next action plan

## P0.1 human decision gate

Use the generated route boards and blank `candidate_route_review.csv` to score:

- visual diversity;
- landmark availability;
- spatial relevance;
- task ambiguity;
- intervention feasibility;
- graph/task support.
- task-definition fit and action confidence;
- candidate type and temporal stability;
- super-landmark presence and exclusion reason.

Review the 12 main routes and three Arc controls. Treat
`candidate_route_review_preliminary.csv` only as pre-screening, not as ground
truth.

## P0.2 route and view freeze

After human review:

1. freeze a smaller KEEP set and named control strata;
2. confirm each provisional maneuver at the OSM decision zone;
3. document removal/replacement reasons for rejected cases;
4. generate route-aligned front/right/back/left views from ERP;
5. retain fixed `view_0..3` and raw ERP as provenance.

## P1 minimal experiment

Recommended first runnable study:

```text
P1A human candidate-landmark elicitation
-> freeze task-valid routes and strata
-> P1B learned-route continuation / route-memory choice
-> only then consider landmark interventions
```

The P1B correct edge is defined by the route shown in the learning phase, not by
asking a participant to guess a geometrically mined route from an unfamiliar
intersection.

Do not start with RL. A simple human annotation, retrieval, or classification
baseline can establish whether the cases support the scientific question.

## Deferred until P1 is supported

- VLM candidate generation;
- original/removal/identity/location image interventions;
- checkpoint replay or RL retraining;
- online cognitive-map agent;
- cross-city replacement search.

## Replacement trigger

Search for another dataset only if human review shows that Paris lacks enough
stable, editable, spatially relevant cues after confounded cases are removed.
Use the failed dimension to define the replacement criteria.
