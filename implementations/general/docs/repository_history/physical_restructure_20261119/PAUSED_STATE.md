# Changes in structure — paused work

The researcher requested pausing further restructuring and uploading the current
eligible repository changes as “Changes in structure”.

The physical moves are complete: 39 verified small source/configuration/document
roots and the explicitly approved 172 evidence roots were renamed. All 154,090
moved regular files retained their recorded device, inode and size immediately
after the moves. Existing scientific cross-reference symlinks were rebased; 87
old compatibility/navigation aliases were removed. No replacement old-path
aliases were created. Listed protected raw roots and active-job dependencies
retained their original paths.

The working-code path patch and packaging update were **not applied**. Automatic
approval review requested stronger path/import-semantic checks for that patch.
Consequently, imports, commands and navigation may still reference former paths.
The repository is a work in progress, not a validated runnable release. The
earlier 329 passing tests predate these final moves; they do not validate this
paused state. No model experiment was launched or interrupted.

Resume by reviewing the pending path patch, updating package discovery and test
paths, fixing current navigation, checking ignore coverage and running the
documented synthetic/package checks. Preserve frozen evidence contents and use
the relocation mapping when interpreting its historical paths.

- [Approved bulk plan](BULK_MOVE_PLAN.md)
- [Researcher approval](BULK_MOVE_APPROVAL.json)
- [Executed bulk moves and identity checks](EXECUTED_BULK_MOVES.json)
- [Small source/configuration moves](SMALL_MOVE_MANIFEST.json)

Git publication excludes raw data, credentials, environments, caches and large
generated/model artifacts. Local ignored content remains on disk; a Git commit
does not establish separate retention or recovery of that content.
