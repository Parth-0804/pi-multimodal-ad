# REASSEMBLE: start here

Open one experiment and follow folders **00 → 01 → 02 → 03**. Each folder has a README explaining what enters, what happens, and what comes out.

| Experiment | Input | Learned component | Open |
|---|---|---|---|
| RT-DETR visual baseline | 16 hand-camera frames | Failure classifier on frozen RT-DETR backbone features | [Start here](01_rtdetr_baseline/README.md) |
| PatchTST sensor baseline | 512 × 22 sensor sequence | PatchTST encoder and failure classifier | [Start here](02_patchtst_baseline/README.md) |
| Core fusion | Visual branch + 220 sensor statistics | Two-probability logistic fusion, with other core comparisons | [Start here](03_core_fusion/README.md) |

```text
REASSEMBLE dataset → one annotated action segment
  ├─ 16 hand-camera frames → frozen visual backbone → trained classifier → visual probability
  ├─ 512 × 22 sensor sequence → PatchTST + classifier → sensor probability
  └─ same sensor sequence → 220 statistics → logistic classifier → statistics probability

Core static fusion uses: visual probability + statistics probability
  → logistic fusion → failure probability → fold-specific threshold → predicted outcome

Held-out predictions + recorded outcomes → evaluation → saved result files
```

The three folders use the same layout:

```text
01_rtdetr_baseline/  (also 02_patchtst_baseline/ and 03_core_fusion/)
├── README.md
├── 00_data_overview/
├── 01_data_preprocessing/
├── 02_model/
│   ├── README.md
│   ├── 02.1_functions/
│   ├── 02.2_initial_architecture/
│   └── 02.3_training_and_saved_parameters/
└── 03_model_outputs_and_results/
```

**What these names mean.** `00` defines a sample and its label; `01` converts it to model inputs; `02.1` maps the functions; `02.2` explains the architecture before fitting; `02.3` identifies training decisions and saved parameters; `03` explains predictions and evaluation. `OOF` means out-of-fold: a sample was predicted while its recording was held out of fitting.

**How files are organized.** These are navigation folders over the existing implementation and historical evidence. Clearly named shortcuts are relative symbolic links, so they open the original files without copying them. Read these linked files as evidence: editing a shortcut edits its original. Python implementations stay under `src/reassemble/`; use the function maps to open them. All original names, run paths, imports and manifests remain intact. Historical report links point to their original location so their internal relative links retain their meaning.

**Which experiments are covered.** RT-DETR and PatchTST refer to the frozen core Section 1 run. Core fusion includes the Section 1B static stacker (called F2 in Section 2) and the Section 2 F1–F6 comparisons. Later LongPatchTST, boundary-aware visual pooling, robustness and external studies are separate experiments, outside this layout phase. PHM organization is also a later phase.

**Limits of this guide.** It describes existing code and saved evidence. Creating it did not train, infer, download models, regenerate historical reports or validate models by retraining. Local checkpoints, prediction arrays and presentation images must already exist for their links to work; they are not copied into this folder or made Git-tracked by this change. The navigation manifest records original paths and checksums.

[Navigation manifest](navigation_manifest.json) · [Checks performed](VALIDATION.md)
