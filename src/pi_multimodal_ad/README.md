# Legacy Python compatibility

Canonical scientific implementation lives only in `src/phm2026/`. These files forward the 53 original module/package paths from the migration manifest. Leaf modules alias the canonical module object, including private helpers and mutable module state; package facades preserve legacy child-module discovery and forward canonical exports.

New work should import `phm2026.*`. Old interfaces remain supported for external notebooks, historical serialized references and downstream callers. No automatic deletion is scheduled and no warning noise is added. Contract: `docs/repository_restructure/COMPATIBILITY_CONTRACT.md`; tests: `tests/compatibility/`.
