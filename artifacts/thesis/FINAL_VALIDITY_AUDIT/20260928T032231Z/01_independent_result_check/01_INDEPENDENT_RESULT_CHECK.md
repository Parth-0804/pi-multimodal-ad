# Independent numerical result check

Separate NumPy score-tie implementation; no project report/metric wrappers imported. Synthetic tests precede this execution.

216 full-precision core metric comparisons, 30 paired AP/AUROC/Brier comparisons and 8 PHM error comparisons match tolerance 1e-08. Historical 2000-draw paired intervals reproduce with seed20310927; invalid draws are counted, never redrawn.

| contrast | metric | estimate | lower_95 | upper_95 | status |
| --- | --- | --- | --- | --- | --- |
| F2 minus U1 | AUPRC | 0.017906682072462543 | 0.008602699847244996 | 0.028284279537387328 | VERIFIED_NUMERICALLY |
| F2 minus U1 | AUROC | 0.015643803235371845 | 0.006029889881454304 | 0.025465087523209296 | VERIFIED_NUMERICALLY |
| F2 minus U1 | Brier | -0.0020051354943943223 | -0.003098508822344915 | -0.0009078408941701413 | VERIFIED_NUMERICALLY |
| F6 minus F2 | AUPRC | -0.00594266081022099 | -0.024795788360732665 | 0.013694501544008706 | VERIFIED_NUMERICALLY |
| F6 minus F2 | AUROC | -0.01944506468740481 | -0.028800779228553 | -0.010238936693967287 | VERIFIED_NUMERICALLY |
| F6 minus F2 | Brier | 0.0022679135799594102 | 0.000661157130353128 | 0.003940101689015357 | VERIFIED_NUMERICALLY |
| V1_0.1:F5 minus V1_0.1:F2 | AUPRC | -0.26749270054252994 | -0.31417570260510264 | -0.22272833136395517 | VERIFIED_NUMERICALLY |
| V1_0.1:F5 minus V1_0.1:F2 | AUROC | -0.13171810665909678 | -0.17083471876907624 | -0.09166897608827855 | VERIFIED_NUMERICALLY |
| V1_0.1:F5 minus V1_0.1:F2 | Brier | 0.07433160728453364 | 0.024677835440999548 | 0.12451992130317728 | VERIFIED_NUMERICALLY |
| V1_0.1:F6 minus V1_0.1:F2 | AUPRC | -0.26879142664227573 | -0.3138666514941393 | -0.22464619288246054 | VERIFIED_NUMERICALLY |
| V1_0.1:F6 minus V1_0.1:F2 | AUROC | -0.14716989244579903 | -0.17835737994510154 | -0.11505506954218846 | VERIFIED_NUMERICALLY |
| V1_0.1:F6 minus V1_0.1:F2 | Brier | 0.0520429769766067 | 0.013493782673159758 | 0.09066420987708111 | VERIFIED_NUMERICALLY |

Identity evidence: sealed inventory/cohort, per-record feature row maps, explicit per-fold rows and documented condition-generation order. Legacy NPZs do not embed IDs. All audit tables carry explicit composite IDs and are joined by them. This is a provenance-bound numerical check, not independent acquisition validation.

Complete-loss probabilities and saved decisions equal the surviving calibrated branch, including its fold-specific threshold. Normalized masked scalar-logit weights become exactly zero/one; frozen remaining-branch output has no learnable gate-only path. This is structural fallback, not a statistical improvement or information recovery.

PHM uses current v3 run-level targets, 20 runs and the actual experiment-disjoint loop. The image reference row is explicitly NOT LOEO. Stale v2/fixed-split fields in the retained config do not override the actual verified inputs and grouping. The old paired ΔMAE is a bootstrap mean, not the empirical difference of displayed means. No PHM raw files were recovered or revalidated. Fitting-scope coverage is separately reported in fitting_scope_trace.md.

Point/interval reproduction does not erase adaptive study/model selection or establish independent confirmation.
