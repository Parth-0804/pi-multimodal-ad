# Independent grouping audit

Investigation: `REBOOT/runs/20261028T192832Z-research-blockers-v2`. Snapshot: 2026-10-28T19:43:33.517787+00:00. Original pilot and published bytes remain unchanged.


**No scientifically admissible supervised split can be constructed.** The verified binary cohort has 0 examples, 0 positive, 0 negative and 0 eligible groups. The richer inventory now includes independently verified identities for the defective-index USB-C collection; it does not establish labels or physical independence.

Across all parseable original episode indexes, exact signatures combine the original four video LFS hashes, per-view start/end timestamps and episode length. There are exactly 60 alias clusters of size two: sample episodes 0–59 and the full cylinder-recovery copies. All 18 sample chunks are shared. No additional exact episode-signature alias was detected in the 2,103 parseable entries. The 33 independently recovered USB-C identities lack original video-offset metadata and cannot be included in that media-alias test. Alias-collapsed inventory ceiling: 2,076 (1,090 expert-name candidates and 986 recovery-name candidates; these are not class labels). Full numeric trajectory equality was not tested across this terabyte-scale release, so further repetitions/near-duplicates remain unknown.

There are 482 original video hashes referenced by more than one episode identity. A connected-component audit binds all episodes sharing any camera's original chunk, including aliases, into 58 conservative components over parseable index entries. Different adjacent episodes in a shared media chunk are not necessarily duplicates; they must remain bound in a conservative source-chunk split unless actual physical recording boundaries are established. Component IDs are derived bookkeeping, not inferred collection sessions. USB-C's 33 identities are not assigned fabricated chunk groups. Evidence: run `reports/EXACT_EPISODE_MEDIA_ALIASES.json`, `ORIGINAL_CHUNK_COMPONENTS.json` and row-level coverage CSV.

Sixty unique annotated recordings carry two operator strings: `op-01`=58 and `op-00`=2. Native session strings are `2026-04-15`=59 and `initial`=1. `initial` is not a verified recording date/session. Two thousand sixteen other inventory identities have no session string. These strings do not establish independent physical acquisitions, and neither upload date, commit date, elapsed frame timestamp, task name nor local filename may substitute. Expert/recovery pair IDs and repeated-rollout identities are absent. Thus verified physical sessions and verified expert/recovery pairings are both 0, rather than a claim that all recordings came from one session.

The 18 task names below are object/direction normalization of repository/native descriptions. They are plausible task inventory groups, not sessions. Distinct language prompts are not automatically distinct physical tasks. Only one task has native machine-readable annotations; it still has no admitted binary classes.

| Inferred task | Inventory ceiling | Expert-name / recovery-name | Native annotated unique | Verified + / − / unknown |
|---|---:|---:|---:|---:|
| 16mm-bar:install | 123 | 61 / 62 | 0 | 0 / 0 / 123 |
| 16mm-bar:remove | 78 | 60 / 18 | 0 | 0 / 0 / 78 |
| 16mm-cylinder:install | 122 | 62 / 60 | 60 | 0 / 0 / 122 |
| 16mm-cylinder:remove | 120 | 60 / 60 | 0 | 0 / 0 / 120 |
| HAN10E:install | 120 | 60 / 60 | 0 | 0 / 0 / 120 |
| HAN10E:remove | 120 | 60 / 60 | 0 | 0 / 0 / 120 |
| M12:install | 120 | 60 / 60 | 0 | 0 / 0 / 120 |
| M12:remove | 120 | 60 / 60 | 0 | 0 / 0 / 120 |
| NEMA1-15:install | 121 | 61 / 60 | 0 | 0 / 0 / 121 |
| NEMA1-15:remove | 120 | 60 / 60 | 0 | 0 / 0 / 120 |
| RCA:install | 120 | 60 / 60 | 0 | 0 / 0 / 120 |
| RCA:remove | 60 | 60 / 0 | 0 | 0 / 0 / 60 |
| RJ45:install | 123 | 63 / 60 | 0 | 0 / 0 / 123 |
| RJ45:remove | 124 | 63 / 61 | 0 | 0 / 0 / 124 |
| USB-A:install | 120 | 60 / 60 | 0 | 0 / 0 / 120 |
| USB-A:remove | 121 | 60 / 61 | 0 | 0 / 0 / 121 |
| USB-C:install | 123 | 60 / 63 | 0 | 0 / 0 / 123 |
| USB-C:remove | 121 | 60 / 61 | 0 | 0 / 0 / 121 |

| Candidate protocol | Eligible examples (+/−) | Eligible groups | Every-fold class support | Overlap / conclusion |
|---|---:|---:|---|---|
| Session-disjoint | 0 (0/0) | 0 physical | Cannot evaluate: no folds | Physical overlap unknown; two native strings cannot establish independence |
| Task-disjoint | 0 (0/0) | 0 labelled; 18 inventory | Cannot evaluate: no folds | Task-name partition could have zero name overlap, physical overlap remains unknown |
| Leave one task out | 0 (0/0) | 0 labelled; 18 inventory | Each prospective task has 0 admitted positive and negative test examples; remaining tasks have 0 admitted train examples | No valid LOTO experiment; future task generalization claim differs from session generalization |
| 3 outer × 2 inner grouped CV | 0 (0/0) | 0 verified eligible | No outer/inner class support can be certified | No folds materialized, hence overlap is undefined rather than invented as zero |

`VERIFIED_SPLIT_FEASIBILITY.json` records counts and admission failures for all protocols plus each prospective held-out task's zero eligible class support. `per_fold_class_support` and actual fold overlap are null because no legitimate folds exist; zeros would falsely imply executed empty splits. No random frame split, substituted group identity, fold reduction or seed search was used. The 58 source-chunk components do not rescue absent labels or certify session independence.
