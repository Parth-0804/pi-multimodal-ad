# Independent human review — completed action clips

Please ask the thesis author (reviewer A) and preferably a second technically informed person (reviewer B) to review independently, without reading each other's answers. Use only this blind_review directory; do not consult the source/label key or model scores. The sheets contain the same64 cases in different orders. Action is supplied as task context; recorded outcome and predictions are hidden. No author/expertise credentials are implied by A/B identifiers.

For each in-segment silent clip fill every field:
- judged_outcome: success / failure / cannot_determine.
- boundary_quality: acceptable / questionable / cannot_determine.
- visibility: adequate / partial / insufficient.
- artifact_flag: none / possible / cannot_determine.
- short_reason: brief explanation, including uncertainty or evidence that a boundary is questionable.

Keep review_id unchanged. Use the supplied reviewer_id or replace it consistently with your own identifier. Do not force a success/failure when evidence is insufficient. Playback is a compact copy of the actual hand-camera frames inside the annotated scored interval. No audio, context extension, synthetic image, annotation overlay, predicted score or outcome label is added. A clip cannot establish everything that happened before/after its interval. Failure consequences visible inside the interval may be legitimate evidence for retrospective outcome classification.

Encoding may soften small details. The copy preserves every decoded in-segment frame; playback cadence is set from source timestamps to preserve the observed total duration. Uneven native frame intervals are displayed at their average cadence, so small local timing variations are a limitation. Do not infer exact event timing from the compact copy. Flag decoding/visibility problems; no difficult case has been deliberately replaced.

Blinding is limited: source content or prior familiarity may reveal context. This is a balanced, recording-spread qualitative audit, not a random estimate of population annotation error. Human agreement is not proof of physical ground truth. Do not inspect other reviewers' answers, relabel the model cohort, tune thresholds or remove disputed cases.

Return your completed CSV to the thesis author. The ingestion command listed in HUMAN_REVIEW_STATUS.md validates and preserves submitted bytes. The automated agent will never supply ratings or invent a second reviewer.
