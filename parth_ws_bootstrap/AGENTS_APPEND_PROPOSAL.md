# Proposed persistent instruction addition — do not install during the audit

Codex discovers AGENTS.md files by directory scope. This file's name is deliberately
not AGENTS.md: extraction must not silently replace existing repository instructions.
The start prompt explicitly reads RESEARCH_RULES.md for the initial task.

After inspecting existing instructions and obtaining permission for an instruction
change, propose adding an appropriately scoped section to the actual root AGENTS.md:

> ## Parth WS research tasks
> Before substantive thesis work, read parth_ws_bootstrap/RESEARCH_RULES.md and the
> specific approved task/protocol. Do not assume a saved task queue grants authority.
> Inspect sources before project claims, distinguish evidence levels, preserve
> historical artifacts, and end with the evidence checkpoint. Do not run excluded
> historical Task 4. Missing approval or budget blocks experiments. Follow the
> appropriate task-specific limits, including audit-only scope where assigned.

Preserve all existing instructions and explain conflicts. Do not replace or blindly
append into a file you have not read. Check nested overrides and actual instruction
loading in a fresh task. Do not alter global user instructions, security settings,
or approval records to make the new text take precedence.

The exact relative path above assumes the pack retains its original folder name.
Update the proposed text to the observed path before presenting it for approval.
