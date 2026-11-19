# PHM: start here

Start with **RT-DETR Model 1: frozen-encoder scalar regression**, then follow **00 → 01 → 02 → 03**. This is the first PHM experiment organized in the numbered layout.

[Open the experiment](01_rtdetr_scalar_regression/README.md) · [Follow one real held-out sample end to end](01_rtdetr_scalar_regression/SAMPLE_WALKTHROUGH.md)

```text
Dataset photo → one image-view sample
  ├─ fixed ROI + image heuristic → provisional candidate-area target (%)
  └─ full image → 640×640 RGB → frozen RT-DETR-L → 768 features
       → append extraction latency → 769 inputs → scaling → scalar head
       → inverse target scaling
       → predicted candidate-area percentage

Saved prediction + provisional target → image/tooth/run metrics → result files
```

This particular baseline is image-only; **fusion is not a stage in Model 1**. PatchTST, late fusion, RT-DETR detection and RT-DETR multitask are distinct experiments with their own configurations and evidence. Their numbered walkthroughs are outside this single-experiment phase.

**Review finding:** the actual saved head used 769 inputs: 768 image features **plus extraction latency**. The historical 768-input description is incomplete. See [the implementation discrepancy](01_rtdetr_scalar_regression/KNOWN_IMPLEMENTATION_ISSUES.md) before interpreting the model.

The PHM scalar target is an image-derived, provisional measurement of candidate area, pending human review. It is not a recorded success/failure label, a bounding-box label, or a ground-truth physical damage measurement. Run numbers are identities, not health labels.

The older RT-DETR storybook is a teaching demonstration using a pretrained detector. It should not be used as the evidence path for this trained scalar-head baseline. Use the pinned run linked in this guide. Current source lives in `src/phm2026/`; historical reports may retain old `pi_multimodal_ad` paths.

This layout adds documentation and relative shortcuts over existing evidence. Read linked files as originals: editing a shortcut edits its target. No raw files, source modules, model checkpoints, or historical outputs were moved or renamed. Local evidence must already exist for these shortcuts to resolve; bulk artifacts stay outside Git tracking.

[Validation and known limits](VALIDATION.md) · [Original-path and preservation manifest](navigation_manifest.json)
