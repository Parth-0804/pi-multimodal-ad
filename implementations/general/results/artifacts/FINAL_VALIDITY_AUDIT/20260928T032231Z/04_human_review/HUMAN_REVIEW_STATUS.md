# Human review status

**PENDING_HUMAN_REVIEW**

No human ratings have been received, invented or inferred by the agent.

Blind package: `../datasets/REASSEMBLE/cache/final_validity_audit/20260928T032231Z/blind_review`. Reviewer A and B sheets contain the same64 cases in different orders. Share only blind_review with reviewers; its clips and sheets omit recorded labels and model outputs. The separate private key is restricted and outside Git.

Export status: READY_FOR_HUMAN_REVIEW. Encoded 64/64 clips; 62.21 MiB.

The thesis author and preferably one other technically informed person should complete sheets independently. Return workflow (only after actual submissions):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. ma_thesis_env/bin/python -B -m scripts.thesis.final_validity_audit.human_review ingest --run artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z --key ../datasets/REASSEMBLE/cache/final_validity_audit/20260928T032231Z/private/source_label_key.csv --sheet PATH_TO_COMPLETED_A.csv --sheet PATH_TO_COMPLETED_B.csv
```

One real reviewer is accepted and reported as one; do not invent the second. New immutable submissions/analysis are saved in timestamped subdirectories. This does not overwrite the audit snapshot, relabel the cohort, recompute model performance or automatically approve correction. Annotation/boundary disagreements trigger an adjudication request. Automated work continues while human review remains pending.
