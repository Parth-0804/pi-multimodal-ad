# Candidate sample-definition options

Status: **no option selected**. These are research-design alternatives, not model samples.

| Sample unit | Input unit | Anchor-time requirement | Status |
|---|---|---|---|
| one image | single photograph | verified comparable image acquisition timestamp | BLOCKED_REQUIRES_RESEARCH_DECISION |
| one tooth inspection | all views of one tooth in one inspection | verified inspection or member acquisition timestamp | BLOCKED_REQUIRES_RESEARCH_DECISION |
| all images from an inspection | archive-level photograph inspection | verified inspection boundary and clock | BLOCKED_REQUIRES_RESEARCH_DECISION |
| one sensor recording | one high-frequency HDF5 recording | verified recording start/end timestamps | BLOCKED_REQUIRES_RESEARCH_DECISION |
| one low-frequency observation | one timestamped low-frequency HDF5 member | verified member timestamp | BLOCKED_REQUIRES_RESEARCH_DECISION |
| one condition-indicator observation | one profiled CI dataset at an evidenced time | verified dataset/member timestamp | BLOCKED_REQUIRES_RESEARCH_DECISION |
| historical window ending at an inspection | past-only sensor history plus an inspection anchor | verified comparable inspection and sensor clocks | BLOCKED_REQUIRES_RESEARCH_DECISION |
| historical window ending at a target time | past-only sensor/image history before a scalar observation | verified target and input clocks | BLOCKED_REQUIRES_RESEARCH_DECISION |

## Decision boundaries

- No `SampleRecord` or training manifest is created by this audit.
- Candidate scalar target name, physical meaning, unit, timestamp, and scope remain unresolved.
- Six-hour proximity is reported only when observed between adjacent verified timestamps; it is not interpreted as an input window or prediction horizon.
- Past-only alignment can be audited, but no interpolation, aggregation, or final sample choice is performed.
