# Explicit compatibility for relocated ViFailback source

The original and matched-study source, configuration, saved identities and stop
records retain their bytes. Their historical paths remain valid evidence names.
An explicit import context translates filesystem access to the consolidated
locations while keeping those logical names for fixed-depth root discovery and
source-identity dictionaries.

The context reuses the [shared relocation loader](../../REASSEMBLE/src/reassemble/relocation.py).
Only the enumerated ViFailback and reused frozen REASSEMBLE source namespaces
receive scoped `pathlib.Path` and `os.path.relpath` compatibility. Global Python
modules are unchanged. The context must be active **before** importing ViFailback
modules, and those modules must be used inside that context.

```python
import sys
sys.path.insert(0, "implementations/VIFAILBACK/relocation")
from adapter import vifailback_context

with vifailback_context() as locations:
    from matched_vifailback.common import code_identity
    saved_logical_identities = code_identity()
```

The example reads source identities only. Relocation does not authorize fitting,
inference, preprocessing, downloads, report replacement or restarting the closed
training queue. Original direct script invocations do not activate this context.
Any future authorized execution must explicitly adapt every participating Python
process; context state is not inherited by a fresh subprocess. No experimental
replay is claimed by these source-path checks.

From the repository root, the additive command-line interface supports only:

```bash
python3 -B implementations/VIFAILBACK/relocation/adapter.py identities
python3 -B implementations/VIFAILBACK/relocation/adapter.py resolve VIFAILBACK/configs/experiment.json
```

`identities` imports only the standard-library common/reference modules. It checks
the entire retained original implementation dictionary, reused REASSEMBLE source
dictionary, matched implementation freeze and matched protocol hash. It does not
read data, feature arrays or checkpoints. Missing, extra or changed sources fail
the comparison; receipts are never rewritten.

`resolve` prints the current location of a historical path without opening it.
The five required move prefixes are explicit in `adapter.py`, including the
independent-verification tree retained in the original configuration.
External `../datasets/...` dependencies retain their external location.

See the [relocation verification record](../../general/docs/repository_history/root_cleanup_20261126/approved_relocation/vifailback_adapter/)
for the inspected source consumers, synthetic test results and actual bounded
source-identity checks. These checks establish compatibility within their stated
scope, not model reproduction or permission to resume unfinished work.
