# Human target review guide

Every value is a provisional pseudo-label, not organizer ground truth. Open the selected overlay using `selected_overlay_path`; the green rectangle is the fixed visible-flank candidate ROI and red pixels are the automated dark/textured candidate mask.

For every row in `tables/human_review_queue.csv`:

1. Set `review_status` to `reviewed` or `needs_second_review`.
2. Set `reviewer_decision` to `accept`, `reject`, or `correct`.
3. If corrected, enter a percentage in `corrected_damage_value` and explain the ROI/mask correction in `reviewer_notes`.
4. Record an ISO-8601 `review_timestamp` and reviewer identity in notes.
5. Reject glare, shadow, tooth-edge, framing, focus, or non-spall texture falsely selected as damage.

Do not promote this target version to scientifically verified until protocol differences (A/B close-ups versus F canonical views) and representative low/medium/high masks have been reviewed.
