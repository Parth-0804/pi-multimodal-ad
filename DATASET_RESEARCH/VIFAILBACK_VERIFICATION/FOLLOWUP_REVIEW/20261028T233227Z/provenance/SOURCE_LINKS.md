# Source provenance and interpretation boundaries

- [Pinned numerical/RGB conversion](https://huggingface.co/datasets/sii-rhos-ai/vifailback-dataset-lerobot/tree/619791b94f61667333fe179d471051e0bca0e06f): metadata, all5,202 actual Parquet SHA-256 identities and the full published camera inventory were audited.
- [Pinned original author release](https://huggingface.co/datasets/sii-rhos-ai/ViFailback-Dataset/tree/21df46c2585c52e5a62df5f4b946bae6cbc6fed7):109 native annotation files were rejoined and checked; original observation arrays were additionally checked through bounded HDF5 reads for three input-selected anomalies.
- [Original ViFailback paper,version3](https://arxiv.org/html/2512.02787v3): describes5,202 real-world trajectories and100 tasks in a failure diagnosis/correction and VQA study. It does not supply the new task-disjoint binary-outcome protocol proposed here.
- [Original pretrained RT-DETR-R18VD revision](https://huggingface.co/PekingU/rtdetr_r18vd/tree/ac77a11ff0170a41b771c03264987f8ce2b0d753): existing local checkpoint/config/processor hashes were verified; no model was downloaded or trained in this follow-up.

Full numerical acquisition receipts preserve public resolve URLs,revision,bytes
and expected/source hashes. Original HDF5 receipts preserve the exact byte ranges
and their hashes; publisher whole-file LFS hashes are distinguished from hashes
of locally retrieved fragments. No credentials,cookies or authentication state
were used or read. The web reader could not render the two pinned HF tree pages;
anonymous direct source resolution and file-hash validation succeeded.

The supplied independent review declares AI assistance. Its blinded provenance
is self-reported; this audit verifies its immutable text and comparisons,not
whether a human performed the review or every action of the external reviewer.
Original source-label consistency is distinct from independent mechanical
ground-truth validation. Cross-dataset exact/near-duplicate comparisons against
all REASSEMBLE raw videos were not performed. Dataset/publication identity alone
does not certify independence of operators,objects,sessions or backgrounds.
