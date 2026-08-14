# PHM target candidates

Decision: **BLOCKED_REQUIRES_PROFESSOR_OR_PROVIDER_DECISION**

No candidate satisfies the target pass criteria. Condition indicators remain diagnostic candidates; they are not selected automatically.

| Candidate | Observed source evidence | Meaning/unit | Pairing | Decision |
|---|---:|---|---|---|
| FM4 | 744 representative rows | gear condition indicator; exact formula and target interpretation are not documented in authoritative local evidence / unknown | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| NA4 | 744 representative rows | gear condition indicator; exact formula and target interpretation are not documented in authoritative local evidence / unknown | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| M6A | 744 representative rows | gear condition indicator; exact formula and target interpretation are not documented in authoritative local evidence / unknown | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| ALR | 744 representative rows | gear condition indicator; exact formula and target interpretation are not documented in authoritative local evidence / unknown | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| Other CI family | 19353 representative rows | derived signal diagnostics including RMS, kurtosis, crest, FM0/M8A and related variants / mixed_or_unknown | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| PAU speed, torque and temperature | 1119 representative rows | operating conditions / RPM|ft-lbf|degF | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | REJECT_AS_PROXY |
| Vibration RMS / amplitude diagnostics | 2980 representative rows | vibration magnitude or derived signal statistic / g_or_unknown_by_path | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| DM4500 / ICM2 particle bins | 5936 representative rows | oil particle counts by instrument bin / number_of_particles | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| Quantitative tooth-damage measurement | 0 representative rows | physical surface-loss, spall or damage extent / unknown | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| Remaining useful life | 0 representative rows | time or cycles remaining to an authoritative failure criterion / unknown | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | UNRESOLVED_CANDIDATE |
| Experiment, run or lifecycle stage | 0 representative rows | administrative experiment/lifecycle identity / none | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | REJECT_AS_PROXY |
| Image brightness, blur, darkness or exposure | 0 representative rows | acquisition quality proxy / normalized_or_algorithm_specific | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | REJECT_AS_PROXY |

## Ranked scientific options requiring a decision

1. Obtain an authoritative quantitative tooth-damage measurement and image/inspection pairing key.
2. If a named condition indicator is intended, obtain its formula, unit, timestamp semantics, inference availability, six-hour rule, and image association from the professor/provider.
3. If RUL is intended, obtain the failure criterion and authoritative RUL construction.

Experiment/run/stage, operating context, and image-quality measures are explicitly rejected as convenient proxy targets.
