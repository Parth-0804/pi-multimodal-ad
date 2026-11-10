# Independent visual review package

Extract the main ZIP and open `index.html` in a browser; all links work offline.
The main ZIP is suitable for upload for an independent review. Its source key
is intentionally withheld in a SECOND archive, `INDEPENDENT_VISUAL_REVIEW_UNBLINDING.zip`.
The expanded package's `UNBLINDING/` directory contains the same key. Do not
upload/open that archive or directory before the reviewer has saved observations.

Review B001–B010 across overhead (`cam_high`), front (`cam_low`), and left/right
wrist views. Each view contains sixteen original selected frame indices in full
and enlarged-context contact sheets, a motion preview, and sixteen 640×480
enlarged-context PNGs for closer inspection. Full-resolution contact sheets are
960×840; sensor plots are 1320×840. Fixed camera crops can exclude the target;
the full view and preview remain available. Enlarging does not create physical detail.

Complete one row per example/view in `RESEARCHER_VISUAL_REVIEW_SHEET.csv`:
identify object and target; describe observed motion/phase; judge failure
visibility yes/no/uncertain with a concrete observation; estimate event times
in original episode seconds; rate confidence 1–5, occlusion and camera utility;
flag force-only or visually ambiguous cases. Report uncertainty rather than
inferring contact forces, submillimetre mating success or hidden causes.
Fourteen traces are observed position feedback, with units not declared in
the release; commands are excluded from these plots. No physical latency
calibration or independent human visual certification is claimed.

Save the completed sheet with reviewer identity/date under a NEW filename.
Only then obtain the separate source key and compare the observations with
native annotations. Keep independent observations distinct from source labels.
An LLM review must be identified as an LLM assessment, not a human review or
original annotation. All forty human assessment rows are currently blank.

These diagnostic windows differ in duration and lack phase-matched normal
controls. The masked gallery does not establish controlled blinding, classifier
accuracy, early warning, or valid binary targets. Existing pilot examples are
development material; future evaluation needs fresh held-out recordings.

`BLINDED_FRAME_MANIFEST.csv` retains index/time/crop/hash without source labels.
`PACKAGE_FILE_MANIFEST.json` records immutable derivative identities.
The separate key retains original repository revisions, LFS source references,
native annotations, episode/video offsets and exact selected-frame mappings.
Original multi-gigabyte recording chunks and duplicate full-frame PNGs are
omitted; no re-encoding or image editing was performed in this packaging step.
