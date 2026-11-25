# Reliable multimodal industrial monitoring: public-source scoping review

**NOT RESULTS-BLIND.** The coordinator has seen project outcomes. This report uses only public sources and does not describe, justify, or compare the project's architecture or results. It does not fulfill the original independent-review requirement. The later project comparison is a separate artifact. No public implementation was run.

Search: 19 October 2026 UTC, 20 October locally. This is purposive scoping through that date, with foundational and recent work, not an exhaustive or systematic review. The log contains 36 actual queries. There were 43 distinct explicitly opened URLs, counting failed fetches, below the session ceilings. Twenty studies were retained: 16 received targeted full-text inspection; HA4M, GIML, ConditionNET and RC-NF have restricted abstract/index/metadata coverage. Full-text inspection means selected methods, evaluations and limitations were read, not that every appendix or proof was independently verified. Bibliography, access depth, claim locations and screening decisions accompany this report.

## 1. Define the prediction before selecting fusion

Industrial monitoring contains several different problems. Completed-action classification observes an interval and predicts whether its outcome was successful. Online monitoring must make a decision using only information available at a declared time. Early detection adds a lead-time requirement. Anomaly detection may learn normal behavior without failure labels; supervised failure classification learns from labelled outcomes. Regression estimates a continuous physical quantity. These tasks require different targets, sampling windows, baselines and evaluation denominators. An architectural comparison cannot erase those distinctions.

A useful task contract states what is observed, when observation ends, what constitutes an event, and how the label was obtained. Using a full action interval can be reasonable for quality inspection. It cannot by itself establish that intervention was possible before a failure. Similarly, classifying which assembly action occurred does not establish whether it was completed correctly. Time-normalizing a completed interval may rely on a boundary that would be unavailable during execution. This is a design implication, rather than an allegation about any particular public implementation.

The public REASSEMBLE description illustrates the distinction: it contains hierarchical action and outcome annotations and separate demonstrations of segmentation, policies and execution monitoring. Its ConditionNET-style monitoring example derives phase labels from selected portions of annotated intervals. Those reported tasks cannot be treated as one common failure benchmark. [P11, sections IV–VI](https://arxiv.org/html/2502.05086v2).

IndustReal explicitly evaluates correct procedure completion, order and timeliness. Its reported delay excludes false positives and false negatives, so delay needs its accompanying recognition metrics. [P12, section 3](https://arxiv.org/html/2310.17323). ConditionNET is related execution-state work, but this review inspected only its abstract and publication identity; detailed split fairness remains unverified. [P19](https://arxiv.org/abs/2502.01167).

The general lesson is to select a task for scientific and operational relevance before choosing an attractive metric. A study that changes from outcome prediction to action recognition during external evaluation can still test software portability. It must describe that change and cannot claim unchanged predictive generalization.

## 2. More modalities do not guarantee a stronger learned system

Wang, Tran and Feiszli show that joint multimodal optimization can underperform a strong unimodal learner. Their explanation and Gradient-Blending method concern unequal overfitting/generalization behavior, beyond simply adding capacity. This is direct counter-evidence to assuming extra inputs automatically improve a trained predictor. [P01, sections 2–3](https://arxiv.org/pdf/1905.12681).

Peng and colleagues distinguish optimization imbalance from fully exploiting each branch. Their gradient modulation and enhancement experiments compare against unimodal, fusion and training-modulation controls. Importantly, they acknowledge remaining limitations in unimodal representations inside the joint model. [P02, sections 3–5](https://arxiv.org/pdf/2203.15332).

These studies support several competing explanations for weak fusion: one modality may carry little target information; a useful branch may be undertrained; the optimizer may favor another branch; the fusion rule may be too flexible for the data; or the assessment may be too small to resolve incremental utility. The explanations are not interchangeable. A visual encoder cannot recover a force transient that was never visible, while a better optimizer cannot create absent information.

Consequently, a fair comparison needs strong independently fitted unimodal systems and a simple static combination. Equal parameter counts alone do not establish fairness: a branch can receive different supervision, different calibration or a different tuning budget. Equal wall time alone can also disadvantage architectures with different convergence rates. Record both practical compute and the fitting/selection policy.

Audio is appropriate where acoustic events are physically meaningful and synchronized. Audio-video studies supply useful methodological counterexamples, but their empirical rankings do not transfer automatically to force, current or position signals. Adding audio solely to increase the number of modalities creates synchronization, licensing and missingness obligations without establishing task relevance.

A stronger research question is therefore conditional: when is there complementary evidence that a particular fusion rule can use reliably? A small or negative fusion benefit is informative if the protocol can distinguish redundancy from optimization failure. It should not trigger an unplanned search for an architecture that produces a positive story.

## 3. Adaptivity has a hypothesis, not an automatic guarantee

Quality-aware fusion has substantial prior work. Zhang and colleagues analyze ensemble-like binary late fusion under logistic loss. Their bound comparison depends on matched expected weights and suitable weight–branch-loss relationships; QMF uses uncertainty signals to pursue that behavior. A tighter upper bound does not prove lower realized error, higher AP, or robustness to arbitrary distribution shifts. [P03, theorems 1–2 and assumption 1](https://proceedings.mlr.press/v202/zhang23ar.html).

The theoretical distinction matters. The existence of a useful input-dependent weighting function does not show that a finite dataset can identify it. A measured gate might respond strongly to corruption while choosing the wrong branch. A quality estimator could learn task identity or class prevalence rather than reliability. Predictive confidence may remain high on a faulty input. These are testable failure mechanisms, not reasons to reject adaptivity in advance.

Willibald, Sliwowski and Lee provide especially close robot-domain prior work: a force/pose GMR expert and a vision-language monitoring expert are combined by choosing the higher-confidence expert. The studies report task-dependent monitoring benefits, using frame and delay outcomes; this is different from completed-action AP and a matched constant soft mixer. [P18, III–IV](https://arxiv.org/html/2506.19077).

A defensible hypothesis would specify how the proposed quality information predicts a branch becoming unreliable and how that signal reaches the final decision. The control should retain the same branch predictions, output transformation, availability behavior and calibration capacity, changing only whether mixing varies across inputs. Competitive practical baselines remain necessary even when they are not exact mechanistic controls.

It is helpful to separate two claims. The mechanism claim is that weights respond to meaningful changes in reliability. The outcome claim is that the response improves predictions relative to appropriate controls. Neither claim entails the other. Gate values are parameters of a model, not percentages of causal contribution. Corruption sensitivity is an intervention on an input pipeline; its interpretation depends on the fault and the information destroyed.

## 4. Missingness, degradation and uncertainty need separate protocols

ModDrop established training with dropped modalities for recognition and missing-channel resilience well before current attention-based fusion. [P07, modality-drop training and missing-signal experiments](https://arxiv.org/pdf/1501.00102). Ma and colleagues find that transformer fusion strategies behave differently under missing modalities across image-text datasets. Their work directly contradicts a universal missing-input advantage from a transformer architecture name. [P05, sections 3–5](https://arxiv.org/pdf/2204.05454).

Known absence provides an explicit availability signal. Hidden degradation presents a seemingly valid stream that may be misleading. A quality-aware system that falls back correctly when told a sensor is absent has passed an availability test; it has not necessarily learned to recognize a silent fault. Randomly dropping channels, dropping whole modalities and introducing a contiguous temporal outage also preserve different information.

Recent work continues to distinguish these cases. Liao and colleagues evaluate entire-missing, random-missing and noisy modalities in semantic segmentation. Their aggregation considers different assumptions about failure occurrence. The experiments use simulated DELIVER data, so they do not by themselves establish physical industrial fault realism. [P15, section 3](https://arxiv.org/html/2503.18445). The July 2026 GIML preprint describes combined degradation/missingness and learned quality estimation, but only its abstract was inspected; its claimed generality is not adopted here. [P17](https://arxiv.org/abs/2607.06943).

For a prospective industrial protocol, list fault families and physical insertion points before evaluation. Describe whether noise is added before resampling, image processing, feature extraction or fusion. Report units, clipping, saturation, affected channels, duration and whether the intervention preserves the target meaning. White Gaussian noise is a useful controlled perturbation; it is not automatically a model of a loose connector, obscured camera or delayed clock.

Corrupt one modality at a time while holding sample identity fixed. Keep known absence separate from undetected failure, and specify behavior when neither modality is usable. Both-input failures may later matter, but they need a distinct justified question. Avoid silently assuming independent faults when illumination, vibration or power failures could affect several streams together.

Training with corruptions changes the learning problem and the information available to the model. A clean-trained assessment and an augmentation-trained comparison answer different questions. Exposure must be matched when isolating a fusion mechanism. Published augmentation methodology is background evidence, not permission to revive an excluded experiment or to change a protocol after inspecting outcomes.

## 5. Encoders: weights, observation and temporal support are distinct

Freezing an encoder fixes its learned transformation. Frame selection, view choice, crop, spatial pooling and observation length determine what information reaches that transformation. Unfreezing weights does not recover unsampled frames or an occluded view. Conversely, increasing temporal coverage can improve information access without changing any pretrained weight. A study that changes both cannot attribute its effect to fine-tuning alone.

Kumar and colleagues provide formal results in an overparameterized linear setting and empirical ID/OOD transfer comparisons. Their work shows circumstances where fine-tuning distorts useful features, and motivates probing before fine-tuning. These findings oppose a blanket fine-tuning preference; they are not a prediction about every industrial pretrained backbone. [P06, sections 3–4](https://arxiv.org/pdf/2202.10054).

An encoder experiment should therefore compare clearly specified frozen, partially trainable and fully trainable paths under shared observation support. Keep initialization and head capacity explicit. Trainable-layer lists, normalization statistics, optimization groups and fitting partitions matter more than a single “frozen” boolean. Parameter reporting should distinguish all loaded weights, forward-active weights, trainable weights and fitted fusion parameters.

RT-DETR illustrates a different architectural distinction: its detector combines backbone features, a hybrid spatial encoder and a query decoder. A detector checkpoint's origin does not establish which component another application calls. Its COCO detection AP is not binary industrial outcome AP. [P09, section 3](https://arxiv.org/pdf/2304.08069).

Temporal attention is a separate hypothesis about order and cross-frame interactions. TimeSformer compares spatial and spatiotemporal variants, with dataset-dependent behavior and differing capacity. [P08, sections 3–4](https://proceedings.mlr.press/v139/bertasius21a/bertasius21a.pdf). Useful controls include a shared per-frame projection with mean pooling, a temporal model without positional encoding, and a predefined order diagnostic. More parameters or a position token alone do not prove useful temporal reasoning.

If only frozen feature banks are available, fitting a different head tests downstream representation use. It cannot establish a backbone fine-tuning comparison. If a learned feature bank was fitted using assessment groups, later fitting a clean fusion head does not repair the leakage. All learned encoders, quality preprocessing and calibration must respect the declared independent partitions.

## 6. Evaluation should make unfavorable conclusions possible

MultiBench evaluates performance, complexity and imperfect-modality robustness across heterogeneous tasks. It distinguishes absolute corrupted performance from robustness relative to clean performance, and shows that these perspectives can disagree. This is a stronger methodological foundation than claiming robustness from one small degradation. [P04, sections 3–4 and figure 4](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/37693cfc748049e45d87b8c7d8b9aacd-Paper-round1.pdf).

A model with weak clean performance can have little left to lose. Report clean and corrupted scores alongside paired changes, then compare models on the same items and faults. Do not average away a failure on one physically important condition. If severities are aggregated, state their weights and whether those weights reflect deployment occurrence or simply a descriptive benchmark convention.

Ranking and decision quality are different. For binary failure classification, specify the positive class, AP convention, prevalence and pooling across folds. A pooled out-of-fold ranking need not equal the mean of fold rankings. AUPRC is an ambiguous label unless its calculation is defined. Recall at a saved threshold, false alarms, Brier score and a declared calibration assessment answer additional questions; they should not be substituted after seeing the primary result.

Guo and colleagues demonstrate that classification confidence can be poorly calibrated and that simple post-hoc calibration can help in studied settings. Their temperature is selected on validation data, not assessment labels. That empirical result does not guarantee calibration under new faults. [P10, sections 4–5](https://proceedings.mlr.press/v70/guo17a.html).

Repeated frames and windows do not necessarily provide independent evidence. The relevant independent unit may be a recording, person, physical bearing, manufacturing batch or robot site. Split that unit before fitting and examine higher-level shared conditions. A recording-level split still needs a limitation if recordings share objects, operators or collection sessions. Large row counts cannot resolve a small number of independent groups.

A future uncertainty protocol should distinguish variation in assessment groups, training initialization and corruption realization. Resampling fixed predictions estimates a conditional quantity; it does not reproduce training variability. Prespecify pairing, the primary contrast, multiplicity treatment and practically meaningful margins. A nonsignificant difference is not equivalence. A validity failure blocks interpretation; it is neither a positive nor a negative scientific finding.

Finally, preserve selection history. Repeatedly consulted outcomes can guide exploratory design but cannot become untouched confirmation. There is no statistical reset from renaming a run, changing a report date or describing a later comparison as “final.” Independent assessment needs genuinely unused information or an explicitly limited exploratory interpretation.

## 7. External datasets: feasibility precedes architecture transfer

The shortlist accompanies this review and is not a dataset approval. IndustReal is the first feasibility candidate because its native completion/error semantics and participant partitions are documented. Its numerical tracks come from the visual platform, so independence from camera failures must not be assumed. Official code is available, while the separate data landing returned 403. Dataset-specific release terms still require verification. [P12/original project](https://github.com/timschoonbeek/industreal).

InspecSafe-V1 is a conditional second candidate from 2026: it combines inspection labels and heterogeneous available streams. Its current benchmark uses RGB VLMs, and point-linked sensor records do not establish independent, fully aligned windows for every annotated keyframe. Supplied sampling does not by itself demonstrate group-disjoint assessment. The official card states CC-BY 4.0; its data licence must be distinguished from the article licence. [P16](https://www.nature.com/articles/s41597-026-07796-x), [official card](https://huggingface.co/datasets/Tetrabot2026/InspecSafe-V1/blob/main/README.md).

HA4M offers camera-derived action modalities, not verified success labels or independent force sensing; full-text access was blocked in this session. [P13](https://pmc.ncbi.nlm.nih.gov/articles/PMC9718853/). AURSAD offers native screwdriving anomalies and synchronized numeric sensing, but a paired visual stream was not established; report and record sample counts differ. [P14](https://zenodo.org/records/4487073). Paderborn provides current/vibration condition monitoring under an official noncommercial licence, without an action-camera task. [Official KAt documentation](https://mb.uni-paderborn.de/en/kat/research/bearing-datacenter/data-sets-and-download).

These alternatives illustrate a constraint: a dataset may support generic fusion software while failing the intended visual–sensor outcome question. Never invent health labels from run identity or images from numeric signals to force compatibility. Camera-derived skeletons also need a declared role rather than being treated as a mechanically independent sensor.

Retraining a method on dataset B tests a dataset-specific learning recipe. Applying unchanged weights tests a transfer claim. Running the same interfaces measures portability. Reconstructing saved metrics checks arithmetic. Reproducing inference or training needs additional executions and tolerances. Each claim requires its own evidence and cannot be inferred from the others.

For portability, measure adapter effort, changed shared-core lines, domain-specific dependencies, schema assumptions, unit handling and failure behavior. Record versions, split identities, target mappings, commands and artifacts. A successful second dataset is a bounded example, not proof of universal compatibility. Published scores require matching task and evaluation protocols before numerical comparison.

## 8. Recent alternatives and feasible unanswered questions

RC-NF is a 2026 normal-only robot-monitoring alternative. Only primary abstract/metadata were accessible here, so its detailed baselines, splits and latency claims remain unchecked. It prevents a simplistic framing in which robot monitoring developments consist only of adding supervised attention. [P20, CVPR identity](https://openaccess.thecvf.com/content/CVPR2026/html/Zhou_RC-NF_Robot-Conditioned_Normalizing_Flow_for_Real-Time_Anomaly_Detection_in_Robotic_CVPR_2026_paper.html).

Three questions remain reasonable proposals, not demonstrated novelty. First, does a reliability signal improve decisions over a matched constant rule when representations, calibration and training exposure are fixed? Closest work includes QMF and robot MoE monitoring. A null would be no reliable gain, or harmful misweighting on rare but informative events.

Second, does changing trainable encoder depth improve robustness at a fixed observation window, or merely clean fitting? Closest work includes the transfer-learning analysis and spatial/temporal architecture studies. The smallest fair study changes one boundary, includes a frozen reference, and reports clean as well as degraded outcomes. A null could favor frozen representations once cost and uncertainty are considered.

Third, can a locked fusion interface support a second native task without changing the shared learning logic? MultiBench and the dataset descriptors establish substantial prior tooling and evaluation practice. A useful contribution could be a transparent failure of portability, identifying the particular timing, target or synchronization assumption that breaks.

None of these questions is new merely because this search did not locate an identical study. The reviewed evidence supports a disciplined comparison agenda and exposes strong prior overlap. It does not promise a new theorem, establish implementation validity, certify public benchmark results or select an approved experiment.

## 9. Review limitations and freeze boundary

This review is outcome-exposed, search-engine dependent and English-language dominated. Recent2025–2026 coverage is selective; inaccessible full texts and sources discovered late may change priority. The twenty rows mix method papers, benchmarks and descriptors intentionally, with access depth visible. No automatic bibliography count substitutes for methodological completeness. There is no human or independent reviewer certification.

Input: neutral public question and declared search/screening rules. Operations: bounded primary-source discovery, targeted reading and contradiction checks. Output: synthesis, paper matrix, dataset shortlist and verified identities. Evaluation: explicit task boundaries, access limitations and primary section references. Conclusion: matched controls, honest target timing and strong branches are prerequisites to interpreting reliability improvements. Uncertainty: which hypotheses will survive a particular dataset remains empirical and unresolved.

The literature packet is frozen and hashed before the separate outcome-aware project comparison. Its original independent-review requirement remains open. The freeze is an integrity checkpoint for these documents, not proof of results blindness or experimental approval.
