# Architecture planning tasks

## Autopilot-full steps

- [x] The operator's gates come first.
- [ ] Spawn one owner per PR, and keep its work where a replacement can find it.
- [ ] Run owners in parallel off trunk, never stacked.
- [ ] Swarm-verify once.
- [ ] The owner merges only what you verified, tested on the trunk it lands on. Skip. The user requested a plan review before formal migration or merge.
- [ ] Run the root layer. Skip autonomous merge approvals. Retain independent artifact review and exact-source validation.
- [ ] Stand down at once on the operator's stop.

## Architect phases

- [ ] Ground
- [ ] Sketch
- [ ] Agree. The deliverable is a reviewable plan, not a formal migration.
- [ ] Implement. Prototype only under the current grant.
- [ ] Scrap. Replace a prototype if its constraints fail.

## Arena phases

- [ ] Frame
- [ ] Fan out
- [ ] Cross-judge
- [ ] Pick
- [ ] Graft
- [ ] Verify

## Investigation scope

A repeated mechanism needs distinct evidenced runs or affected paths. Count run failures, affected paths and corrective commits separately. Multiple paths fixed by one commit are not multiple correction events. Broader event families remain separate from repeated mechanisms. Current suspicious structure is an observation until history or a reproduced defect supports it. Compare two complete ownership designs with the same failure probes. Keep all prototype changes under this planning directory. Generate and execute a repository-local verification skill against the real CLI. Separate unavailable Apple execution from portable logic, and never relabel skipped or blocked work as passing.

Inputs are a commit graph, original diffs, review records and runnable commands. Outputs are incident records, a measured structural inventory, two candidate sketches, replay logs, a generated verification skill and one migration plan. No formal package move, production import rewrite, gate relaxation, force push, upstream write, release or merge is authorized by this plan task.

The Cursor plugin source is pinned at 00d5decc6f05669044fd092dec73da9ef6f7eec0. This runtime executes its instructions from source. It does not register native Cursor slash commands. Its default Claude and Grok agent models and Task API are unavailable, so independent inherited-model agents replace those seats. There is no cross-model-diversity claim.
