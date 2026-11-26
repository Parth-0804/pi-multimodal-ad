# Preliminary blinded visibility inspection

This is an assistant inspection of five label-blind previews, not a second-human
signoff or an outcome-label review. Each preview shows four of the sixteen fixed
timestamps from all three cameras. Selection spans five task groups among the
currently completed technical checks; it does not cover all99 tasks. No outcome
judgments were produced, and the original20-example review remains locked.

Images: `VIFAILBACK/08_visual_examples_and_eda/real_examples/generated/20261029T004900Z/PRELIMINARY_BLINDED_VISIBILITY_CHECKS/`.

| Blinded ID | Visible content | Visibility limitation |
|---|---|---|
| B0799a965 | Board, elongated food object, knife and moving gripper in high view; close knife/board wrist views | Wrist framing changes substantially during motion |
| B1b09f4d5 | Cup and marker with gripper approaching in high view | Left wrist mainly sees the table; right wrist has close, partly cropped views |
| B08c16c1a | Box/lid, marker and gripper in high view | Wrist cameras partly lose the object or see a close box edge/gripper |
| B0d4e6daf | Bowl, cabinet/drawer area and gripper in high view | Wrist views intermittently show large surfaces rather than the active interaction |
| B0086210b | Cup containing objects and approaching gripper in high view | Left wrist is largely uninformative; right wrist framing becomes close and changes context |

The high view captures relevant manipulation context in these five previews.
Technically valid wrist streams can still be weak or self-occluded. Equal camera
averaging therefore does not guarantee an informative representation. No visible
human appears in these sparse frames; that does not establish absence throughout
an episode or the dataset. No prediction about native failure status follows
from this inspection.

Full-cohort contact sheets are generated separately after complete technical QC.
Semantic visibility and incidental human presence remain unresolved for unreviewed
episodes. Weak views remain in the primary technical cohort and stress analysis;
they are not removed using class labels or classifier correctness.
