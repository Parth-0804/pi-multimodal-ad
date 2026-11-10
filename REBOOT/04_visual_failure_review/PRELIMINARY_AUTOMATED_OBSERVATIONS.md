# Preliminary automated visual observations — not human certification

These notes come from Codex inspection of actual source-derived16-frame contact sheets, not from an independent human reviewer, trained anomaly model or native ground-truth replacement. The human review sheet remains blank and no new frame labels are created.

| Example/view | Preliminary observation | Limitation |
|---|---|---|
| B003, right wrist | At sampled frame270 the cylinder is between the fingers; by284 it is outside the open gripper and subsequently lies on the wood before being reapproached. This is a visibly useful coarse release/drop candidate. | The native induction is frame300; the visible transition between270 and284 may precede it. This is a coarse observation to review, not a corrected event label. |
| B003, high / left wrist | Overhead shows global arm motion but the contact region is small; the left wrist mostly shows the other arm/background. | A timestamp-correct view can have weak physical-event visibility. |
| B008, right wrist | Cylinder and approaching fingers are visible; gripper/object offset changes during the candidate pickup window. | Misalignment cause and exact onset are not independently certified. |
| B002, right wrist | Approach/closure and a cylinder remaining near the tray are visible. | A specific collision/jamming or force explanation cannot be certified from these images. |
| B002, low | The task board is distant and much relevant gripper motion is at/outside the top of view. | This view is a poor default for fine engagement inspection in this example. |
| B006, right wrist | Cylinder, gripper and target board region are visible during the short placement window. | Submillimetre alignment and true contact/seating are visually ambiguous; no force/torque channel resolves them. |
| B001, right wrist | Whole expert-name episode shows approach, transport and placement context. | Repository membership and a sparse sequence do not independently certify every phase as normal or the terminal outcome. |

The right wrist is a promising view for coarse cylinder-release events; this is a development-pilot observation, not a universal view ranking or held-out model result. The overhead camera supplies scene context. All four views, including unhelpful ones, are retained. Do not select a best test camera after examining model scores. Further review should prioritize the clearly observable Transport drop and macro pickup errors; fine placement/force-dependent failures require stronger native labels and human checks.
