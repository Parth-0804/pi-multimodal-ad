# Gate 0 — data access

PASS for local representative access, not for completeness.
Expected dataset: IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset.
Located at repository-relative `data/Full Dataset/`. Searched repository data
entries and workspace sibling directories; /mnt and /media contained no mounts.
Further searches/downloads were unnecessary once the copy was found.

Manifest is readable: 4,040 records, SHA256 `9c4fb4df70bb137fc851dd858ac22d53eed86ba08c3806d7177e40b300406826`.
Representative and subsequently all present audio/CSV/image files were readable;
video decode probes identified 16 failures. License file present: Intel Research
Use License Agreement. No authentication state was inspected or used; no network
payload download or acceptance of access terms occurred. The public dataset card
is accessible, while hosted payload access requires agreeing to conditions:
https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset

Blocker at Gate 0: none for local audit. Local completeness, video integrity,
physical grouping and holdout contamination are separate downstream blockers.
