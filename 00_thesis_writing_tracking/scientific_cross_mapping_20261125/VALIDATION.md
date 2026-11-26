# Validation and review boundary

Checks performed on 25 November 2026; machine-readable receipt: [validation.json](validation.json).

| Check actually performed | Result and scope |
|---|---|
| Existing LaTeX-project preservation | All 56 baseline files retain their SHA256; no project files added. Includes source, bibliography, figures and existing PDFs. |
| F2 arithmetic audit | Passed target/fold/recording checks, available-artifact branch parity, coefficient consistency, F1/F2 formula reconstruction, independent AP formula and pairwise AUROC-difference checks. |
| Audit outputs | Fold CSV and JSON agree. Four positive AP fold differences; five positive AUROC fold differences. |
| Proposal navigation | Local Markdown destinations checked. The existing manuscript and report paths are retained as references. |
| Proposed LaTeX | Nineteen fenced LaTeX blocks checked for balanced braces/math delimiters; five used citation keys resolve against the existing bibliography plus the single proposed entry. These checks are not compilation. |
| Source identities | Thirty-eight linked source files hashed, in addition to the audit's prediction/configuration/source input manifest. No raw dataset or archive hashing. |
| Audit code | Python syntax parsed; the substantive audit itself ran successfully in the existing environment. |
| Repository checks | `git diff --check` passed; `git diff --stat` is empty because the proposal files are new/untracked. `git status --short --branch --untracked-files=all` was inspected. Pre-existing untracked thesis material remains present. |
| New-file whitespace | Checked separately because ordinary `git diff --check` does not cover untracked additions. |

The complete new prose was reviewed for claim scope, repeated caveats, location anchors and numerical consistency. Parallel reasoning reviews checked the F2 inference and chronology boundaries against supplied source excerpts; those agents did not independently retrieve artifacts. Their review is not external scientific validation.

The proposed revisions are **PROPOSED FOR RESEARCHER REVIEW**, not accepted manuscript changes. The existing revision pipeline is reused: this folder supplies concrete candidate passages and evidence, without changing its canon, state or workflow. No editable manuscript file changed, so its LaTeX-diff checker and document rebuild were not invoked. Integration and rendered-document review belong after acceptance of the proposed changes.

## Limits retained

- Historical bootstrap intervals and training are not newly reproduced. The new computation verifies saved REASSEMBLE predictions only.
- The original unimodal visual prediction file is unavailable at the inspected location; exact visual parity covers saved Section 1B and Section 2 artifacts.
- Live Zotero access was unavailable. Existing registers and targeted original papers were used; no full-library completeness, plagiarism or reference-certification claim is made.
- The 20-epoch REASSEMBLE handoff path named by manuscript E059 was not located. Its existing status description is attributed, not promoted to a new verified execution result. The proposed arguments rely on the directly inspected controlled comparisons.
- ViFailback's latest report contains a stale prospective inner2 sentence; the dated final receipt and coverage resolve the completion status. Its wider FULL20 matrix and corruption evaluations remain incomplete.
- `f2_verification/fold_metrics.csv` exists locally but is ignored by the repository's existing `*.csv` rule. The same results are also in `results.json`. Nothing was staged or committed, and no retention claim beyond these present local files is implied.

No training, model inference, raw-data preprocessing, environment alteration or experiment-process action occurred. The next manuscript action is review of [the 16 proposed revisions](PROPOSED_MANUSCRIPT_REVISIONS.md); this package does not apply them automatically.
