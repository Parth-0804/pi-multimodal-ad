# ViFailback independent multimodal evaluation

The researcher authorized full implementation, three-camera 16-timestamp inputs,
three model seeds and 100-epoch visual experiments. This project is currently
being implemented; no ViFailback neural result is established by this README.

Historical evidence remains under
`DATASET_RESEARCH/VIFAILBACK_VERIFICATION/`. The initial preservation commit is
`9414da8f8ecc73299e442609f6e41e437dce9ec7`. No original data was moved or copied.
The conservative starting manifest contains 4,384 episodes, 3,755 native failures,
629 native no-failure episodes and 99 canonical tasks. Final eligibility still
depends on actual three-camera video QC.

The domain folders follow the existing MSM organization. Implementation lives in
`src/vifailback/`; scripts bootstrap both this package and reusable repository
code. Configuration paths are repository-relative. Raw video payloads, live
training state and large generated arrays are ignored by Git.

Current commands, from repository root:

```bash
ma_thesis_env/bin/python -B -m pytest -q VIFAILBACK/tests
ma_thesis_env/bin/python -B VIFAILBACK/scripts/acquire_videos.py
```

`configs/experiment.json` fixes all three camera streams, sixteen synchronized
temporal positions per camera, 100 scheduled epochs, seeds 42/123/20261023 and
three outer task groups with three inner grouped OOF partitions. The new 3×3
design satisfies the current request's minimum and replaces the earlier draft
5×4 design; no epochs are reduced and no model results choose the split count.
The three-camera input means 48 RGB images at 16 times, not 32 timestamps.

The existing REASSEMBLE 75-fit study has priority. ViFailback must not use its GPU
until that study has completed and the GPU is idle. CPU acquisition, QC,
preprocessing, implementation and independently valid baseline work can proceed.
Long-run status and exact resumable commands will be recorded in
`RESEARCH_COMPLETION_STATUS.md` and `10_final_research_reports/` as stages finish.
