# Approved null metadata guard repair

The parent batch runner compared a computed numeric reward amplitude against a missing (null) reference. The approved R1 uses explicit `is not None`, retaining equality checks for real numeric references including zero. It additionally verifies a finite runtime number and records it. The original FixedGoalGame.on_reset -> _shortest_paths calculation was unchanged.

001/002/024 initialization returned26/23/51. Ten guard tests passed; no model forward/navigation in these tests. All48 formal trajectories restarted independently under one revised source. The old partial001 was not merged.42 references were missing and6 were non-null; every runtime value matched the historical formal Full record.

Executed runner SHA-256: `a17335a574e32ee2993cefbdf15ee16ca226f3477acd77b71c908093af96223c`. Full patch and original execution evidence are retained privately and indexed by hash.
