# Blinded researcher review protocol

Open `galleries/blinded_pilot_v1/index.html` first. The deterministic seed20261028 randomizes ten examples as B001–B010. Initial HTML contains no outcome/source-collection identity key. Four native camera names, full/context16-frame sequences, neutral motion clips and numerical position plots are available for each example. The manipulated object is the16mm cylinder; the intended target is its assembly-task-board fixture. A reviewer must identify the exact physical target and any occlusion; there is no invented object box or frame-level anomaly annotation.

Complete RESEARCHER_VISUAL_REVIEW_SHEET.csv (40 example/view rows) with reviewer/date, observed phase/event, visibility confidence, event-time estimate, occlusion and ambiguity. Keep failure visibility separate from nominal timestamp validity. Do not infer collision force, submillimetre clearance or physical cause from unavailable measurements. Then open UNBLINDED_LABEL_KEY.html / UNBLINDING_KEY.json to compare with the native descriptions and known annotation limitations.

The review is label-blinded at the initial display, not a controlled diagnostic-accuracy experiment: diagnostic windows differ in duration and expert candidates lack phase matching. Source collections can also differ visually. Do not calculate a certified visibility rate or classifier accuracy from these examples. Raw videos can contain laboratory context; no human identity is inferred. Human review cells remain blank.

Automated Codex observations in PRELIMINARY_AUTOMATED_OBSERVATIONS.md are separate, explicitly uncertified, and must not be copied into a supposedly independent human review. No model prediction exists in this task.
