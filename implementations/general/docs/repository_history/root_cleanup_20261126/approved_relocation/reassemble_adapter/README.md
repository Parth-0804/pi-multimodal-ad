# REASSEMBLE relocation compatibility and preservation gate

The approved relocation preserves the two historical study trees byte for byte
while changing their storage locations. The additive adapter is
`implementations/REASSEMBLE/src/reassemble/relocation.py`; its reviewed prefixes
and explicit import scopes are in
`implementations/REASSEMBLE/configs/relocation_paths.json`. No frozen scientific
source, configuration, stop record or identity manifest is amended by the adapter.

The [pre-move gate](PRE_MOVE_GATE.json) passes for location compatibility and a
bounded preservation baseline. It is **not a scientific replay or resume gate**.
[The baseline](BASELINE_SOURCE_HASHES.json) records 62 selected frozen source,
test, configuration, identity and stop files; all hashes matched a second read.
The [post-move validation](POST_MOVE_VALIDATION.json) confirms all 62 hashes match
at their canonical destinations, all 20 configured destination prefixes exist,
and physical paths and historical relative identities agree with every mapping.
The six synthetic tests pass after relocation as well. Raw data, caches, model
weights and Parquet payloads were not opened or hashed by this adapter check.

## Explicit activation

An authorized Python consumer must enter `reassemble_relocation(repo)` **before**
importing a preserved study module and keep the context active for that consumer's
operation. Importing the adapter or entering its context does not import or run a
study. The configured source directory can then be added to `sys.path` inside the
context for the specific, separately authorized consumer. Pre-imported scoped
modules are rejected. On exit the context restores its import search path and
removes modules it loaded; callers should discard references to those modules.

The generic `relocation_context(repo, mappings, scope_roots)` interface is also
used by the ViFailback location adapter. Only modules whose physical source files
are under the explicitly configured scopes receive location-aware `pathlib`,
`os.path.relpath`, and explicit-source-loader imports. Original Python bytes are
compiled unchanged. No global `pathlib`, `os`, or `importlib` function is patched.

The path object retains historical components for fixed-depth parent discovery.
Its absolute `str()`/`os.fspath()` resolves current storage; `str(relative_to(REPO))`
and scoped `os.path.relpath(..., REPO)` retain historical evidence keys. Opening
an old configured path therefore accesses the canonical file while the original
hash comparison still compares its bytes against the original identity. More
specific prefixes preserve files already moved in earlier consolidation phases.

## Checked consumers and limits

| Preserved consumer | Location dependency covered |
| --- | --- |
| Bootstrap `source/common.py` | Fixed-depth repository discovery, configured paths, `check_originals()` file locations |
| Bootstrap `source/data.py` | Historical `os.path.relpath` identity keys and filesystem paths |
| Phase 1 `phase_common.py` / `phase_controller.py` | Original study depth, bootstrap source imports, relocated audit/report paths, original `relative_to(REPO)` source keys |
| C20 and 100-epoch `*_common.py` / `*_controller.py` | Original revision parents, Phase 1 imports and original source-key construction |
| CNN100 comparison `src/original_api.py` | Explicit `importlib.util.spec_from_file_location` loader for preserved source |
| GPU audit source reused by Phase 1 | Original audit prefix resolved to its earlier canonical location |

`study.sh` uses its historical shell-relative repository depth. Phase 1, C20 and
100-epoch controllers start fresh Python interpreters; multiprocessing spawn does
the same. **Their old CLI commands are not certified by this import adapter.**
Every fresh interpreter would need separately reviewed explicit activation before
any future authorized replay. The adapter provides no controller, subprocess
runner, automatic resumption, or stop override. External model-library behavior
and full scientific execution have not been tested in this maintenance task.

The original bootstrap `initial_state.json` has one **pre-existing** identity
mismatch: `AGENTS.md`. The first check incorrectly classified two policy-document
mismatches as pre-existing as well. Phase-preimage evidence shows that
`docs/data_boundaries.md` and `docs/output_policy.md` still matched the original
identities before this phase; their transient edits during this phase have now
been restored byte for byte. See the [dated correction and retained earlier
observations](IDENTITY_CLASSIFICATION_CORRECTION.json).

Eleven bounded source/configuration/assignment/policy entries now match, and two
Parquet entries were deliberately not read. See [the exact
comparison](EXISTING_IDENTITY_LIMITS.json). The remaining AGENTS mismatch still
fails the original check; the adapter neither refreshes the manifest nor declares
the stopped study resumable. The 62-file post-move preservation check is unchanged.

## Validation

[Six synthetic tests](SYNTHETIC_TESTS.txt) passed using temporary invented files:
fixed-depth discovery and physical I/O; unchanged historical identity keys;
original hash checks accepting unchanged bytes and rejecting a deliberate test
mutation; package and explicit-file imports; retained stop records and no implicit
execution; invalid mapping and pre-import rejection. Standard-library functions
remain unchanged outside the scoped imports. No real study or model module was
imported. The command and adapter/configuration hashes are in
[SYNTHETIC_VALIDATION.json](SYNTHETIC_VALIDATION.json).
