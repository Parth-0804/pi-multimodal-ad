# Primary-source check: assigned Pxxx citations

Fresh, read-only inspection of 25 local PDFs covers 78 citation occurrences counted separately by key. Result and method passages were read in freshly extracted text. P003 and P035 tables that did not extract were opened as rendered images. Record matching to Zotero or its exports is a separate part of the root audit. No thesis or library edits were made.

## Verified numerical comparisons

- **P003:** Table III (PDF page 7) gives 96.1% fusion, 90.2% image and 84.4% audio accuracy. Table V (PDF page 9) gives 96.1% dynamic fusion, 90.5% summation and 92.6% gating. PDF page 6 states 20 frames at 37 fps; PDF page 7 reports 26.2 ms inference. No run-disjoint split is documented in the extracted text.
- **P006:** Table 2 (printed and PDF page 11) gives GMU macro F-score .541 versus concatenation .521. Architecture is in Section 3.1; result discussion is in Section 5.2.
- **P023:** Table 4 (printed and PDF page 4) gives DLinear/Energy MSE .263 without text, .670 with concat-first, and .243 with CFA. Values are averaged across four forecasting horizons.
- **P026:** Table 3 (PDF page 7) gives intact I-AUROC/P-AUPRO .9788/.9901 and missing-3D .9330/.9586. Aggregation alternatives retain the evidence sources; the separate missing-3D row does not establish adaptive-versus-static absence superiority.
- **P033:** Table 4 (printed and PDF page 10) gives local M3DM .779 and add-on .800 image AUROC, versus original published M3DM .945. Table 5 (page 11) gives Eyecandies image AUROC .810 to .794, pixel AUROC .963 to .971, and AU-PRO .849 to .870.
- **P035:** Table V (printed page 6661, PDF page 10) gives 2.33 million parameters and 5.65 ms per image. Table IV gives NwfDD 99.87 versus 98.87 in Tables VI–VII: the source inconsistency is present.
- **P045:** Table 1 (printed and PDF page 24) gives MAE 6.6183 for the proposed method, 8.3002 visual, 60.5118 acoustic, 48.4795 Stage-LSTM and 45.0145 Swin-Fusion. The official MATWI baseline of 19 is an external cited reference, separate from the locally retrained comparisons.

## Locator refinements

All locations below refer to the pre-edit Chapter 2 inventory.

| Key and line | Existing postnote | Recommended postnote | Basis |
|---|---|---|---|
| P006, 666 | `Section~3, Table~2` | `Section~3.1, Table~2` | Specific method subsection; result in Table 2 |
| P035, 159 | `PDF p.~10 Tables~IV, VI, VII` | `p.~6661, Tables~IV, VI--VII` | Printed page 6661 is PDF page 10 |
| P035, 188 | `PDF p.~8` | `p.~6659` | Printed page 6659 is PDF page 8 |
| P035, 410 | `PDF p.~10, Table~V` | `p.~6661, Table~V` | Direct table and pagination inspection |
| P035, 1048 | `PDF p.~10, Table~V` | `p.~6661, Table~V` | Direct table and pagination inspection |
| P038, 684 | `PDF p.~3, Eq.~8` | `p.~149226, Eq.~8` | Printed page 149226 is PDF page 3 |
| P051, 755 | `PDF p.~29, Figure~8` | `Figure~8` | Missingness prose is PDF page 29; Figure 8 is on PDF page 30 |

P003 and P031 use viewer indices because the inspected pages lack suitable unique printed page numbers. P026 has an obsolete “Conference ’17, July 2017” template header; this is not its actual publication year. P021, P022, P023, P024, P025 and the MDPI articles have printed page numbers matching viewer indices. P051 is a browser printout: its 29/40 footer is not article pagination. P055 includes a publisher cover: PDF page 6 is printed page 363.

## Resolved version issue

**P017:** The local attachment is arXiv 2207.07048v1 dated 14 July 2022, while the shared bibliography identifies the 2023 *Patterns* article. The final 2023 full text was subsequently retrieved through NCBI’s BioC endpoint for [PMC10499856](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/). Its title, authors, 2023 year, *Patterns* 4(9), article 100804 and DOI match the final record.

The final article’s Results taxonomy, particularly L1, L1.2, L1.3 and L3.2, explicitly addresses preprocessing and feature-selection leakage and dependence across training/test units. The later model-info-sheet section reiterates separation throughout preprocessing, modeling and evaluation. These passages support the existing general claims in Chapters 1–2. Retain the final-article P017 key; preserve the note that the local attachment is an earlier preprint. No final PDF page number is asserted. The canonical HTML returned a browser challenge, but the NCBI full-text endpoint supplied the final article successfully. Retrieval URL and SHA-256 are recorded in the JSON report.

There are no remaining unsupported claims among this subagent’s assigned citations, within the scope of these source checks.

## Other methodological checks

P005 and P016 support transferable missing-modality mechanisms. P008 supports confidence failures under shift. P009 supports graded reproducibility assurance. P011, P013 and P034 support the representation descriptions. P022 explicitly trains an estimator of corruption intensity and acknowledges difficulty and imbalance as competing sources of uncertainty. P024 combines RGB-depth representations and point-cloud priors; the physical-source-count distinction is an architectural interpretation.

P025 uses report and mask supervision before assessment on held-out categories or datasets and defines its self-consistency metrics. Its input-subset presentation does not fully specify the shared checkpoint and exposure protocol. P026 and P033 use target-domain normal memory or calibration rather than demonstrating unchanged-model generalization. P031 reports optimal-threshold pixel F1. P036 supports conditional evaluation of attention explanations. P038 Equation 8 uses a learned scalar without an explicit sample-quality input. P045 loss weights allocate training objectives. P051 varies incomplete federated clients. P055 supports Brier and logarithmic forecast scoring.

Full citation passages, PDF hashes, pagination mapping and scoped findings are in `claims_papers.json`.
