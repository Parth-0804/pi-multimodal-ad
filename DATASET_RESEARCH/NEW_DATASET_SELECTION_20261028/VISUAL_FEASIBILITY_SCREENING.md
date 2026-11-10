# Initial visual-feasibility screen

Only RoboFAC and FAILURE were visually reviewed. CRIA was withdrawn and its downloaded previews were not examined.

This screen uses genuine source recordings and deterministic contact sheets, with no generated imagery, CNN features or learned predictions. Eight ordered source positions span each preview. Contact sheets are unblinded and are not evidence of independent human rater agreement. Uniform eight-frame previews can miss short events; native clips must be watched during the next review.

| Source example | Object and gripper | Relevant event | Assessment |
|---|---|---|---|
| RoboFAC real InsertCylinder episode 0, above camera | Cylinder, fixture and gripper visible | Failed grasp/no object transfer is visible in the sampled sequence | VISIBLE for this failure; full corpus UNKNOWN |
| RoboFAC real InsertCylinder episode 100, above camera | Lift and transfer visible | Placement/insertion visible; exact hole contact partly occluded | PARTIALLY VISIBLE for fine contact; task progress visible |
| RoboFAC simulated UprightStack trajectory UUID 24df13c8… | Robot and objects visible at a distance | Object displacement/fall visible late in sequence | PARTIALLY VISIBLE; simulator state cannot be called physical sensing |
| FAILURE author pour_s GIF | Gripper, source cup and receiving vessel visible | Material transfer and final placement visible | VISIBLE demonstration; original recording identity UNKNOWN |
| FAILURE author pour_f GIF | Gripper, vessels and spilled material visible | Material remains/spills outside intended vessel | VISIBLE demonstration; original recording identity UNKNOWN |

Artifacts:

- [RoboFAC simulation](visual_screening/RoboFAC_source_01.jpg)
- [RoboFAC real native No. answer](visual_screening/RoboFAC_source_02.jpg)
- [RoboFAC real native Yes. answer](visual_screening/RoboFAC_source_03.jpg)
- [FAILURE official successful pour](visual_screening/FAILURE_official_pour_s.jpg)
- [FAILURE official failed pour](visual_screening/FAILURE_official_pour_f.jpg)

Exact source filenames, frame counts and sampled indices are in `checks/source_preview_audit.json`; source hashes and pinned URLs are in provenance. The existing OpenCV decoder could read container properties but failed to decode AV1 pixels. The existing repository FFmpeg binary then decoded only the three selected RoboFAC clips on CPU, with hardware acceleration disabled and one decoder/filter thread. No environment packages were installed. ffprobe was unavailable on PATH, so reported preview timing is container frame count/fps rather than a full packet-timestamp audit.

The two FAILURE GIFs differ in vessel appearance and background. They are not matched comparison pairs and cannot validate visual learnability or episode labels. The next pilot must retrieve source RGB frames linked to native annotations and paired audio, retain the full camera view, and include contact-region crops only as supplementary views. A reviewer must see label-free chronological sequences before accessing the native key. Rate object/gripper visibility and actual failure observability separately. Record UNKNOWN if a failure cannot be judged, and keep exclusions independent of model performance.

RoboFAC's visible real failures do not repair its missing numerical modality. FAILURE's visible demos justify a corpus-linked visual pilot, not a completed multimodal cohort or a claim that audio adds value.
