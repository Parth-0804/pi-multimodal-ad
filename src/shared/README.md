# Shared-code admission policy

This directory contains documentation only, not a shared implementation package. The import and call-site audit found no cross-domain production consumers of the old generic package: its contracts, archive helpers, normalizers, metrics and provenance utilities serve PHM and therefore live in `src/phm2026/`.

Admit implementation here only when actual consumers in at least two domains justify a stable domain-neutral contract. Add the corresponding shared tests and document both callers at that time. Do not create speculative acquisition, model or evaluation subdirectories.

There are currently no shared entry points, configs, tests, runs, artifacts or shared dependencies. Domain navigation: `src/phm2026/README.md`, `src/intel_welding/README.md`, and scientific REASSEMBLE under `src/reassemble/`. Repository maintenance is `scripts/ops/`; thesis audit/synthesis is `scripts/thesis/`.
