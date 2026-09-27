# Completion implementation and validation notes

- All downstream analysis was implemented before inspecting corruption outcomes.
  Implementation commits: `8917cdd`, `c043125`, `378d607`, `b126f99`.
- REASSEMBLE tests passed: 60 in 9.24 seconds; `pip check` found no broken
  requirements; `git diff --check` passed before implementation commits.
- A synthetic report-assembly smoke check generated the complete tables, figures
  and narratives in an explicitly marked `/tmp/reassemble_SYNTHETIC_report_smoke_*`
  directory. These are not study results and are not thesis artifacts.
- The first synthetic smoke attempt lacked Git context after changing into its
  temporary directory. Supplying the existing repository's Git directory to that
  test process fixed the harness; no scientific procedure or output was changed.
- Before actual execution, reporting was completed with all-five-fold parameter
  maxima, the concatenation head's actual parameter composition, explicit warm
  component throughput, calibration contrasts, static fusion coefficients,
  cross-study evidence mapping and the requested twelve completion items.
- Intentional interruption/resumption of initial serial extraction is documented
  separately in the Section 3 run's `failures_and_corrections.md`.
- Further execution corrections, if any, will be appended here and their original
  attempt logs retained. No historical Section 1/1B/2 output is overwritten.

## Final claim review correction

The initial generated evidence map used a generic INCONCLUSIVE status for all
non-positive robustness classes. Four noise comparisons (V1/F5, V1/F6, S1/F5,
S1/F6) have negative paired AP and degradation-advantage intervals and a failed
adaptation criterion, so their tested positive robustness hypothesis is marked
FALSIFIED in the reviewed map. The original generated map is retained at
`review/FINAL_EVIDENCE_MAP.generated.md`. No metric, model, criterion or historical
Section 1/1B/2 evidence was changed. Remaining B/C comparisons stay inconclusive
about predictive benefit. The generator now reproduces the reviewed status rule.
