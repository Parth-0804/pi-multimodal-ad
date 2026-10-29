# Preserved status-journal formatting

The frozen report formatter emits one trailing space on the status line when
there is no error message. This is cosmetic and affects neither input data,
models, numerical results nor content hashes. It was detected during the
documentation commit check; the shell continued to the commit after that
check failed. No scientific check failed.

The domain-owned `.gitattributes` disables only `blank-at-eol` for the live
completion-status journal and its archived copies. This preserves already
published evidence byte-for-byte and lets later scoped evidence commits use
the normal `git diff --check` gate. Other documentation and all code retain
normal whitespace checking. No global Git configuration was changed.

The formatter itself is intentionally left unchanged while the experiment's
code fingerprint is frozen. A later source revision can remove the cosmetic
space without rewriting earlier snapshots.
