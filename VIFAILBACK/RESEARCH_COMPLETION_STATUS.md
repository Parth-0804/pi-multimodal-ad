# Research completion status

**Active implementation. No ViFailback neural model has been trained yet.**

Completed: preserved the existing investigation in local commit `9414da8f8`;
independently recounted native 5,202 labels and the 4,384-row conservative core;
verified 1,274 original and 5,358 follow-up artifact hashes; implemented selective,
immutable, hash-verified three-camera acquisition with synthetic HTTP tests.

In progress: full three-camera acquisition and video QC; preprocessing, split
lineage, models, fusion, corruption evaluation and independent result validation
remain implementation work. Their completion will be established by artifacts,
not by successful script exit alone.

Resource constraint: one Tesla T4 is occupied by the unrelated REASSEMBLE study.
It showed 4/75 completed fits at the initial resource check. Do not interrupt it.
The ViFailback GPU stage must be scheduled sequentially after that study.

Unchanged historical limitations: task 55 coordinate quarantine; native human
category is not an exhaustive human-presence mask; session/operator identities
and original hardware clock calibration are unavailable. The locked B02 review
remains uncertain regardless of its native failure label.

Read `README.md`, `configs/experiment.json`, and the historical follow-up audit
before interpreting this active project. Local commits only; nothing is pushed.
