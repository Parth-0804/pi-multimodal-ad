# T2.1 checkpoint — image-derived target

Status: **PASS_PROVISIONAL_FOR_ENGINEERING_BASELINE**  
Target version: `phm2026_image_damage_v2`  
Run: `20260814T012054997053Z-e195f6d9`

## Decision

The official challenge page resolves the task semantics: participants derive their own scalar from 28 post-run tooth images. The problem is end-of-run current damage-state estimation. Six hours is the typical run/inspection/output cadence, not automatically a forecast horizon. Repository experiment/run/tooth identity is sufficient for post-run association; image UTC remains unverified.

The automated value is a **provisional pseudo-label**, not organizer ground truth or calibrated physical spall area. A normalized visible-flank band is illumination-normalized; elongated dark components become damage candidates. One image ratio is candidate pixels / ROI pixels. Multiple views aggregate to a tooth by maximum. The raw run target is the top-3 tooth mean; the causal monotonic alternative is the within-experiment cumulative maximum.

## Evidence

- 1,311/1,311 JPEGs decoded and source-hashed; 0 decode exclusions.
- 560 experiment/run/tooth records and 20 run targets; every run has 28 tooth identities.
- EXP-A/B replace canonical teeth 1–4 with ten close-ups; EXP-F has one canonical image/tooth. This protocol shift is a major limitation.
- V1 masks selected unrelated texture and were preserved as a failed attempt. V2 narrowed the physical band and horizontal component rule after bounded visual QA.
- 560 human reviews remain pending. Values may support an engineering baseline only; physical-damage claims remain prohibited.

Primary artifacts:

- `runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/tables/per_tooth_damage.parquet`
- `runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/tables/run_damage_targets.parquet`
- `runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/tables/human_review_queue.csv`
- `runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/reports/HUMAN_TARGET_REVIEW_GUIDE.md`

Gate: T2.2/R3 engineering work is allowed only with prominent provisional status. Scientific verification requires human mask/ROI review and protocol-bias assessment.
