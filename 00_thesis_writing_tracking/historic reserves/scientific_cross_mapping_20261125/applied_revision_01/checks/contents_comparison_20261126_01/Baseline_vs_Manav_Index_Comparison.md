# Baseline versus latest Manav extract: contents comparison

Verified against the compiled contents records and PDF destinations on 26 November 2026. Manuscript sources and PDFs were not changed.

Baseline: preserved `baseline/LaTeX_Project` edition, compiled as [baseline main.pdf](../baseline_build/main.pdf). Latest: [Manav_review_Abstract_Chapters_1-4.pdf](../../Manav_review_Abstract_Chapters_1-4.pdf), 126 pages, after the one-page abstract layout correction.

Page convention: baseline numbers are printed body pages (physical PDF page = body page + 11). Latest Manav numbers are both the printed and physical PDF pages. Its Abstract is page 1; Chapter 1 begins on page 2. Baseline front matter, contents, bibliography and later chapters are excluded from the chapter-length comparison.

## Exact chapter page ranges

| Chapter | Baseline pages | Count | Latest Manav pages | Count | Added pages |
| --- | --- | --- | --- | --- | --- |
| Abstract | i | 1 | 1 | 1 | +0 |
| 1 Introduction | 1–7 | 7 | 2–8 | 7 | +0 |
| 2 Critical Literature Review | 8–34 | 27 | 9–55 | 47 | +20 |
| 3 Technical Foundations | 35–47 | 13 | 56–87 | 32 | +19 |
| 4 Research Design and Methodology | 48–57 | 10 | 88–126 | 39 | +29 |
| Chapters 1–4 total | 1–57 | 57 | 2–126 | 125 | +68 |

The chapters grew from 57 to 125 pages (+68, approximately 119%). The latest extract is 126 pages including its one-page Abstract. Chapter 4 accounts for 29 of the added pages; Chapters 3 and 4 together account for 48 (71%).

## Main-section index and distribution of growth

Start pages are exact. The span columns count from a heading's starting page to the next numbered main section's starting page (or the next chapter). They show where pagination expands, not exact text occupancy: adjacent sections can share a page, and a span of zero does not mean an absent or empty section. Figures and tables that float across a heading boundary can also affect this attribution. The final Chapter 4 boundary is one past the extract's last page (127).

### Chapter 1

| Baseline section | Baseline start | Latest section | Manav start |
| --- | --- | --- | --- |
| 1.1 Industrial Monitoring and the Motivation for Multimodal Learning | 1 | 1.1 Context and Motivation | 2 |
| 1.2 Problem Statement | 2 | 1.2 Problem Statement and Research Gap | 3 |
| 1.3 / 1.4 Research Aim and Objectives / Main Research Question and Four Subquestions | 3 / 3 | 1.3 Research Questions and Objectives | 4 |
| 1.6 Contributions of the Thesis | 5 | 1.4 Methodology Overview and Contributions | 5 |
| 1.5 Scope and Evolution of the Research | 4 | 1.5 Scope and Delimitations | 6 |
| 1.7 Organization of the Thesis | 6 | 1.6 Structure of the Thesis | 8 |

### Chapter 2

| Section (latest wording) | Baseline start | Manav start | Boundary span B → M | Change |
| --- | --- | --- | --- | --- |
| 2.1 Review Scope and Search Methodology | 9 | 10 | 3 → 4 | +1 |
| 2.2 Industrial Monitoring Tasks and Supervision | 12 | 14 | 3 → 4 | +1 |
| 2.3 Multimodal Data in Industrial Applications | 15 | 18 | 2 → 4 | +2 |
| 2.4 Representation Learning for Industrial Monitoring — SQ1 | 17 | 22 | 4 → 5 | +1 |
| 2.5 Multimodal Fusion Strategies — SQ2 | 21 | 27 | 3 → 5 | +2 |
| 2.6 Reliability and Robustness — SQ3 | 24 | 32 | 3 → 5 | +2 |
| 2.7 Evaluation Beyond Accuracy — SQ4 | 27 | 37 | 3 → 4 | +1 |
| 2.8 Critical Synthesis and Research Gap | 30 | 41 | 5 → 15 | +10 |

### Chapter 3

| Section (latest wording) | Baseline start | Manav start | Boundary span B → M | Change |
| --- | --- | --- | --- | --- |
| 3.1 Common Mathematical Notation and Prediction Formulation | 35 | 57 | 1 → 1 | +0 |
| 3.2 Visual Representations | 36 | 58 | 2 → 6 | +4 |
| 3.3 Sensor and Time-Series Representations | 38 | 64 | 3 → 7 | +4 |
| 3.4 Prediction Models and Reference Baselines | 41 | 71 | 1 → 3 | +2 |
| 3.5 Fusion Mechanisms | 42 | 74 | 4 → 11 | +7 |
| 3.6 Component Selection Criteria and Implementation Mapping | 46 | 85 | 2 → 3 | +1 |

### Chapter 4

| Section (latest wording) | Baseline start | Manav start | Boundary span B → M | Change |
| --- | --- | --- | --- | --- |
| 4.1 Research Design and Relationship to the Research Questions | 48 | 88 | 1 → 5 | +4 |
| 4.2 Dataset Selection Criteria and Research Chronology | 49 | 93 | 2 → 2 | +0 |
| 4.3 Intel Welding Feasibility Assessment and Scope Evolution | 51 | 95 | 0 → 1 | +1 |
| 4.4 Dataset Admission and Preparation Checks | 51 | 96 | 1 → 2 | +1 |
| 4.5 Target Provenance, Prediction Units, and Available Inputs | 52 | 98 | 1 → 2 | +1 |
| 4.6 Grouped Assessment, Data Splits, and Leakage Prevention | 53 | 100 | 1 → 5 | +4 |
| 4.7 Model Fitting, Selection, Calibration, and Threshold Procedures | 54 | 105 | 1 → 4 | +3 |
| 4.8 Metrics and Uncertainty Estimation | 55 | 109 | 1 → 6 | +5 |
| 4.9 Robustness Evaluation Design | 56 | 115 | 0 → 5 | +5 |
| 4.10 Reproducibility and Experiment Provenance | 56 | 120 | 1 → 3 | +2 |
| 4.11 Computational Constraints and Exploratory Research Boundaries | 57 | 123 | 1 → 4 | +3 |

## Largest expanded blocks

| Section | Baseline start → next heading | Manav start → next heading | Added boundary span |
| --- | --- | --- | --- |
| 2.8 Critical Synthesis and Research Gap | 30 → 35 | 41 → 56 | +10 |
| 3.5 Fusion Mechanisms | 42 → 46 | 74 → 85 | +7 |
| 4.8 Metrics and Uncertainty Estimation | 55 → 56 | 109 → 115 | +5 |
| 4.9 Robustness Evaluation Design | 56 → 56 | 115 → 120 | +5 |
| 3.2 Visual Representations | 36 → 38 | 58 → 64 | +4 |
| 3.3 Sensor and Time-Series Representations | 38 → 41 | 64 → 71 | +4 |
| 4.1 Research Design and Relationship to the Research Questions | 48 → 49 | 88 → 93 | +4 |
| 4.6 Grouped Assessment, Data Splits, and Leakage Prevention | 53 → 54 | 100 → 105 | +4 |
| 4.7 Model Fitting, Selection, Calibration, and Threshold Procedures | 54 → 55 | 105 → 109 | +3 |
| 4.11 Computational Constraints and Exploratory Research Boundaries | 57 → 58 | 123 → 127 | +3 |

Chapter 2 §2.8 alone accounts for 10 of that chapter's 20 added boundary pages. Chapter 3 §3.5 accounts for 7 of its 19 added pages. One additional Chapter 3 page precedes §3.1. Chapter 4 keeps its 11 main sections but now has 30 numbered subsections, compared with none in the baseline.

## Complete side-by-side contents, including subsections

Chapter 1 is matched by topic because its numbering changed. Elsewhere, corresponding numbers are aligned; changed titles and newly numbered subsections are shown explicitly. A new subsection heading does not prove that all of its material was absent from the baseline.

### Chapter 1: full index

| Baseline entry | Page | Latest Manav entry | Page | Mapping note |
| --- | --- | --- | --- | --- |
| 1 Introduction | 1 | 1 Introduction | 2 |  |
| 1.1 Industrial Monitoring and the Motivation for Multimodal Learning | 1 | 1.1 Context and Motivation | 2 |  |
| 1.2 Problem Statement | 2 | 1.2 Problem Statement and Research Gap | 3 |  |
| 1.3 / 1.4 Research Aim and Objectives / Main Research Question and Four Subquestions | 3 / 3 | 1.3 Research Questions and Objectives | 4 | Combined former aim/objectives and research-question sections |
| 1.6 Contributions of the Thesis | 5 | 1.4 Methodology Overview and Contributions | 5 | Former contributions section; methodology overview added |
| 1.5 Scope and Evolution of the Research | 4 | 1.5 Scope and Delimitations | 6 |  |
| 1.7 Organization of the Thesis | 6 | 1.6 Structure of the Thesis | 8 |  |

### Chapter 2: full index

| Baseline entry | Page | Latest Manav entry | Page | Mapping note |
| --- | --- | --- | --- | --- |
| 2 Critical Literature Review | 8 | 2 Critical Literature Review | 9 |  |
| Multimodal Monitoring in Robotic Welding | 8 | Multimodal Learning in Industrial and Robotic Monitoring | 9 | Unnumbered opening subtitle renamed |
| 2.1 Review Scope and Search Methodology | 9 | 2.1 Review Scope and Search Methodology | 10 |  |
| 2.1.1 Research Themes and Search Questions | 9 | 2.1.1 Research Themes and Search Questions | 11 |  |
| 2.1.2 Sources, Search Terms, and Search Period | 10 | 2.1.2 Sources, Search Terms, and Search Period | 11 |  |
| 2.1.3 Inclusion and Exclusion Criteria | 10 | 2.1.3 Inclusion and Exclusion Criteria | 12 |  |
| 2.1.4 Evidence Extraction and Critical Appraisal | 11 | 2.1.4 Evidence Extraction and Critical Appraisal | 13 |  |
| 2.1.5 Limitations of the Review | 12 | 2.1.5 Limitations of the Review | 14 |  |
| 2.2 Industrial Monitoring Tasks and Supervision | 12 | 2.2 Industrial Monitoring Tasks and Supervision | 14 |  |
| 2.2.1 Anomaly Detection, Defect Classification, and Failure Classification | 12 | 2.2.1 Anomaly Detection, Defect Classification, and Failure Classification | 14 |  |
| 2.2.2 Condition Estimation and Regression | 13 | 2.2.2 Condition Estimation and Regression | 15 |  |
| 2.2.3 Dataset-Provided Labels, Derived Targets, and Proxy Supervision | 14 | 2.2.3 Dataset-Provided Labels, Derived Targets, and Proxy Supervision | 16 |  |
| 2.2.4 Retrospective Assessment and Online Monitoring | 14 | 2.2.4 Retrospective Assessment and Online Monitoring | 17 |  |
| 2.3 Multimodal Data in Industrial Applications | 15 | 2.3 Multimodal Data in Industrial Applications | 18 |  |
| 2.3.1 Visual and Video Observations | 15 | 2.3.1 Visual and Video Observations | 19 |  |
| 2.3.2 Sensor Time Series and Process Measurements | 16 | 2.3.2 Sensor Time Series and Process Measurements | 19 |  |
| 2.3.3 Audio Observations | 16 | 2.3.3 Audio Observations | 20 |  |
| 2.3.4 Synchronization, Correspondence, and Modality Availability | 17 | 2.3.4 Synchronisation, Correspondence, and Modality Availability | 21 |  |
| 2.4 Representation Learning for Industrial Monitoring — SQ1 | 17 | 2.4 Representation Learning for Industrial Monitoring — SQ1 | 22 |  |
| 2.4.1 Engineered Features and Conventional Machine Learning | 18 | 2.4.1 Engineered Features and Conventional Machine Learning | 22 |  |
| 2.4.2 Pretrained Visual Representations | 18 | 2.4.2 Pretrained Visual Representations | 23 |  |
| 2.4.3 Temporal and Time-Series Representations | 19 | 2.4.3 Temporal and Time-Series Representations | 24 |  |
| 2.4.4 Audio Representations | 19 | 2.4.4 Audio Representations | 25 |  |
| 2.4.5 Frozen Representations, Fine-Tuning, and Computational Constraints | 20 | 2.4.5 Frozen Representations, Fine-Tuning, and Computational Restrictions | 26 |  |
| 2.5 Multimodal Fusion Strategies — SQ2 | 21 | 2.5 Multimodal Fusion Strategies — SQ2 | 27 |  |
| 2.5.1 Unimodal References and Incremental Modality Value | 21 | 2.5.1 Unimodal References and Incremental Modality Value | 27 |  |
| 2.5.2 Feature Concatenation | 21 | 2.5.2 Feature Concatenation | 28 |  |
| 2.5.3 Prediction-Level and Late Fusion | 22 | 2.5.3 Prediction-Level and Late Fusion | 29 |  |
| 2.5.4 Gated and Context-Conditioned Fusion | 23 | 2.5.4 Gated and Context-Conditioned Fusion | 30 |  |
| 2.5.5 Comparability and Fairness of Fusion Evaluations | 23 | 2.5.5 Comparability and Fairness of Fusion Evaluations | 31 |  |
| 2.6 Reliability and Robustness — SQ3 | 24 | 2.6 Reliability and Robustness — SQ3 | 32 |  |
| 2.6.1 Missing Modalities | 24 | 2.6.1 Missing Modalities | 32 |  |
| 2.6.2 Noise and Partial Degradation | 25 | 2.6.2 Noise and Partial Degradation | 33 |  |
| 2.6.3 Temporal Misalignment and Distribution Shift | 25 | 2.6.3 Temporal Misalignment and Distribution Shift | 34 |  |
| 2.6.4 Quality-Aware and Uncertainty-Aware Fusion | 26 | 2.6.4 Quality-Aware and Uncertainty-Aware Fusion | 35 |  |
| 2.6.5 Modality Dropout, Augmentation, and Fallback Mechanisms | 26 | 2.6.5 Modality Dropout, Augmentation, and Fallback Mechanisms | 36 |  |
| 2.7 Evaluation Beyond Accuracy — SQ4 | 27 | 2.7 Evaluation Beyond Accuracy — SQ4 | 37 |  |
| 2.7.1 Grouped Evaluation and Leakage Prevention | 27 | 2.7.1 Grouped Evaluation and Leakage Prevention | 37 |  |
| 2.7.2 Discrimination, Calibration, and Decision Thresholds | 28 | 2.7.2 Discrimination, Calibration, and Decision Thresholds | 38 |  |
| 2.7.3 Uncertainty and Statistical Comparisons | 28 | 2.7.3 Uncertainty and Statistical Comparisons | 39 |  |
| 2.7.4 Interpretability and Its Limits | 29 | 2.7.4 Interpretability and Its Limits | 40 |  |
| 2.7.5 Modularity, Reproducibility, and Computational Cost | 30 | 2.7.5 Modularity, Reproducibility, and Computational Cost | 41 |  |
| 2.8 Critical Synthesis and Implications for This Thesis | 30 | 2.8 Critical Synthesis and Research Gap | 41 |  |
| 2.8.1 Findings Supported Across the Reviewed Studies | 30 | 2.8.1 Findings Supported Across the Reviewed Studies | 42 |  |
| 2.8.2 Conflicting Findings and Unresolved Questions | 31 | 2.8.2 Unresolved Questions and Research Gap | 43 | Same numbered slot, reframed scope; not a one-to-one paragraph correspondence |
| 2.8.3 Implications for Representation and Fusion Selection | 32 | 2.8.3 Derived Research Design Requirements | 46 | Same numbered slot, reframed scope; not a one-to-one paragraph correspondence |
| 2.8.4 Implications for Experimental Design | 32 | 2.8.4 Implications for the Empirical Investigations | 49 | Same numbered slot, reframed scope; not a one-to-one paragraph correspondence |

### Chapter 3: full index

| Baseline entry | Page | Latest Manav entry | Page | Mapping note |
| --- | --- | --- | --- | --- |
| 3 Technical Foundations and Candidate Models | 35 | 3 Technical Foundations and Possible Models | 56 |  |
| 3.1 Common Mathematical Notation and Prediction Formulation | 35 | 3.1 Common Mathematical Notation and Prediction Formulation | 57 |  |
| 3.2 Visual Representations | 36 | 3.2 Visual Representations | 58 |  |
| 3.2.1 Convolutional Feature Extraction and Spatial Pooling | 36 | 3.2.1 Convolutional Feature Extraction and Spatial Pooling | 59 |  |
| 3.2.2 RT-DETR Architecture and Component Roles | 36 | 3.2.2 RT-DETR Architecture and Component Roles | 60 |  |
| 3.2.3 Backbone Extraction Versus Hybrid-Encoder or Full-Detector Execution | 37 | 3.2.3 Backbone Extraction Versus Hybrid-Encoder or Full-Detector Execution | 61 |  |
| 3.2.4 Frame Sampling, Feature Aggregation, and Temporal Modelling | 37 | 3.2.4 Frame Sampling, Feature Aggregation, and Temporal Modelling | 62 |  |
| 3.2.5 Frozen Extraction and Visual Fine-Tuning | 38 | 3.2.5 Frozen Extraction and Visual Fine-Tuning | 63 |  |
| 3.3 Sensor and Time-Series Representations | 38 | 3.3 Sensor and Time-Series Representations | 64 |  |
| 3.3.1 Statistical and Signal-Derived Features | 38 | 3.3.1 Statistical and Signal-Derived Features | 65 |  |
| 3.3.2 PatchTST Architecture | 39 | 3.3.2 PatchTST Architecture | 66 |  |
| 3.3.3 Patching, Sequence Length, Padding, and Aggregation | 39 | 3.3.3 Patching, Sequence Length, Padding, and Aggregation | 67 |  |
| 3.3.4 Representation Learning Versus Direct Prediction | 40 | 3.3.4 Representation Learning Versus Direct Prediction | 70 |  |
| 3.4 Prediction Models and Reference Baselines | 41 | 3.4 Prediction Models and Reference Baselines | 71 |  |
| 3.4.1 Constant and Simple Reference Predictors | 41 | 3.4.1 Constant and Simple Reference Predictors | 71 |  |
| 3.4.2 Linear and Logistic Models | 41 | 3.4.2 Linear and Logistic Models | 72 |  |
| 3.4.3 Neural Classification and Regression Heads | 41 | 3.4.3 Neural Classification and Regression Heads | 73 |  |
| 3.4.4 Other Models Relevant to Retained Experiments | 42 | 3.4.4 Other Models Relevant to Retained Experiments | 74 |  |
| 3.5 Fusion Mechanisms | 42 | 3.5 Fusion Mechanisms | 74 |  |
| 3.5.1 Feature Concatenation | 42 | 3.5.1 Feature Concatenation | 75 |  |
| 3.5.2 Uniform Prediction Averaging | 42 | 3.5.2 Uniform Prediction Averaging | 76 |  |
| 3.5.3 Logistic Stacking | 43 | 3.5.3 Logistic Stacking | 77 |  |
| 3.5.4 Context-Conditioned Scalar Gating | 43 | 3.5.4 Context-Conditioned Scalar Gating | 78 |  |
| 3.5.5 Quality-Conditioned Interactions and Adaptive Extensions | 44 | 3.5.5 Quality-Conditioned Interactions and Adaptive Extensions | 80 |  |
| 3.5.6 Missing-Modality Routing and Fallback | 45 | 3.5.6 Missing-Modality Routing and Fallback | 81 |  |
| — | — | 3.5.7 Comparison of the Investigated Fusion Interfaces | 83 | New numbered subsection; not necessarily wholly new content |
| 3.6 Component Selection Criteria and Implementation Mapping | 46 | 3.6 Component Selection Criteria and Implementation Mapping | 85 |  |

### Chapter 4: full index

| Baseline entry | Page | Latest Manav entry | Page | Mapping note |
| --- | --- | --- | --- | --- |
| 4 Research Design and Shared Methodology | 48 | 4 Research Design and Shared Methodology | 88 |  |
| 4.1 Relationship Between the Research Questions and Case Studies | 48 | 4.1 Research Design and Relationship to the Research Questions | 88 | Broadened parent section; original title now appears at 4.1.1 |
| — | — | 4.1.1 Relationship Between the Research Questions and Case Studies | 89 | Original 4.1 heading moved to this subsection |
| — | — | 4.1.2 Methodological Implementation of the Research Design Requirements | 92 | New numbered subsection; not necessarily wholly new content |
| 4.2 Dataset Selection Criteria and Research Chronology | 49 | 4.2 Dataset Selection Criteria and Research Chronology | 93 |  |
| 4.3 Intel Welding Feasibility Assessment and Resulting Scope Decisions | 51 | 4.3 Intel Welding Feasibility Assessment and Scope Evolution | 95 |  |
| 4.4 Dataset Admission and Preparation Checks | 51 | 4.4 Dataset Admission and Preparation Checks | 96 |  |
| 4.5 Target Provenance, Prediction Units, and Available Inputs | 52 | 4.5 Target Provenance, Prediction Units, and Available Inputs | 98 |  |
| — | — | 4.5.1 Observation Windows and Prediction Horizons | 98 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.5.2 Contextual Information and Predictive Shortcuts | 99 | New numbered subsection; not necessarily wholly new content |
| 4.6 Grouping, Data Splits, and Leakage Prevention | 53 | 4.6 Grouped Assessment, Data Splits, and Leakage Prevention | 100 |  |
| — | — | 4.6.1 Training-Side Preprocessing and Model Selection | 101 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.6.2 Out-of-Fold Predictions and Learned Fusion | 101 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.6.3 Assessment Cohort Reconciliation | 103 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.6.4 Historical Preprocessing Dependencies | 104 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.6.5 Repeated Assessment Exposure | 104 | New numbered subsection; not necessarily wholly new content |
| 4.7 Model Fitting, Selection, Calibration, and Threshold Procedures | 54 | 4.7 Model Fitting, Selection, Calibration, and Threshold Procedures | 105 |  |
| — | — | 4.7.1 Model Fitting and Selection | 106 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.7.2 Probability Calibration | 106 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.7.3 Within-Fold Ranking and Pooled Prediction Scores | 107 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.7.4 Decision-Threshold Selection | 108 | New numbered subsection; not necessarily wholly new content |
| 4.8 Metrics and Uncertainty Estimation | 55 | 4.8 Metrics and Uncertainty Estimation | 109 |  |
| — | — | 4.8.1 Regression Metrics | 109 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.8.2 Classification Metrics | 110 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.8.3 Average Precision and Outcome Prevalence | 111 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.8.4 Metric Aggregation Across Folds and Seeds | 112 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.8.5 Probability Quality and Calibration | 113 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.8.6 Paired Model Comparisons and Uncertainty Estimation | 114 | New numbered subsection; not necessarily wholly new content |
| 4.9 Robustness Evaluation Design | 56 | 4.9 Robustness Evaluation Design | 115 |  |
| — | — | 4.9.1 Definition of Controlled Reliability Interventions | 116 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.9.2 Known Modality Absence and Fallback | 117 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.9.3 Degraded but Available Observations | 117 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.9.4 Training Exposure and Matched Comparisons | 118 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.9.5 Interpretation of Robustness Performance | 119 | New numbered subsection; not necessarily wholly new content |
| 4.10 Reproducibility and Experiment Provenance | 56 | 4.10 Reproducibility and Experiment Provenance | 120 |  |
| — | — | 4.10.1 Software and Implementation Environment | 120 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.10.2 Levels of Experimental Verification | 121 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.10.3 Source Versioning and Experimental Reporting Boundary | 122 | New numbered subsection; not necessarily wholly new content |
| 4.11 Computational Constraints and Exploratory Versus Confirmatory Analysis | 57 | 4.11 Computational Constraints and Exploratory Research Boundaries | 123 |  |
| — | — | 4.11.1 Computational Measurement Boundaries | 124 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.11.2 Exploratory Versus Confirmatory Interpretation | 125 | New numbered subsection; not necessarily wholly new content |
| — | — | 4.11.3 Methodological Synthesis | 125 | New numbered subsection; not necessarily wholly new content |

## Additional visible Chapter 2 subheadings

The latest PDF does not register these starred subheadings in the contents. The five study-specific headings had paragraph entries in the baseline contents. Page locations below were checked directly in the latest PDF text. Dashes mean there is no corresponding standalone baseline heading, not necessarily no related discussion.

| Heading (shortened for study names) | Baseline page | Manav page |
| --- | --- | --- |
| R1. Target validity and modality correspondence | — | 46 |
| R2. Representation suitability under explicit fitting conditions | — | 46 |
| R3. Incremental fusion value under comparable experimental conditions | — | 47 |
| R4. Reliability-aware comparison of fusion mechanisms | — | 47 |
| R5. Methodological validity and bounded cross-dataset interpretation | — | 48 |
| PHM gear monitoring | 32 | 50 |
| REASSEMBLE robotic assembly | 33 | 51 |
| MSM milling | 33 | 52 |
| ViFailback manipulation | 34 | 52 |
| HANDOVER human–robot interaction | 34 | 53 |

## Reading the result

The additional length is concentrated in expanded synthesis, model explanations and shared methodology. Chapter 1 has the same page count. Start-page shifts alone are not section growth: later sections inherit all expansion before them. Use the chapter totals and heading-boundary spans above to separate those effects.

This is a pagination and contents comparison, not a judgement that every added page should be removed. No thesis text, figures, layout or PDF was edited for this comparison.
