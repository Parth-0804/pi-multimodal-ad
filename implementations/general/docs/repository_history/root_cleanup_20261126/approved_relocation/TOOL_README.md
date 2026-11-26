# Approved relocation engine

`RELOCATE.py prepare` performs metadata inspection and writes a new, immutable
`preflight_<UTC>/` directory. It does not move project material. Source payloads
are never opened, hashed, copied or decoded. The only content read for publication
coverage is `.gitignore` policy text and this phase's approval/gate/plan records.
The policy-only shadow contains no source data.

The exact eleven prefixes are bound to `APPROVAL.json`. Individual collision
exceptions preserve the original VIFAILBACK README and two original ignore files;
independent files are never overwritten. VIFAILBACK moves before its separate
verification package. `nonfrozen` selects Handover raw, REBOOT raw/runs, legacy
milling, cross-dataset native examples, discovery sources and historical PHM EDA.
The VIFAILBACK, feedback and bootstrap groups require separate passing adapter
gates; independent VIF verification cannot pass through an unreplaced proxy.

## Preparing and applying

Run from the repository root, using the existing Python executable:

```bash
python3 -B implementations/general/docs/repository_history/root_cleanup_20261126/approved_relocation/RELOCATE.py prepare --groups nonfrozen
```

For the complete set, use `--groups all`. Explicit comma-separated group IDs also
work; exact IDs appear in `PLAN.json`. After any source or ignore-policy change,
prepare a new snapshot. Older snapshots remain evidence and must not be edited.

The coordinator supplies an execution gate with this schema (the template is not
permission or a passing gate):

```json
{
  "preflight": "repository-relative path to the selected preflight directory",
  "groups": ["exact group IDs from its PLAN.json"],
  "checked_utc": "fresh timezone-aware ISO-8601 process-check time",
  "process_gate_passed": true,
  "scientific_jobs_will_not_be_resumed": true,
  "adapter_gates": {
    "vifailback": "repository-relative independently validated adapter report",
    "feedback": "repository-relative independently validated adapter report",
    "bootstrap": "repository-relative independently validated adapter report"
  }
}
```

The `adapter_gates` entries are needed only for selected frozen groups. Each
referenced report must contain `status: "PASS"`, `frozen_source_unchanged: true`,
`no_resume: true`, and a `groups` array including the corresponding group ID.
The engine also checks the recorded empty GPU gate. The process gate expires
after 30 minutes; a fresh gate remains the coordinator's responsibility.

```bash
python3 -B implementations/general/docs/repository_history/root_cleanup_20261126/approved_relocation/RELOCATE.py apply --preflight <repository-relative-preflight> --gate <repository-relative-execution-gate>
```

Do not apply a preflight with conflicts, ignored-to-exposed files, stale source
metadata or changed ignore policies. Every move is a same-filesystem `os.rename`.
Each affected node is checked immediately before and after its rename. All regular
files are checked again at completion by device, inode, size, mode and nanosecond
mtime. Directory merge containers may disappear only after live empty checks.
The action journal records durable intent and completion; no fit is resumed.

The fresh symbolic-link plan records target identities. It covers verified
browsing-proxy replacement, Handover's study link, eight bootstrap cache consumers,
VIFAILBACK's latest-results link, and the explicitly verified pre-existing MSM
raw-data link error. Unrelated broken links remain reported; no new broken link
is allowed. Directory identity checks do not constitute content hashing or
scientific replay.

## Recovery

`recover --preflight <path>` prints the reverse sequence without changing files.
`recover --preflight <path> --execute` reverses only completed journal actions,
checking each current identity and refusing occupied original paths. Every
restored regular file is checked again. Recovery itself has an append-only
journal. An unfinished INTENT, changed payload identity, occupied source path or
partly completed recovery requires inspection; the tool refuses blind retry.
It never overwrites an independent file or deletes a scientific payload.

## Synthetic validation

`SELFTEST.py` creates tiny synthetic-only repositories inside this phase. Tests
cover the eleven-group move/recovery round trip, merge/proxy/link behavior,
independent-destination conflict refusal, source drift refusal, ignore exposure
refusal and a differential proof that Git reads the alternate policy shadow.
No real source material is used. Initial fixture construction encountered an
already-created empty synthetic parent; that setup was corrected before the
passing tests. Its isolated attempt directory remains preserved.
