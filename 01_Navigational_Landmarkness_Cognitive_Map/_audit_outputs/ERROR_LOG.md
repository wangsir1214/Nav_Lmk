# Audit error log

## Current unresolved issues

### 1. Point snapping lacks command-level provenance

The archive contains the exact final graph copy and Paris notebook cells that read
`Line_Points_3.shp` and build/output the graph. It does not contain the command,
QGIS processing history, or script that moved raw GSV points onto roads to create
`Line_Points_1/2.shp`.

Impact: the snapping rule is reproduced exactly from data, but the original tool
and parameter provenance cannot yet be claimed.

### 2. Route actions are provisional

Candidate maneuvers are derived from incoming/outgoing geographic bearings at
audited connector zones. They are not human-verified gold labels.

Impact: no benchmark accuracy claim is currently allowed.

### 3. Historical RL replay is not reproducible yet

Checkpoints exist, but exact checkpoint/config/data/code pairing and fixed-episode
inference are not established. Orientation branches are inconsistent.

Impact: no RL result or visual-dependence claim is currently allowed.

### 4. Hard-coded credentials

At least two historical code paths contain literal service credentials. Values are
not logged here.

Resolution: revoke/rotate, then replace literals with environment or secret-manager
reads before executing historical code.

### 5. Final human suitability scores missing

Codex contact-sheet screening is complete, but user/teacher six-dimension scoring
is pending.

Impact: current Go/Adapt/Replace state is provisional ADAPT.

### 6. Four-view batch script missing

The current 4x640 asset orientation and FOV are output-verified, but the batch
script, interpolation, pitch, and JPEG settings were not found in the archive or
the two Paris Z-drive code roots.

Impact: the assets are usable for review; formal route-aligned derivatives require
a new provenance-complete script.

## Resolved execution issues

- `Z:` is invisible inside the default sandbox but readable through user-approved,
  path-scoped, read-only access. Core Paris assets were scanned successfully.
- PowerShell 5 initially misread UTF-8 JSON through its default local code page;
  explicit `-Encoding UTF8` and Python strict JSON loading both pass.
- Optional plotting packages were absent in the first partial audit; built-in/PIL
  audit renderers were used without network installation.
- Initial PowerShell execution-policy and coordinate-binding problems in the graph
  overview script were fixed.
- Candidate validation passes for 15 routes, 120 steps/panos, 480 images, 120
  headings, and 30 review boards.
- The point snapping result is reproduced for all 3,059 intermediate points; its
  metric-CRS alternative and route-level impact are quantified.
- Google official Tile API `heading`, JavaScript API `centerHeading`, Static API
  metadata, and request-heading definitions are now recorded.
- The archive projection search was moved from a slow PowerShell expression to a
  reproducible Python script after one parser error and one timeout.
- A first review-CSV edit omitted one empty field per row; column-count validation
  found the mismatch before handoff, and the corrected 15 rows all have 27 fields.
